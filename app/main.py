import os
import traceback
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# --- NUEVOS IMPORTS PARA EL FRONTEND ---
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# LangChain Essential Imports
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# 1. Configuración Inicial
load_dotenv()
app = FastAPI(
    title="Agente Futbolero AI",
    description="API que responde sobre fútbol chileno usando SQL y RAG con Fallback",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURACIÓN DEL FRONTEND (AGREGADO) ---
# Obtenemos la ruta de la carpeta donde está este archivo main.py (carpeta 'app')
current_dir = os.path.dirname(os.path.abspath(__file__))
# Definimos la ruta de la carpeta 'frontend' que está dentro de 'app'
frontend_path = os.path.join(current_dir, "frontend")

# Montamos la carpeta para que sea accesible desde /static
app.mount("/static", StaticFiles(directory=frontend_path), name="static")


# --- 2. Cargar Modelos (LLM y Embeddings) con Fallback ---
llm = None
embeddings = None
quota_error = False

def load_models():
    global llm, embeddings, quota_error
    
    # Intentar OpenAI
    try:
        print("🔍 Probando OpenAI (GPT-3.5 + Embeddings)...")
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        o_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, max_retries=1)
        o_embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        o_llm.invoke("ping")
        llm = o_llm
        embeddings = o_embeddings
        print("✅ OpenAI activo (Plan A)")
        return
    except Exception as e:
        print(f"⚠️ OpenAI falló: {e}")

    # Intentar Gemini
    try:
        print("🔍 Probando Gemini (Plan B)...")
        from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
        g_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        g_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        g_llm.invoke("ping")
        llm = g_llm
        embeddings = g_embeddings
        print("✅ Gemini activo (Plan B)")
        return
    except Exception as e2:
        print(f"⚠️ Gemini falló: {e2}")

    print("❌ ERROR: Todos los proveedores de LLM han fallado o agotado su cuota.")
    quota_error = True

load_models()

# --- 3. Recursos de Datos ---
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, "data", "campeonato_nacional_2025.db")
db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

if llm:
    # Agente SQL
    sql_agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools" if "ChatOpenAI" in str(type(llm)) else "zero-shot-react-description",
        verbose=True,
        handle_parsing_errors=True
    )
    
    # Descubrir Embeddings Disponibles
    REDIS_URL = f"redis://:{os.getenv('REDIS_PASSWORD')}@{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}"
    BASE_INDEX_NAME = os.getenv("REDIS_INDEX", "agente_futbol")
    embeddings = None
    final_index_name = BASE_INDEX_NAME
    
    try:
        print("🔍 Probando OpenAI Embeddings...")
        from langchain_openai import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        embeddings.embed_query("test") 
        final_index_name += "_openai"
    except:
        try:
            print("🔍 Probando Gemini Embeddings...")
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
            embeddings.embed_query("test")
            final_index_name += "_gemini"
        except:
            print("❌ ERROR: No se pudieron cargar embeddings de nube.")
            embeddings = None

    # Prompts Base (Compartidos por SQL y RAG)
    contextualize_q_system_prompt = """Dado el historial de chat y la última pregunta del usuario 
    que podría referirse al contexto en el historial, formula una pregunta independiente 
    que se pueda entender sin el historial. NO respondas la pregunta, 
    solo reformúlala si es necesario, de lo contrario devuélvela tal cual."""

    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    rag_prompt = ChatPromptTemplate.from_messages([
        ("system", "Contesta la pregunta basándote SOLO en el siguiente contexto:\n\n{context}"),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    # RAG Chain Initialization
    rag_chain = None
    try:
        if embeddings:
            from langchain_community.vectorstores import Redis
            print(f"🔌 Conectando a Redis: {final_index_name}")
            vectorstore = Redis(
                redis_url=REDIS_URL,
                index_name=final_index_name,
                embedding=embeddings
            )
            retriever = vectorstore.as_retriever()
            history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
            document_chain = create_stuff_documents_chain(llm, rag_prompt)
            rag_chain = create_retrieval_chain(history_aware_retriever, document_chain)
    except Exception as e:
        print(f"⚠️ Error al conectar con Redis o configurar RAG: {e}")
        rag_chain = None
else:
    sql_agent = None
    rag_chain = None

@app.get("/api/dashboard")
async def get_dashboard_data():
    import sqlite3
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Obtener Top 5 Posiciones
        cursor.execute('''
            SELECT p.posicion, e.nombre, p.puntos, p.dif_gol 
            FROM posiciones p 
            JOIN equipos e ON p.equipo_id = e.id 
            ORDER BY p.posicion LIMIT 5
        ''')
        top_posiciones = [dict(row) for row in cursor.fetchall()]
        
        # 2. Obtener Últimos 5 Resultados
        cursor.execute('''
            SELECT p.fecha, el.nombre as local, ev.nombre as visita, p.goles_local, p.goles_visita 
            FROM partidos p 
            JOIN equipos el ON p.local_id = el.id 
            JOIN equipos ev ON p.visita_id = ev.id 
            ORDER BY p.id DESC LIMIT 5
        ''')
        ultimos_resultados = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return {
            "top_posiciones": top_posiciones,
            "ultimos_resultados": ultimos_resultados
        }
    except Exception as e:
        print(f"⚠️ Error en dashboard data: {e}")
        return {"error": str(e)}

# --- 5. Endpoints ---
class Message(BaseModel):
    role: str
    content: str

class QueryRequest(BaseModel):
    question: str
    history: Optional[List[Message]] = []

@app.post("/agent/chat")
async def chat_endpoint(request: QueryRequest):
    if not llm:
        return {
            "source": "mantenimiento", 
            "answer": "⚠️ Lo siento, he agotado mis créditos diarios de IA (OpenAI y Gemini). Por favor, intenta de nuevo en unos minutos o mañana. ¡El fútbol chileno te espera!"
        }
    
    pregunta = request.question
    chat_history = [
        HumanMessage(content=msg.content) if msg.role == "user" else AIMessage(content=msg.content)
        for msg in request.history
    ]

    # Clasificador de intención
    system_instruction = """
    Eres un clasificador de preguntas de fútbol.
    Si la pregunta requiere contar, sumar, ver puntos, tablas o estadísticas numéricas, responde SOLAMENTE: "SQL".
    Si la pregunta es sobre historia, reglas, apodos, o información cualitativa, responde SOLAMENTE: "RAG".
    Ten en cuenta el historial para entender a qué se refiere el usuario.
    """
    
    router_inputs = [("system", system_instruction)] + chat_history + [("human", pregunta)]
    decision = (llm.invoke(router_inputs)).content.strip()
    
    print(f"🤔 Router: {decision}")

    try:
        if "SQL" in decision and sql_agent:
            print("📊 SQL Agent...")
            # Reformular para SQL agent
            standalone_q = (contextualize_q_prompt | llm).invoke({"input": pregunta, "chat_history": chat_history})
            response = sql_agent.invoke({"input": standalone_q.content})
            return {"source": "database_sql", "answer": response["output"]}
        elif rag_chain:
            print("📚 RAG Chain...")
            response = rag_chain.invoke({"input": pregunta, "chat_history": chat_history})
            return {"source": "knowledge_base_rag", "answer": response["answer"]}
        else:
            return {"source": "error", "answer": "La herramienta solicitada no está configurada correctamente."}
            
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower() or "ResourceExhausted" in error_msg:
            return {
                "source": "mantenimiento",
                "answer": "⚠️ Créditos de IA agotados por hoy. El agente ha superado su límite de peticiones gratuitas. Por favor, intenta de nuevo mañana o en unas horas. ⚽️"
            }
        
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)

# --- MODIFICACIÓN DEL ROOT ENDPOINT ---
# Antes devolvía JSON, ahora devuelve el HTML del Frontend
@app.get("/")
def read_root():
    # Verifica que exista el archivo antes de enviarlo
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend no encontrado. Verifica la carpeta app/frontend"}
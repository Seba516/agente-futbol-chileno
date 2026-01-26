import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
# LangChain Imports
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
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
    description="API que responde sobre fútbol chileno usando SQL y RAG",
    version="1.0.0"
)

# Configurar CORS (Permitir peticiones desde el frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar el LLM (El cerebro)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# ---------------------------------------------------------
# 2. Configurar Herramienta SQL (Estadísticas)
# Ajustamos la ruta para que encuentre la DB incluso si ejecutamos desde la carpeta 'app'
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, "data", "campeonato_nacional_2025.db")
db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

# Creamos un agente especializado en SQL
# Este agente sabe mirar las tablas y crear queries automáticamente
sql_agent = create_sql_agent(
    llm=llm,
    db=db,
    agent_type="openai-tools",
    verbose=True
)

# ---------------------------------------------------------
# 3. Configurar Herramienta RAG (Texto/Historia)
# ---------------------------------------------------------
CHROMA_PATH = os.path.join(base_dir, "data", "chroma_db")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Conectar a la base vectorial que creamos antes
vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
retriever = vectorstore.as_retriever()

# A. Condensador de Contexto (Contextualize Question)
# Esto toma el historial y la nueva pregunta, y genera una pregunta "independiente" (standalone)
contextualize_q_system_prompt = """Dado el historial de chat y la última pregunta del usuario 
que podría referirse al contexto en el historial, formula una pregunta independiente 
que se pueda entender sin el historial. NO respondas la pregunta, 
solo reformúlala si es necesario, de lo contrario devuélvela tal cual."""

contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

# Creamos el retriever que entiende el historial
history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

# B. Cadena de Respuesta (Response Chain)
rag_prompt = ChatPromptTemplate.from_messages([
    ("system", "Contesta la pregunta basándote SOLO en el siguiente contexto:\n\n{context}"),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

document_chain = create_stuff_documents_chain(llm, rag_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, document_chain)

# ---------------------------------------------------------
# 4. Lógica de Enrutamiento (El "Router")
# ---------------------------------------------------------
# Modelo de datos para la petición (Request Body)
class Message(BaseModel):
    role: str  # "user" o "assistant"
    content: str

class QueryRequest(BaseModel):
    question: str
    history: Optional[List[Message]] = []

@app.post("/agent/chat")
async def chat_endpoint(request: QueryRequest):
    """
    Endpoint principal. Decide si la pregunta es de datos (SQL) o texto (RAG).
    """
    pregunta = request.question
    
    # Convertir historial a formato LangChain
    chat_history = []
    for msg in request.history:
        if msg.role == "user":
            chat_history.append(HumanMessage(content=msg.content))
        else:
            chat_history.append(AIMessage(content=msg.content))

    # Paso A: Preguntar al LLM qué herramienta usar
    system_instruction = """
    Eres un clasificador de preguntas de fútbol.
    Si la pregunta requiere contar, sumar, ver puntos, tablas o estadísticas numéricas, responde SOLAMENTE: "SQL".
    Si la pregunta es sobre historia, reglas, apodos, o información cualitativa, responde SOLAMENTE: "RAG".
    Ten en cuenta el historial para entender a qué se refiere el usuario si usa pronombres.
    """
    
    # El router también recibe el historial para entender el contexto
    router_inputs = [("system", system_instruction)]
    for msg in chat_history:
        router_inputs.append(msg)
    router_inputs.append(("human", pregunta))
    
    router_response = llm.invoke(router_inputs)
    decision = router_response.content.strip()
    
    print(f"🤔 Decisión del Router: {decision}")

    try:
        if "SQL" in decision:
            # Ejecutar Agente SQL
            # Reformulamos la pregunta con el LLM para que el agente SQL la entienda sin contexto
            print("📊 Ejecutando consulta SQL...")
            
            # Para SQL agent, es mejor reformular la pregunta primero si hay historial
            # ya que el create_sql_agent estándar no maneja chat_history nativamente tan fácil como el RAG chain
            standalone_q_chain = contextualize_q_prompt | llm
            standalone_q = standalone_q_chain.invoke({"input": pregunta, "chat_history": chat_history})
            query_to_run = standalone_q.content

            response = sql_agent.invoke({"input": query_to_run})
            return {
                "source": "database_sql",
                "answer": response["output"]
            }
        else:
            # Ejecutar Cadena RAG
            print("📚 Buscando en documentos de texto...")
            response = rag_chain.invoke({
                "input": pregunta,
                "chat_history": chat_history
            })
            return {
                "source": "knowledge_base_rag",
                "answer": response["answer"]
            }
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"status": "ok", "message": "El Agente Futbolero está activo ⚽️"}
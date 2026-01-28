import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# LangChain Imports
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
# Rutas corregidas para LangChain 0.3+
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# 1. Configuración Inicial
load_dotenv()
app = FastAPI(
    title="Agente Futbolero AI",
    description="API que responde sobre fútbol chileno usando SQL y RAG",
    version="1.0.0"
)

# Configurar el LLM (El cerebro)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# ---------------------------------------------------------
# 2. Configurar Herramienta SQL (Estadísticas)
# ---------------------------------------------------------
db_path = os.path.join("data", "resultados_campeonato_nacional_2025.db")

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
CHROMA_PATH = "data/chroma_db"
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Conectar a la base vectorial que creamos antes
vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
retriever = vectorstore.as_retriever()

# Template para respuestas basadas en texto
rag_prompt = ChatPromptTemplate.from_template("""
Contesta la pregunta basándote SOLO en el siguiente contexto:
<context>
{context}
</context>

Pregunta: {input}
""")

document_chain = create_stuff_documents_chain(llm, rag_prompt)
rag_chain = create_retrieval_chain(retriever, document_chain)

# ---------------------------------------------------------
# 4. Lógica de Enrutamiento (El "Router")
# ---------------------------------------------------------
# Modelo de datos para la petición (Request Body)
class QueryRequest(BaseModel):
    question: str

@app.post("/agent/chat")
async def chat_endpoint(request: QueryRequest):
    """
    Endpoint principal. Decide si la pregunta es de datos (SQL) o texto (RAG).
    """
    pregunta = request.question
    
    # Paso A: Preguntar al LLM qué herramienta usar
    # Esto es un "clasificador de intención" simple
    system_instruction = """
    Eres un clasificador de preguntas de fútbol.
    Si la pregunta requiere contar, sumar, ver puntos, tablas o estadísticas numéricas, responde SOLAMENTE: "SQL".
    Si la pregunta es sobre historia, reglas, apodos, o información cualitativa, responde SOLAMENTE: "RAG".
    """
    
    router_response = llm.invoke([
        ("system", system_instruction),
        ("human", pregunta)
    ])
    decision = router_response.content.strip()
    
    print(f"🤔 Decisión del Router: {decision}")

    try:
        if "SQL" in decision:
            # Ejecutar Agente SQL
            print("📊 Ejecutando consulta SQL...")
            response = sql_agent.invoke({"input": pregunta})
            return {
                "source": "database_sql",
                "answer": response["output"]
            }
        else:
            # Ejecutar Cadena RAG
            print("📚 Buscando en documentos de texto...")
            response = rag_chain.invoke({"input": pregunta})
            return {
                "source": "knowledge_base_rag",
                "answer": response["answer"]
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"status": "ok", "message": "El Agente Futbolero está activo ⚽️"}
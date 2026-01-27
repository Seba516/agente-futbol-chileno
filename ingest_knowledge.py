import os
import redis
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import Redis

# Cargar variables de entorno
load_dotenv()

DATA_PATH = "data/knowledge_base"
REDIS_URL = f"redis://:{os.getenv('REDIS_PASSWORD')}@{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}"
BASE_INDEX_NAME = os.getenv("REDIS_INDEX", "agente_futbol")

def ingest_data():
    print("🔄 Iniciando carga de documentos...")
    
    # 1. Cargar documentos
    loader = DirectoryLoader(DATA_PATH, glob="*.txt", loader_cls=TextLoader)
    documents = loader.load()
    print(f"📄 Documentos cargados: {len(documents)}")

    # 2. Dividir en fragmentos
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)
    print(f"🧩 Fragmentos creados: {len(chunks)}")

    # 3. Configurar Embeddings con Triple Fallback
    embeddings = None
    final_index_name = BASE_INDEX_NAME
    
    # Intento 1: OpenAI
    try:
        print("🔍 Probando OpenAI...")
        from langchain_openai import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        embeddings.embed_query("test")
        final_index_name += "_openai"
        print("✅ Usando OpenAI Embeddings")
    except Exception as e:
        print(f"⚠️ OpenAI falló: {e}")
        # Intento 2: Gemini
        try:
            print("🔍 Probando Google Gemini...")
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
            embeddings.embed_query("test")
            final_index_name += "_gemini"
            print("✅ Usando Google Gemini Embeddings")
        except Exception as e2:
            print(f"⚠️ Gemini falló: {e2}")
            # Intento 3: Local (Plan C)
            print("🔍 Cambiando a Plan C: Embeddings Locales (HuggingFace)...")
            from langchain_huggingface import HuggingFaceEmbeddings
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            final_index_name += "_local"
            print("✅ Usando HuggingFace Embeddings (Local)")

    # 4. Enviar a Redis
    print(f"🧠 Enviando a Redis ({os.getenv('REDIS_HOST')}) -> Índice: {final_index_name}...")
    Redis.from_documents(
        documents=chunks,
        embedding=embeddings,
        redis_url=REDIS_URL,
        index_name=final_index_name
    )
    print(f"🎉 ÉXITO: Base de conocimiento guardada en índice: {final_index_name}")

if __name__ == "__main__":
    ingest_data()
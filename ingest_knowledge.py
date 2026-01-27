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

def ingest_to_provider(chunks, provider_name):
    """Realiza la ingesta para un proveedor específico."""
    embeddings = None
    index_name = f"{BASE_INDEX_NAME}_{provider_name}"
    
    try:
        if provider_name == "openai":
            from langchain_openai import OpenAIEmbeddings
            print(f"🔍 Preparando OpenAI (Índice: {index_name})...")
            embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        elif provider_name == "gemini":
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            print(f"🔍 Preparando Gemini (Índice: {index_name})...")
            embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        
        # Validar
        embeddings.embed_query("test")
        
        # Ingestar
        print(f"🧠 Enviando a Redis -> {index_name}...")
        Redis.from_documents(
            documents=chunks,
            embedding=embeddings,
            redis_url=REDIS_URL,
            index_name=index_name
        )
        print(f"✅ ÉXITO: {provider_name.upper()} subido correctamente.")
        return True
    except Exception as e:
        print(f"❌ ERROR en {provider_name}: {e}")
        return False

def ingest_data():
    print("🔄 Iniciando carga de documentos...")
    
    # 1. Cargar documentos
    if not os.path.exists(DATA_PATH):
        print(f"❌ ERROR: No existe la carpeta {DATA_PATH}")
        return

    loader = DirectoryLoader(DATA_PATH, glob="*.txt", loader_cls=TextLoader)
    documents = loader.load()
    if not documents:
        print("⚠️ No hay archivos .txt para cargar.")
        return
        
    print(f"📄 Documentos cargados: {len(documents)}")

    # 2. Dividir en fragmentos
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)
    print(f"🧩 Fragmentos creados: {len(chunks)}")

    # 3. Intentar ambos proveedores
    success_count = 0
    
    # Ingesta OpenAI
    if ingest_to_provider(chunks, "openai"):
        success_count += 1
        
    # Ingesta Gemini
    if ingest_to_provider(chunks, "gemini"):
        success_count += 1

    if success_count == 0:
        print("\n❌ FALLO TOTAL: No se pudo ingestar en ningún proveedor (OpenAI o Gemini). Revisa tus API Keys.")
    else:
        print(f"\n🎉 PROCESO FINALIZADO: {success_count} índice(s) actualizados en Redis.")

if __name__ == "__main__":
    ingest_data()
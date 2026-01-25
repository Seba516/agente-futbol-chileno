import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# Cargar variables de entorno (API Key)
load_dotenv()

# Rutas
DATA_PATH = "data/knowledge_base"
CHROMA_PATH = "data/chroma_db"

def ingest_data():
    print("🔄 Iniciando carga de documentos...")
    
    # 1. Cargar documentos de texto
    loader = DirectoryLoader(DATA_PATH, glob="*.txt", loader_cls=TextLoader)
    documents = loader.load()
    print(f"📄 Documentos cargados: {len(documents)}")

    # 2. Dividir en fragmentos (Chunks)
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)
    print(f"🧩 Fragmentos creados: {len(chunks)}")

    # 3. Crear Embeddings y guardar en ChromaDB
    print("🧠 Generando embeddings (esto puede tardar un poco)...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Crea la base vectorial en disco
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    print(f"✅ Base de conocimiento vectorial guardada en: {CHROMA_PATH}")

if __name__ == "__main__":
    ingest_data()
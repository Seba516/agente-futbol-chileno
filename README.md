# ⚽️ Agente de IA: Fútbol Chileno (SQL + RAG)

Este proyecto implementa un Agente de Inteligencia Artificial Avanzado capaz de responder preguntas complejas sobre el Campeonato Nacional de Fútbol Chileno 2024-2025. 

Utiliza una arquitectura híbrida inteligente que decide dinámicamente qué herramienta utilizar:
1.  **Agente SQL:** Para consultas estadísticas precisas (tablas de posiciones, resultados, goles) consultando una base de datos relacional.
2.  **Sistema RAG (Retrieval-Augmented Generation):** Para consultas cualitativas (reglamento, historia, noticias) buscando en una base de conocimiento vectorial.

## 🚀 Características Principales

* **Router Semántico:** Un LLM clasifica la intención del usuario y enruta la pregunta a la herramienta experta correspondiente.
* **Base de Datos 2025:** Integración con SQLite (`campeonato_nacional_2025.db`) con resultados simulados y tablas de posiciones actualizadas.
* **Motor Vectorial:** Uso de ChromaDB y OpenAI Embeddings para búsqueda semántica en documentos de texto.
* **API REST:** Backend robusto construido con FastAPI.
* **Memoria:** Capacidad de razonamiento sobre datos estructurados y no estructurados.

## 🛠 Stack Tecnológico

* **Lenguaje:** Python 3.11
* **Framework API:** FastAPI + Uvicorn
* **Orquestación IA:** LangChain (v0.2 - Versión Estable)
* **Modelos:** GPT-3.5-turbo / GPT-4o
* **Bases de Datos:** * SQLite (Relacional)
    * ChromaDB (Vectorial)

## 📦 Instalación y Configuración

Sigue estos pasos para ejecutar el proyecto en tu entorno local.

### 1. Clonar el repositorio
```bash
git clone <URL_DE_TU_REPO>
cd futbol-agent

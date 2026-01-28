# ⚽️ Agente de IA: Fútbol Chileno 2025 (SQL + RAG)

Este proyecto implementa un Agente de Inteligencia Artificial capaz de responder preguntas sobre el Campeonato Nacional 2025. Utiliza una arquitectura híbrida:

1.  **Agente SQL:** Consulta la base de datos `resultados_campeonato_nacional_2025.db` para obtener estadísticas exactas, resultados de partidos y tablas de posiciones.
2.  **Sistema RAG:** Utiliza `ChromaDB` para buscar información cualitativa en documentos de texto (`equipos_info.txt`, `resultados_2025.txt`) sobre reglas, historia y contexto de los equipos.

## 🚀 Funcionalidades

* **Router Inteligente:** Decide automáticamente si usar SQL o RAG según la pregunta.
* **Consulta de Datos:** Responde preguntas complejas como *"¿Quién ganó el partido entre X e Y en la fecha 1?"* o *"¿Cuántos goles de visita tiene la U?"*.
* **Contexto:** Explica reglas y situaciones de equipos basándose en documentos actualizados.

## 🛠 Instalación y Uso

1.  **Clonar repositorio y crear entorno:**
    ```bash
    git clone <URL_DEL_REPO>
    cd futbol-agent
    python3.11 -m venv venv
    source venv/bin/activate
    ```

2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurar API Key:**
    Crea un archivo `.env` con tu llave: `OPENAI_API_KEY=sk-...`

4.  **Inicializar Base de Conocimiento (RAG):**
    Si es la primera vez, ejecuta:
    ```bash
    python ingest_knowledge.py
    ```
    *(Esto procesará los archivos en `data/knowledge_base/` y creará la memoria vectorial)*.

5.  **Ejecutar Agente:**
    ```bash
    uvicorn app.main:app --reload
    ```

## 🧪 Pruebas
* **Swagger UI:** `http://127.0.0.1:8000/docs`
* **Ejemplo SQL:** *"¿Cuáles fueron los resultados de la fecha 1?"*
* **Ejemplo RAG:** *"Háblame de los refuerzos de Colo-Colo para el 2025"*

---
**Autor:** Sebastián Soto - Proyecto Sistemas de IA
# 🤖⚽ Agente de Fútbol Chileno 2025 (Edición Dashboard)

Este proyecto es un **Asistente Experto en el Campeonato Nacional Chileno 2025**, diseñado para responder preguntas complejas sobre resultados, estadísticas y narrativa del torneo.

Combina un **Agente SQL** (para datos duros) con un sistema **RAG** (para contexto histórico), todo presentado en un dashboard moderno y responsivo.

## 🏗️ Arquitectura de Producción

El sistema está desplegado en una infraestructura de alto rendimiento diseñada para seguridad y velocidad:

```mermaid
graph TD
    User((Usuario)) --> |HTTPS/443| CF[🛡️ Cloudflare Proxy]
    CF --> |SSL Encriptado| GCE[☁️ Google Compute Engine]
    
    subgraph "Servidor Ubuntu (GCE)"
        Nginx[🦅 Nginx (Reverse Proxy)] --> |Proxy Pass| Uvi[🦄 Uvicorn + FastAPI]
        Uvi --> |Lógica| Agente[🤖 Agente AI (LangChain)]
        
        Agente --> |Consultas| SQL[(🗄️ SQLite - Resultados)]
        Agente --> |Contexto| Redis[(🧠 Redis Vector Store - RAG)]
        
        Agente -.-> |Plan A| OpenAI[⚡ GPT-4o]
        Agente -.-> |Plan B (Backup)| Gemini[🌟 Gemini 1.5 Flash]
    end
```

### Componentes Clave:
*   **Cloudflare:** Provee DNS, Proxy caché y protección DDoS. Gestiona el certificado SSL Edge.
*   **Nginx:** Servidor web reverso que maneja la terminación SSL y redirige el tráfico al puerto interno de la aplicación.
*   **FastAPI + Uvicorn:** Backend asíncrono de alto rendimiento en Python.
*   **Redis Stack:** Motor vectorial para búsquedas semánticas ultrarrápidas (RAG).

---

## 🚀 Características Principales

### 🧠 Inteligencia Híbrida
*   **Router de Intención (GPT-4o):** Clasifica cada pregunta:
    *   **SQL:** Para resultados, fechas exactas, goleadores, tablas ("¿Cómo salió la U?", "¿Quién es el campeón?").
    *   **RAG:** Para historia, reglas, apodos y contexto ("¿Qué es el Superclásico?", "¿Quiénes descendieron?").
*   **Respaldo Automático:** Usa **GPT-4o** como cerebro principal. Si se agota la cuota, conmuta automáticamente a **Gemini 1.5 Flash**.

### 🛡️ Blindaje Anti-Alucinaciones
*   **Precisión SQL:** Reglas estrictas prohíben inventar goleadores, estadios o datos no columnares.
*   **Validación Ida/Vuelta:** Distingue partidos repetidos exigiendo siempre la fecha exacta en la respuesta.
*   **Lógica de Ganador:** Algoritmo de comparación goles local vs visita para evitar falsos positivos en diferencias de goles.
*   **Sin IDs:** Respuestas limpias que solo usan nombres de equipos, ocultando IDs internos de base de datos.

### 📊 Dashboard Interactivo
*   **Frontend Moderno:** HTML5 + CSS Grid con diseño Glassmorphism.
*   **Stats en Tiempo Real:** Sidebar con Top 5 de la tabla y Últimos 5 Resultados directo desde SQLite.
*   **Responsive:** Adaptable a móviles y escritorio.

---

## 🛠️ Instalación y Despliegue

### Requisitos Previos
*   Python 3.10+
*   Redis Stack Server (corriendo local o en Docker)
*   Claves API: `OPENAI_API_KEY`, `GEMINI_API_KEY`

### 1. Configuración de Entorno
Crea un archivo `.env` en la raíz:
```env
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=...
REDIS_INDEX=agente_futbol
```

### 2. Generación de Base de Datos
Crea la base de datos SQLite y puebla los datos iniciales:
```bash
python3 data/generar_db.py
```

### 3. Ingesta de Conocimiento (RAG)
Procesa los archivos de texto (`data/knowledge_base/*.txt`) y genera los embeddings en Redis:
```bash
python3 ingest_knowledge.py
```

### 4. Ejecución del Servidor
Para correr en modo producción (background):
```bash
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers > app.log 2>&1 &
```

---

## 📂 Estructura del Proyecto

```text
.
├── app/
│   ├── main.py            # 🧠 Cerebro del Agente (API + Lógica)
│   └── frontend/          # 🎨 Interfaz de Usuario
│       ├── index.html
│       ├── style.css
│       └── script.js
├── data/
│   ├── campeonato_2025.db # 🗄️ Base de datos SQL
│   ├── generar_db.py      # Script de creación SQL
│   └── knowledge_base/    # 📄 Archivos de texto para RAG
├── ingest_knowledge.py    # ⚙️ Script de carga vectorial a Redis
└── requirements.txt       # Dependencias ligeras (GCP friendly)
```

---

## 🏆 Créditos
Desarrollado para la **UAI** como demostración de un Agente AI Avanzado con capacidades de razonamiento SQL+RAG y arquitectura resiliente.

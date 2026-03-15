Chatbot Project

Aplicación fullstack compuesta por:

Backend en Python (FastAPI)

Frontend en Node.js

Integración con modelo LLM (ej: OpenAI)

Sistema de embeddings y consultas

📦 Requisitos Previos

Antes de empezar, necesitas tener instalado:

Python 3.10+

Node.js 18+

Git

Puedes verificar:

python --version
node --version
git --version
🚀 Instalación Paso a Paso
1️⃣ Clonar el repositorio
git clone https://github.com/tu-usuario/chatbot.git
cd chatbot
2️⃣ Backend (FastAPI)

Ubicación:

backend/
Crear entorno virtual

Windows:

python -m venv venv
venv\Scripts\activate

Mac/Linux:

python3 -m venv venv
source venv/bin/activate
Instalar dependencias
pip install -r requirements.txt
Configurar variables de entorno

Crea un archivo .env dentro de backend/ con:

OPENAI_API_KEY=tu_api_key
3️⃣ Frontend (Node.js)

Ubicación:

frontend/

Instalar dependencias:

npm install

Si usa Vite:

npm run dev

Si usa Next.js:

npm run dev
▶️ Ejecutar el Proyecto
Iniciar Backend

Desde:

backend/
uvicorn app.main:app --reload

Servidor disponible en:

http://localhost:8000

Docs automáticas:

http://localhost:8000/docs
Iniciar Frontend

Desde:

frontend/
npm run dev

Normalmente corre en:

http://localhost:5173

o

http://localhost:3000

# arquitectura temporal

backend
 ├── api
 │   ├── main.py
 │   └── routes
 │        └── upload.py
 │
 ├── services
 │   └── kafka_producer.py
 │
 ├── workers
 │   ├── parser_worker.py
 │   ├── embedding_worker.py
 │   └── chroma_worker.py
 │
 ├── core
 │   ├── config.py
 │   └── dependencies.py
 │
 └── rag
     ├── loader.py
     ├── chunker.py
     ├── embedding.py
     └── vector_store.py


# Flujo

Browser
   │
   ▼
Nginx (reverse proxy)
   │
   ├── / → Frontend (React + Vite)
   └── /api → FastAPI
                │
                ▼
              Kafka
          (event pipeline)
                │
        ┌───────┴────────┐
        ▼                ▼
   parser_worker     embedding_worker
        │                │
        ▼                ▼
      chunks          embeddings
        │                │
        └───────► ChromaDB
                       │
                       ▼
                     Ollama
                 (LLM inference)

Shared state
     │
     ▼
    Redis

Observability
     │
     ├── Prometheus
     └── Grafana
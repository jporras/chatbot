Chatbot RAG Platform

Plataforma de chatbot basada en Retrieval Augmented Generation (RAG) para consultar documentos mediante un modelo LLM local.

La arquitectura utiliza un pipeline distribuido para ingestión de documentos, generación de embeddings y recuperación semántica antes de generar respuestas con un modelo de lenguaje.

Arquitectura
Flujo general
Usuario
   │
   ▼
Frontend (React + Vite)
   │
   ▼
Nginx (reverse proxy)
   │
   ▼
FastAPI Backend
   │
   ├── Upload documentos
   ├── Consulta preguntas
   │
   ▼
Kafka Event Bus
   │
   ├── Parser Worker
   ├── Embedding Worker
   │
   ▼
ChromaDB (vector store)
   │
   ▼
Recuperación de contexto
   │
   ▼
Ollama (LLM)
   │
   ▼
Respuesta al usuario

Tecnologías
Frontend

React

Vite

Interfaz web para:

subir documentos

hacer preguntas al chatbot

visualizar respuestas

Backend

FastAPI

Responsabilidades:

API REST

ingestión de documentos

recuperación de contexto

conexión con el LLM

Endpoints principales:

POST /api/upload
POST /api/ask

Procesamiento Asíncrono

Apache Kafka

Kafka se usa para desacoplar el pipeline de procesamiento:

upload → kafka topic → parser worker → embedding worker


Ventajas:

escalabilidad

resiliencia

procesamiento paralelo

Vector Store

ChromaDB

Función:

almacenar embeddings

realizar búsqueda semántica

Operaciones principales:

add_documents()
similarity_search()

Modelo de Lenguaje

Ollama

Se usa para:

generar respuestas

combinar pregunta + contexto recuperado

Ejemplo de modelos posibles:

llama3
mistral
phi3

Estado y Cache

Redis

Uso:

almacenamiento temporal

estado compartido

caché de resultados

Observabilidad
Métricas

Prometheus

Recolecta métricas de:

backend

workers

vector search

Dashboards

Grafana

Visualiza:

latencia

throughput

uso del modelo

Estructura del proyecto
chatbot/

backend/
 └ app/
     ├ api/
     │   ├ ask.py
     │   └ upload.py
     │
     ├ core/
     │   └ config.py
     │
     ├ rag/
     │   ├ loader.py
     │   ├ chunker.py
     │   └ vector_store.py
     │
     ├ ingest/
     │   ├ ingest.py
     │   ├ rag.py
     │   └ llm.py
     │
     ├ services/
     │   └ kafka.py
     │
     ├ workers/
     │   ├ parser.py
     │   └ embeddings.py
     │
     └ main.py

frontend/
 └ src/
     ├ components/
     ├ App.tsx
     └ main.tsx

nginx/
kafka/
redis/
chromadb/
prometheus/
grafana/
ollama/

Pipeline RAG
1️⃣ Ingestión de documentos
Usuario sube documento
       │
       ▼
FastAPI /upload
       │
       ▼
Kafka topic
       │
       ▼
Parser Worker


Se realiza:

lectura del documento

extracción de texto

chunking

2️⃣ Generación de embeddings
Chunks
   │
   ▼
Embedding Worker
   │
   ▼
Vector Store


Se crean embeddings y se almacenan en ChromaDB.

3️⃣ Consulta del usuario
Pregunta usuario
      │
      ▼
FastAPI /ask
      │
      ▼
embedding de pregunta
      │
      ▼
similarity search


Se recuperan los chunks más relevantes.

4️⃣ Generación de respuesta
Pregunta + contexto
        │
        ▼
Ollama
        │
        ▼
Respuesta final

Despliegue

Servicios principales en contenedores:

frontend
nginx
backend
kafka
redis
chromadb
ollama
prometheus
grafana


Se orquestan con:

docker compose

Objetivo del proyecto

Construir una plataforma modular de RAG que permita:

ingestión de documentos

consultas semánticas

modelos LLM locales

arquitectura escalable basada en eventos
# Chatbot RAG Platform

## 1) ¿Qué es este proyecto?

Este repositorio implementa una plataforma **RAG (Retrieval-Augmented Generation)** para consultar documentos empresariales desde una interfaz web.

El flujo principal es:

1. El usuario sube documentos (`.pdf` y `.md`) desde el frontend.
2. El backend recibe la carga y publica eventos de procesamiento.
3. Workers consumen eventos para parsear, chunkear, generar embeddings y guardar en Chroma.
4. El usuario hace preguntas y recibe avance en tiempo real por **SSE** hasta la respuesta final del LLM.

El objetivo es desacoplar ingestión y consulta usando servicios/eventos para escalar y mantener trazabilidad de cada etapa.

---

## 2) Tecnologías usadas

### Frontend
- React + Vite + TypeScript
- SSE para seguimiento en vivo de procesos (`upload` y `ask`)

### Backend
- FastAPI (API REST)
- Redis (estado de documentos/consultas y contexto conversacional)
- Kafka (bus de eventos para el pipeline asíncrono)
- ChromaDB (almacenamiento vectorial de embeddings)
- Ollama (generación de respuesta con LLM local)

### Procesamiento RAG
- Chunking por tipo de documento (`MarkdownChunker`, `SemanticChunker`)
- Embeddings con modelo configurable
- Recuperación híbrida + reranking
- Filtros por metadatos

---

## 3) Prerrequisitos

Antes de instalar, asegúrate de tener:

- Docker y Docker Compose
- Node.js 20+ y npm (para desarrollo frontend local)
- Python 3.11+ (para desarrollo backend local)
- (Opcional) acceso a GPU si quieres acelerar LLM/embeddings

---

## 4) Instalación y ejecución

## Opción A: con Docker Compose (recomendada)

1. Clona el repositorio.
2. Configura variables de entorno (`.env`) para backend/frontend según tu entorno.
3. Levanta la plataforma:

```bash
docker compose -f docker_compose.yml up --build
```

4. Verifica servicios:
   - Backend: `http://localhost:8000`
   - Frontend: (según configuración de tu contenedor/frontend)
   - Chroma: `http://localhost:8001`
   - Grafana: `http://localhost:3001`
   - Prometheus: `http://localhost:9090`

## Opción B: desarrollo local mixto

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 5) Endpoints principales

### Ingesta de documentos
- `POST /api/upload`
- `GET /api/uploads/{batch_id}/status`
- `GET /api/uploads/{batch_id}/stream` (SSE)
- `GET /api/documents/{document_id}/status`

### Consulta RAG
- `POST /api/ask`
- `GET /api/queries/{query_id}/status`
- `GET /api/queries/{query_id}/stream` (SSE)

### Contexto de usuario
- `GET /api/users/{user_id}/state`
- `GET /api/users/{user_id}/sessions/{session_id}/history`

---

## 6) Diagramas de funcionamiento

### 6.1 Arquitectura general

```text
┌───────────────┐
│   Frontend    │
│ React + SSE   │
└───────┬───────┘
        │ HTTP/SSE
        ▼
┌───────────────┐      publish/subscribe      ┌───────────────┐
│    FastAPI    │ ───────────────────────────▶ │     Kafka     │
│ upload / ask  │                              │ event bus      │
└───────┬───────┘                              └───────┬───────┘
        │ set/get status                              │ consume
        ▼                                             ▼
┌───────────────┐                              ┌───────────────┐
│     Redis     │                              │    Workers    │
│ estado + SSE  │                              │ parser/embed  │
└───────────────┘                              └───────┬───────┘
                                                        │
                                                        ▼
                                                ┌───────────────┐
                                                │   ChromaDB    │
                                                │  embeddings   │
                                                └───────┬───────┘
                                                        │ retrieval
                                                        ▼
                                                ┌───────────────┐
                                                │    Ollama     │
                                                │     LLM       │
                                                └───────────────┘
```

### 6.2 Flujo de upload (asíncrono)

```text
Frontend -> POST /api/upload -> FastAPI
FastAPI -> Kafka (document.uploaded)
Parser Worker -> Kafka (document.chunked)
Embedding Worker -> Chroma (add embeddings)
Estado por etapa -> Redis
Frontend escucha -> /api/uploads/{batch_id}/stream
```

### 6.3 Flujo de pregunta (asíncrono)

```text
Frontend -> POST /api/ask -> query_id
Frontend -> SSE /api/queries/{query_id}/stream
Backend:
  EMBEDDING_QUERY -> HYBRID_RETRIEVAL -> RERANKING -> PROMPT_BUILD -> GENERATING -> DONE
Estados -> Redis pub/sub -> SSE al frontend
```

---

## 7) Notas operativas

- El sistema está pensado para retroalimentación en vivo por SSE, por eso los endpoints principales de negocio son `upload` y `ask` asíncronos.
- El procesamiento y la consulta usan servicios desacoplados por eventos (Kafka) y estado compartido (Redis).
<<<<<<< ours
<<<<<<< ours
<<<<<<< ours
- Los embeddings se almacenan en Chroma para recuperación semántica y filtros por metadatos.
=======
- Los embeddings se almacenan en Chroma para recuperación semántica y filtros por metadatos.
>>>>>>> theirs
=======
- Los embeddings se almacenan en Chroma para recuperación semántica y filtros por metadatos.
>>>>>>> theirs
=======
- Los embeddings se almacenan en Chroma para recuperación semántica y filtros por metadatos.
>>>>>>> theirs

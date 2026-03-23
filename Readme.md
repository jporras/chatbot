# Chatbot RAG Platform

Plataforma RAG orientada a documentos empresariales, diseñada como un sistema distribuido de ingesta asincrona, recuperacion hibrida y generacion asistida por LLM. El repositorio no implementa solo una UI de preguntas y respuestas: construye una arquitectura desacoplada con trazabilidad de etapas, versionado documental, procesamiento por eventos, estado en tiempo real y observabilidad operativa.

## Resumen Ejecutivo

Este proyecto demuestra una aproximacion de ingenieria mas cercana a una plataforma que a un monolito CRUD:

- separa ingesta, transformacion, indexacion y consulta en componentes con responsabilidades claras,
- desacopla la aceptacion de trabajo de su ejecucion intensiva mediante Kafka,
- usa Redis como store de estado operacional y canal de publicacion para SSE,
- combina ChromaDB, embeddings y reranking para retrieval de mayor calidad,
- integra Prometheus y Grafana como parte del sistema, no como un agregado posterior.

El resultado es una base que privilegia trazabilidad, mantenibilidad y capacidad de evolucion.

## Que Hace el Sistema

El sistema permite:

- cargar documentos `.pdf` y `.md`,
- parsearlos y dividirlos en chunks especializados,
- generar embeddings y persistirlos en ChromaDB,
- ejecutar consultas RAG con recuperacion hibrida, reranking y generacion con LLM,
- exponer el avance de ingesta y consulta en tiempo real via SSE,
- mantener contexto conversacional por usuario y sesion.

## Arquitectura

### Vista General

```text
                           +----------------------+
                           |      Frontend        |
                           | React + Vite + SSE   |
                           +----------+-----------+
                                      |
                                      | HTTP / SSE
                                      v
                           +----------------------+
                           |        Nginx         |
                           | Reverse Proxy        |
                           +----+------------+----+
                                |            |
                                |            |
                     +----------v--+      +--v------------------+
                     |   FastAPI    |      | Observability       |
                     | API Gateway  |      | Prometheus/Grafana  |
                     +------+-------+      +---------------------+
                            |
                 +----------+-----------+
                 |                      |
                 | write/read state     | publish events
                 v                      v
         +---------------+      +---------------+
         |     Redis     |      |     Kafka     |
         | state + SSE   |      | event backbone|
         +-------+-------+      +-------+-------+
                 ^                      |
                 |                      |
                 |               consume|
         +-------+-------+      +-------+--------+
         | Query Service  |      | Parser Worker  |
         | Retrieval/RAG  |      | Chunking       |
         +-------+--------+      +-------+--------+
                 |                       |
                 |                       | publish chunked docs
                 |                       v
                 |              +-------------------+
                 |              | Embedding Worker  |
                 |              | Vector indexing   |
                 |              +---------+---------+
                 |                        |
                 |                        |
                 v                        v
          +-------------+         +---------------+
          |   Ollama    |         |   ChromaDB    |
          | LLM runtime |         | Vector Store  |
          +-------------+         +---------------+
```

### Principios de Diseno

- desacoplamiento por eventos: la ingesta no depende del tiempo de ejecucion del pipeline pesado,
- responsabilidad unica por servicio: API, chunking, embeddings, almacenamiento y serving viven separados,
- trazabilidad operativa: cada documento y consulta expone estados intermedios,
- observabilidad integrada: el pipeline no es una caja negra,
- evolucion controlada: el sistema admite crecer hacia mas workers, exporters y politicas de retrieval.

## Flujo de Ingesta

### 1. Recepcion

El frontend envia uno o varios archivos al backend.

- endpoint: `POST /api/upload`
- el backend valida el tipo de archivo,
- persiste el archivo en almacenamiento local,
- reserva una nueva version logica del documento,
- publica un evento `document.uploaded` en Kafka,
- registra estado inicial en Redis.

### 2. Parsing y Chunking

`parser_worker` consume `document.uploaded`.

- carga el contenido del documento,
- selecciona la estrategia de chunking:
  - `MarkdownChunker` para `.md`
  - `SemanticChunker` para `.pdf`
- genera chunks con metadata rica para trazabilidad y recuperacion,
- publica `document.chunked` en Kafka.

### 3. Embeddings e Indexacion

`embedding_worker` consume `document.chunked`.

- genera embeddings con el modelo configurado,
- inserta chunks, embeddings y metadata en ChromaDB,
- publica `document.indexed`,
- actualiza estado final del documento en Redis.

## Flujo de Consulta

### 1. Entrada

- endpoint: `POST /api/ask`
- el backend crea un `query_id`,
- la ejecucion real corre en segundo plano,
- el frontend puede suscribirse al stream de estado.

### 2. Pipeline RAG

La consulta avanza por estas etapas:

1. `EMBEDDING_QUERY`
2. `HYBRID_RETRIEVAL`
3. `RERANKING`
4. `PROMPT_BUILD`
5. `GENERATING`
6. `DONE`

### 3. Recuperacion Hibrida

La busqueda combina:

- similitud vectorial en ChromaDB,
- busqueda por texto,
- deduplicacion por `chunk_hash`,
- seleccion de candidatos y reranking posterior.

Esto mejora recall y reduce la fragilidad de depender de una sola tecnica de retrieval.

### 4. Contexto Conversacional

Redis mantiene historial reciente y estado persistente basico por usuario/sesion para:

- reconstruir contexto reciente,
- conservar continuidad conversacional,
- enriquecer el prompt sin rehidratar toda la historia desde una capa mas costosa.

## Tiempo Real y UX Operacional

El sistema usa Redis Pub/Sub y SSE para reflejar el avance de procesos largos:

- `GET /api/uploads/{batch_id}/stream`
- `GET /api/queries/{query_id}/stream`

Esto permite una UX reactiva aun cuando el pipeline interno sigue ejecutandose en segundo plano.

## Observabilidad

La plataforma incluye monitoreo con Prometheus y Grafana.

### Que Se Mide

Se exponen metricas de:

- throughput de uploads,
- volumen de bytes ingeridos,
- chunks generados por estrategia,
- batches de embeddings,
- latencia total de consultas,
- latencia por etapa del pipeline RAG,
- latencia por etapa de ingesta,
- fallos por etapa,
- memoria RSS por proceso,
- consumo de CPU por servicio.

### Targets Scrapeados

Prometheus recolecta metricas de:

- `backend:8000/metrics`
- `parser:9101/metrics`
- `embedding:9102/metrics`
- `prometheus:9090/metrics`

### Grafana

Grafana queda aprovisionado con:

- un datasource de Prometheus,
- un dashboard inicial llamado `Chatbot RAG Observability`.

### Limite Actual

El dashboard incluye metricas de proceso Python y metricas de negocio del pipeline. Si se desea monitoreo mas profundo de host, contenedores, disco o red, el siguiente paso natural es agregar exporters como `node-exporter`, `cAdvisor`, `redis-exporter` y exporters para Kafka.

## Stack Tecnologico

### Frontend

- React
- Vite
- TypeScript
- SSE

### Backend y Pipeline

- FastAPI
- Kafka
- Redis
- ChromaDB
- Sentence Transformers
- Ollama

### Plataforma y Operacion

- Docker Compose
- Nginx
- Prometheus
- Grafana

## Estructura de Servicios

- `backend`: API principal y orquestacion sincronica de consultas.
- `parser`: procesamiento documental y chunking.
- `embedding`: generacion de embeddings e indexacion vectorial.
- `frontend`: interfaz web.
- `nginx`: reverse proxy y punto unico de entrada.
- `redis`: estado rapido, pub/sub y contexto.
- `kafka`: backbone de eventos.
- `chroma`: persistencia vectorial.
- `ollama`: inferencia local del LLM.
- `prometheus`: recoleccion de metricas.
- `grafana`: visualizacion y analisis operativo.

## Ejecucion con Docker Compose

```bash
docker compose up --build
```

## URLs Principales

Con la configuracion actual del repositorio:

- aplicacion: `http://localhost/`
- API docs: `http://localhost/docs`
- backend metrics: `http://localhost/metrics`
- Grafana: `http://localhost/grafana/`
- Prometheus: `http://localhost/prometheus/`

## Credenciales de Grafana

- usuario: `admin`
- password: `admin`

## Endpoints Relevantes

### Ingesta

- `POST /api/upload`
- `GET /api/uploads/{batch_id}/status`
- `GET /api/uploads/{batch_id}/stream`
- `GET /api/documents/{document_id}/status`

### Consulta

- `POST /api/ask`
- `GET /api/queries/{query_id}/status`
- `GET /api/queries/{query_id}/stream`

### Conversacion

- `GET /api/users/{user_id}/state`
- `GET /api/users/{user_id}/sessions/{session_id}/history`

## Senales de Ingenieria que Este Proyecto Demuestra

Para un reclutador o un ingeniero senior revisando el repositorio, este proyecto evidencia:

- diseno orientado a servicios y eventos en lugar de flujo lineal acoplado,
- separacion entre aceptacion de trabajo y ejecucion intensiva,
- versionado documental y metadatos orientados a trazabilidad,
- observabilidad desde el diseno y no como parche posterior,
- capacidad de streaming de estado para experiencias reactivas,
- retrieval hibrido y reranking en vez de un RAG ingenuo de una sola etapa,
- base apta para evolucionar hacia multi-worker, multi-model o despliegues mas productivos.

## Proximas Evoluciones Naturales

- agregar exporters de infraestructura para Docker y host,
- persistir alertas y reglas en Prometheus,
- introducir retries y DLQ para eventos fallidos,
- mover de hilos locales a un ejecutor de trabajos mas robusto para consultas,
- versionar prompts y politicas de retrieval,
- incorporar autenticacion y multitenancy.

## Conclusion

La propuesta va mas alla de “subir documentos y preguntarle a un modelo”. Se trata de una plataforma RAG con pipeline observable, componentes especializados y una arquitectura con criterios claros de desacoplamiento, mantenibilidad y capacidad de evolucion: justo el tipo de senal que suele separar un prototipo funcional de una pieza de ingenieria seria.

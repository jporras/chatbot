# Cambios necesarios para el backend

## 1) Alinear contratos API con el frontend actual

Hoy hay una desalineación entre lo que espera el frontend y lo que entrega el backend:

- El frontend de **upload** envía `file` y `document_id` (singular) y espera una respuesta directa por documento.
- El backend de **upload** recibe `files` y `document_ids` (plural/coma separada) y responde `batch_id + items`.
- El frontend de **ask** espera `{ answer, sources }` en la respuesta de `POST /api/ask`.
- El backend de **ask** devuelve `query_id` y procesamiento asíncrono, con estado/stream en endpoints aparte.

### Recomendación

Definir explícitamente una de estas dos estrategias:

1. **Modo síncrono simple (compatible con frontend actual)**
   - `POST /api/upload` acepta `file` y `document_id`.
   - `POST /api/ask` devuelve respuesta final `{ answer, sources }`.

2. **Modo asíncrono completo (recomendado para escalabilidad)**
   - Mantener `POST /api/upload` por lote y `POST /api/ask` por `query_id`.
   - Actualizar frontend para consumir `/uploads/{batch_id}/stream` y `/queries/{query_id}/stream`.

## 2) Endpoints de compatibilidad para transición

Para evitar romper clientes existentes, conviene agregar rutas puente:

- `POST /api/upload-single` (wrapper hacia el pipeline por lotes).
- `POST /api/ask-sync` (bloqueante, con timeout configurable).

Así se puede migrar el frontend por etapas sin cortar operación.

## 3) Validación de entrada y errores consistentes

- Estandarizar errores con un esquema común (`code`, `message`, `details`, `request_id`).
- Validar tamaño máximo de archivo, MIME real y extensiones permitidas.
- Limitar longitud de pregunta y rechazar payloads vacíos.
- Devolver 404 real en consultas de estado inexistentes (hoy se responde `{"detail": "Not found"}` con 200).

## 4) Idempotencia y deduplicación de ingestión

- Reforzar idempotencia por `document_id + file_hash` para evitar reprocesado accidental.
- Exponer un endpoint para reindexado explícito (`/api/documents/{id}/reindex`).
- Definir política de versiones y retención (última vs históricas) de forma contractual.

## 5) Seguridad y operación

- Restringir CORS (evitar `*` en producción).
- Añadir autenticación/autorización (API key o JWT).
- Incorporar rate limiting por IP/tenant en upload y ask.
- Sanitizar mensajes de error para no filtrar trazas internas.

## 6) Observabilidad y trazabilidad

- Propagar `correlation_id`/`request_id` en todo el flujo (API → Kafka → workers → SSE).
- Incluir métricas mínimas: latencia por etapa, throughput, errores por tipo, tamaño de cola, tiempo a indexado.
- Añadir health checks de dependencias (`redis`, `kafka`, `chromadb`, `ollama`) además del `health` básico.

## 7) Resiliencia del pipeline

- Configurar DLQ para eventos fallidos y estrategia de reintentos con backoff.
- Definir commits de offset de Kafka de forma segura (evitar pérdida/duplicación en fallos).
- Manejar chunking vacío y documentos no parseables con estados terminales claros.

## 8) Calidad de respuesta RAG

- Filtrar resultados por `is_latest` y por versión vigente del documento.
- Añadir reranking opcional y umbral de relevancia para evitar contexto ruido.
- Exponer metadatos de fuente uniformes (archivo, página, chunk, versión, score).

## 9) Checklist de implementación sugerido

1. Congelar contrato API objetivo (síncrono o asíncrono) y versionar (`/api/v1`).
2. Crear wrappers de compatibilidad temporal (`upload-single`, `ask-sync`).
3. Estandarizar errores y códigos HTTP.
4. Aplicar seguridad base (CORS, auth, rate limits).
5. Completar observabilidad y health checks profundos.
6. Endurecer resiliencia de Kafka (reintentos + DLQ + offsets).
7. Ajustar frontend al contrato definitivo y retirar rutas puente.

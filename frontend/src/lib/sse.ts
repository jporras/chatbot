import { API_BASE_URL } from "./api";

export function streamBatch(
  batchId: string,
  handlers: {
    onSnapshot?: (payload: unknown) => void;
    onDocumentStatus?: (payload: unknown) => void;
    onError?: () => void;
  },
) {
  const source = new EventSource(`${API_BASE_URL}/api/uploads/${batchId}/stream`);

  source.addEventListener("snapshot", (event) => {
    handlers.onSnapshot?.(JSON.parse((event as MessageEvent).data));
  });

  source.addEventListener("document_status", (event) => {
    handlers.onDocumentStatus?.(JSON.parse((event as MessageEvent).data));
  });

  source.onerror = () => handlers.onError?.();
  return source;
}

export function streamQuery(
  queryId: string,
  handlers: {
    onSnapshot?: (payload: unknown) => void;
    onQueryStatus?: (payload: unknown) => void;
    onError?: () => void;
  },
) {
  const source = new EventSource(`${API_BASE_URL}/api/queries/${queryId}/stream`);

  source.addEventListener("snapshot", (event) => {
    handlers.onSnapshot?.(JSON.parse((event as MessageEvent).data));
  });

  source.addEventListener("query_status", (event) => {
    handlers.onQueryStatus?.(JSON.parse((event as MessageEvent).data));
  });

  source.onerror = () => handlers.onError?.();
  return source;
}
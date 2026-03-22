export const API_BASE_URL = import.meta.env.VITE_API_URL?.replace(/\/$/, "") || "";

export type UploadResponse = {
  message: string;
  document_id: string;
  file_version?: number;
  correlation_id?: string;
  status: string;
};

export type AskSource = {
  document_id?: string;
  file_version?: number;
  filename?: string;
  source?: string;
  page?: number;
  chunk_index?: number;
  h1?: string;
  h2?: string;
  h3?: string;
};

export type AskResponse = {
  answer: string;
  sources?: AskSource[];
};

export type AskAcceptedResponse = {
  query_id: string;
  status: string;
};

export type UploadBatchItem = {
  filename: string;
  document_id: string;
  file_version: number;
  correlation_id: string;
  batch_id: string;
  status: string;
};

export type UploadBatchResponse = {
  batch_id: string;
  items: UploadBatchItem[];
};

export type DocumentStatus = {
  document_id: string;
  batch_id: string;
  filename: string;
  file_version: number;
  status: string;
  progress: number;
  stage_message: string;
  updated_at: string;
  error?: string | null;
};

async function parseJsonSafe<T>(response: Response): Promise<T | null> {
  const text = await response.text();
  if (!text) return null;

  try {
    return JSON.parse(text) as T;
  } catch {
    return null;
  }
}

export async function uploadDocuments(
  files: File[],
  documentIds?: string[],
): Promise<UploadBatchResponse> {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }
  if (documentIds && documentIds.length > 0) {
    formData.append("document_ids", documentIds.join(","));
  }

  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });

  const data = await parseJsonSafe<UploadBatchResponse | { detail?: string }>(response);

  if (!response.ok) {
    throw new Error(
      (data && "detail" in data && data.detail) || "No se pudo subir el lote de documentos.",
    );
  }

  if (!data || !("batch_id" in data) || !Array.isArray(data.items)) {
    throw new Error("La respuesta del backend para upload batch no es válida.");
  }

  return data;
}

export async function askQuestion(params: {
  question: string;
  userId?: string;
  sessionId?: string;
}): Promise<AskAcceptedResponse> {
  const response = await fetch(`${API_BASE_URL}/api/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question: params.question,
      user_id: params.userId ?? "web-user",
      session_id: params.sessionId ?? "default",
    }),
  });

  const data = await parseJsonSafe<AskAcceptedResponse | { detail?: string }>(response);

  if (!response.ok) {
    throw new Error(
      (data && "detail" in data && data.detail) || "No se pudo consultar el RAG.",
    );
  }

  if (!data || !("query_id" in data)) {
    throw new Error("La respuesta del backend para ask no es válida.");
  }

  return data;
}
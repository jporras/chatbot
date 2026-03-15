const API_BASE_URL = import.meta.env.VITE_API_URL?.replace(/\/$/, "") || "";

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

async function parseJsonSafe<T>(response: Response): Promise<T | null> {
  const text = await response.text();
  if (!text) return null;

  try {
    return JSON.parse(text) as T;
  } catch {
    return null;
  }
}

export async function uploadSingleDocument(params: {
  file: File;
  documentId?: string;
}): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", params.file);

  if (params.documentId?.trim()) {
    formData.append("document_id", params.documentId.trim());
  }

  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });

  const data = await parseJsonSafe<UploadResponse | { detail?: string }>(response);

  if (!response.ok) {
    throw new Error(
      (data && "detail" in data && data.detail) || "No se pudo subir el documento.",
    );
  }

  if (!data || !("document_id" in data)) {
    throw new Error("La respuesta del backend para upload no es válida.");
  }

  return data;
}

export async function askQuestion(question: string): Promise<AskResponse> {
  const response = await fetch(`${API_BASE_URL}/api/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });

  const data = await parseJsonSafe<AskResponse | { detail?: string }>(response);

  if (!response.ok) {
    throw new Error(
      (data && "detail" in data && data.detail) || "No se pudo consultar el RAG.",
    );
  }

  if (!data || !("answer" in data)) {
    throw new Error("La respuesta del backend para ask no es válida.");
  }

  return data;
}

import { useMemo, useRef, useState } from "react";
import { uploadSingleDocument, type UploadResponse } from "../lib/api";

type UploadJob = {
  localId: string;
  filename: string;
  documentId?: string;
  correlationId?: string;
  fileVersion?: number;
  status:
    | "SELECTED"
    | "UPLOADING"
    | "UPLOADED"
    | "PARSING"
    | "CHUNKED"
    | "EMBEDDING"
    | "INDEXED"
    | "FAILED";
  progress: number;
  stageMessage?: string;
  error?: string | null;
};


const ALLOWED_EXTENSIONS = [".pdf", ".md", ".txt"];

function isValidFile(file: File): boolean {
  const name = file.name.toLowerCase();
  return ALLOWED_EXTENSIONS.some((ext) => name.endsWith(ext));
}

function fileKey(file: File): string {
  return `${file.name}-${file.size}-${file.lastModified}`;
}

export type DocumentStatusResponse = {
  document_id: string;
  file_version?: number;
  filename?: string;
  status: string;
  progress?: number;
  stage_message?: string;
  updated_at?: string;
  error?: string | null;
};

export async function getDocumentStatus(documentId: string) {
  const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}/status`);
  if (!response.ok) {
    throw new Error("No se pudo consultar el estado del documento.");
  }
  return (await response.json()) as DocumentStatusResponse;
}

export default function UploadForm() {
  const inputRef = useRef<HTMLInputElement | null>(null);

  const [documentId, setDocumentId] = useState("");
  const [files, setFiles] = useState<UploadItem[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [results, setResults] = useState<UploadResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  const fileCountLabel = useMemo(() => {
    if (files.length === 0) return "No hay archivos seleccionados";
    if (files.length === 1) return "1 archivo listo para subir";
    return `${files.length} archivos listos para subir`;
  }, [files.length]);

  function appendFiles(fileList: FileList | null) {
    if (!fileList) return;

    const validFiles = Array.from(fileList).filter(isValidFile);
    const incoming = validFiles.map((file) => ({ file, id: fileKey(file) }));

    setFiles((prev) => {
      const seen = new Set(prev.map((item) => item.id));
      const dedupedIncoming = incoming.filter((item) => !seen.has(item.id));
      return [...prev, ...dedupedIncoming];
    });
  }

  function removeFile(id: string) {
    setFiles((prev) => prev.filter((item) => item.id !== id));
  }

  async function handleUpload() {
    if (files.length === 0) return;

    setIsUploading(true);
    setError(null);
    setResults([]);

    const uploaded: UploadResult[] = [];

    try {
      for (const item of files) {
        const response = await uploadSingleDocument({
          file: item.file,
          documentId: documentId || undefined,
        });

        uploaded.push({
          ...response,
          filename: item.file.name,
        });
      }

      setResults(uploaded);
      setFiles([]);
      setDocumentId("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ocurrió un error al subir.");
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <section className="mx-auto max-w-4xl">
      <div className="mb-8">
        <p className="text-sm uppercase tracking-[0.25em] text-cyan-400">
          Upload
        </p>
        <h2 className="mt-2 text-3xl font-semibold">Subir documentos al pipeline</h2>
        <p className="mt-3 max-w-2xl text-sm text-slate-400">
          Envía archivos PDF, Markdown o TXT al backend. Si indicas un{" "}
          <code className="rounded bg-slate-800 px-1.5 py-0.5 text-slate-200">
            document_id
          </code>{" "}
          el backend podrá tratarlos como nuevas versiones del mismo documento.
        </p>
      </div>

      <div className="space-y-6 rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl shadow-black/20">
        <div>
          <label htmlFor="documentId" className="mb-2 block text-sm font-medium text-slate-200">
            ID lógico del documento (opcional)
          </label>
          <input
            id="documentId"
            type="text"
            value={documentId}
            onChange={(e) => setDocumentId(e.target.value)}
            placeholder="ej. manual-empleados"
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-cyan-500"
          />
        </div>

        <div
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setIsDragging(false);
            appendFiles(e.dataTransfer.files);
          }}
          className={`rounded-2xl border-2 border-dashed p-8 text-center transition ${
            isDragging
              ? "border-cyan-500 bg-cyan-500/10"
              : "border-slate-700 bg-slate-950/70"
          }`}
        >
          <p className="text-lg font-medium text-slate-100">
            Arrastra tus archivos aquí
          </p>
          <p className="mt-2 text-sm text-slate-400">
            Se aceptan PDF, MD y TXT.
          </p>

          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            className="mt-5 rounded-xl bg-cyan-500 px-4 py-3 font-medium text-slate-950 transition hover:bg-cyan-400"
          >
            Seleccionar archivos
          </button>

          <input
            ref={inputRef}
            type="file"
            multiple
            accept=".pdf,.md,.txt"
            className="hidden"
            onChange={(e) => appendFiles(e.target.files)}
          />
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-950/80 p-4">
          <p className="text-sm font-medium text-slate-200">{fileCountLabel}</p>

          {files.length > 0 && (
            <ul className="mt-4 space-y-3">
              {files.map((item) => (
                <li
                  key={item.id}
                  className="flex items-center justify-between gap-4 rounded-xl border border-slate-800 bg-slate-900 px-4 py-3"
                >
                  <div>
                    <p className="font-medium text-slate-100">{item.file.name}</p>
                    <p className="text-sm text-slate-400">
                      {(item.file.size / 1024).toFixed(1)} KB
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={() => removeFile(item.id)}
                    className="rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 transition hover:bg-slate-800"
                  >
                    Quitar
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        {error && (
          <div className="rounded-xl border border-rose-800 bg-rose-950/40 px-4 py-3 text-sm text-rose-200">
            {error}
          </div>
        )}

        {results.length > 0 && (
          <div className="rounded-xl border border-emerald-800 bg-emerald-950/30 p-4">
            <h3 className="text-sm font-semibold uppercase tracking-wide text-emerald-300">
              Subidas realizadas
            </h3>

            <ul className="mt-4 space-y-3">
              {results.map((result, index) => (
                <li
                  key={`${result.document_id}-${index}`}
                  className="rounded-xl border border-emerald-900/60 bg-slate-950/50 p-4"
                >
                  <p className="font-medium text-slate-100">{result.filename}</p>
                  <p className="mt-1 text-sm text-slate-300">
                    document_id:{" "}
                    <code className="rounded bg-slate-800 px-1.5 py-0.5">
                      {result.document_id}
                    </code>
                  </p>
                  {typeof result.file_version !== "undefined" && (
                    <p className="mt-1 text-sm text-slate-300">
                      versión:{" "}
                      <code className="rounded bg-slate-800 px-1.5 py-0.5">
                        {result.file_version}
                      </code>
                    </p>
                  )}
                  {result.correlation_id && (
                    <p className="mt-1 text-sm text-slate-400">
                      correlation_id:{" "}
                      <code className="rounded bg-slate-800 px-1.5 py-0.5">
                        {result.correlation_id}
                      </code>
                    </p>
                  )}
                  <p className="mt-2 text-sm text-emerald-300">{result.message}</p>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="flex justify-end">
          <button
            type="button"
            disabled={files.length === 0 || isUploading}
            onClick={handleUpload}
            className="rounded-xl bg-cyan-500 px-5 py-3 font-medium text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isUploading ? "Subiendo..." : "Enviar al backend"}
          </button>
        </div>
      </div>
    </section>
  );
}

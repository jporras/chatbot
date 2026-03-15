import { useMemo, useRef, useState } from "react";
import { type DocumentStatus, uploadDocuments } from "../lib/api";
import { streamBatch } from "../lib/sse";
import StatusBadge from "./StatusBadge";

type BatchState = {
  batchId: string;
  items: Record<string, DocumentStatus>;
};

const ALLOWED_EXTENSIONS = [".pdf", ".md", ".txt"];

function isAllowedFile(file: File): boolean {
  const lower = file.name.toLowerCase();
  return ALLOWED_EXTENSIONS.some((ext) => lower.endsWith(ext));
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
}

export default function UploadConsole() {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const batchStreamRef = useRef<EventSource | null>(null);

  const [files, setFiles] = useState<File[]>([]);
  const [documentIdsText, setDocumentIdsText] = useState("");
  const [batch, setBatch] = useState<BatchState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  const summary = useMemo(() => {
    if (!batch) return null;

    const values = Object.values(batch.items);

    return {
      total: values.length,
      indexed: values.filter((item) => item.status === "INDEXED").length,
      failed: values.filter((item) => item.status === "FAILED").length,
      processing: values.filter(
        (item) => !["INDEXED", "FAILED"].includes(item.status),
      ).length,
    };
  }, [batch]);

  function dedupeFiles(nextFiles: File[]): File[] {
    const map = new Map<string, File>();

    for (const file of [...files, ...nextFiles]) {
      const key = `${file.name}-${file.size}-${file.lastModified}`;
      map.set(key, file);
    }

    return Array.from(map.values());
  }

  function addFiles(fileList: FileList | null) {
    if (!fileList) return;

    const incoming = Array.from(fileList);
    const invalid = incoming.filter((file) => !isAllowedFile(file));
    const valid = incoming.filter((file) => isAllowedFile(file));

    if (invalid.length > 0) {
      setError(
        `Estos archivos no están permitidos: ${invalid
          .map((file) => file.name)
          .join(", ")}`,
      );
    } else {
      setError(null);
    }

    if (valid.length > 0) {
      setFiles((prev) => {
        const map = new Map<string, File>();

        for (const file of [...prev, ...valid]) {
          const key = `${file.name}-${file.size}-${file.lastModified}`;
          map.set(key, file);
        }

        return Array.from(map.values());
      });
    }
  }

  function removeFile(indexToRemove: number) {
    setFiles((prev) => prev.filter((_, index) => index !== indexToRemove));
  }

  function clearFiles() {
    setFiles([]);
    setDocumentIdsText("");
    setError(null);
  }

  function parseDocumentIds(): string[] | undefined {
    const ids = documentIdsText
      .split("\n")
      .map((value) => value.trim())
      .filter(Boolean);

    if (ids.length === 0) return undefined;
    return ids;
  }

  async function handleUpload() {
    if (files.length === 0) return;

    setUploading(true);
    setError(null);

    try {
      const documentIds = parseDocumentIds();

      if (documentIds && documentIds.length !== files.length) {
        throw new Error(
          "Si defines document_id por línea, debe haber uno por cada archivo.",
        );
      }

      if (batchStreamRef.current) {
        batchStreamRef.current.close();
        batchStreamRef.current = null;
      }

      const result = await uploadDocuments(files, documentIds);

      setBatch({
        batchId: result.batch_id,
        items: Object.fromEntries(
          result.items.map((item) => [
            item.document_id,
            {
              document_id: item.document_id,
              batch_id: item.batch_id,
              filename: item.filename,
              file_version: item.file_version,
              status: item.status,
              progress: 10,
              stage_message: "Archivo recibido y enviado a la cola",
              updated_at: new Date().toISOString(),
              error: null,
            },
          ]),
        ),
      });

      const source = streamBatch(result.batch_id, {
        onSnapshot: (payload) => {
          const snapshot = payload as {
            batch_id: string;
            items: DocumentStatus[];
          };

          setBatch({
            batchId: snapshot.batch_id,
            items: Object.fromEntries(
              snapshot.items.map((item) => [item.document_id, item]),
            ),
          });
        },
        onDocumentStatus: (payload) => {
          const item = payload as DocumentStatus;

          setBatch((prev) => {
            if (!prev) return prev;

            return {
              ...prev,
              items: {
                ...prev.items,
                [item.document_id]: item,
              },
            };
          });
        },
        onError: () => {
          setError(
            "Se perdió la conexión en tiempo real del lote. Recarga la página o vuelve a subir si necesitas retomar el seguimiento.",
          );
          source.close();
          batchStreamRef.current = null;
        },
      });

      batchStreamRef.current = source;
      setFiles([]);
      setDocumentIdsText("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error en la carga.");
    } finally {
      setUploading(false);
    }
  }

  return (
    <section className="space-y-6">
      <div>
        <p className="text-sm uppercase tracking-[0.25em] text-cyan-400">
          Upload
        </p>
        <h2 className="mt-2 text-3xl font-semibold">
          Carga múltiple con seguimiento en vivo
        </h2>
        <p className="mt-3 max-w-3xl text-sm text-slate-400">
          Sube varios documentos al backend y sigue su progreso por etapa:
          recepción, parsing, chunking, embeddings e indexación. Puedes enviar
          un <code className="rounded bg-slate-800 px-1.5 py-0.5">document_id</code>{" "}
          por archivo para manejar versiones futuras del mismo documento lógico.
        </p>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <div className="rounded-2xl border-2 border-dashed border-slate-700 p-8 text-center">
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            className="rounded-xl bg-cyan-500 px-4 py-3 font-medium text-slate-950 transition hover:bg-cyan-400"
          >
            Seleccionar archivos
          </button>

          <input
            ref={inputRef}
            type="file"
            multiple
            accept=".pdf,.md,.txt"
            className="hidden"
            onChange={(e) => addFiles(e.target.files)}
          />

          <p className="mt-3 text-sm text-slate-400">PDF, MD o TXT</p>
        </div>

        <div className="mt-4">
          <label className="mb-2 block text-sm font-medium text-slate-200">
            document_id por línea (opcional, uno por archivo)
          </label>

          <textarea
            rows={4}
            value={documentIdsText}
            onChange={(e) => setDocumentIdsText(e.target.value)}
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-cyan-500"
            placeholder={"manual-empleados\npolitica-seguridad"}
          />

          <p className="mt-2 text-xs text-slate-500">
            Si escribes IDs, la cantidad debe coincidir exactamente con el número
            de archivos seleccionados.
          </p>
        </div>

        <div className="mt-4 rounded-xl border border-slate-800 bg-slate-950/70 p-4">
          <div className="flex items-center justify-between gap-4">
            <p className="text-sm text-slate-300">
              Archivos seleccionados: {files.length}
            </p>

            {files.length > 0 && (
              <button
                type="button"
                onClick={clearFiles}
                className="rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 transition hover:bg-slate-800"
              >
                Limpiar
              </button>
            )}
          </div>

          {files.length === 0 ? (
            <p className="mt-3 text-sm text-slate-500">
              Aún no has seleccionado archivos.
            </p>
          ) : (
            <ul className="mt-3 space-y-2">
              {files.map((file, idx) => (
                <li
                  key={`${file.name}-${file.size}-${file.lastModified}-${idx}`}
                  className="flex items-center justify-between gap-4 rounded-lg border border-slate-800 px-3 py-3 text-sm text-slate-200"
                >
                  <div className="min-w-0">
                    <p className="truncate font-medium">{file.name}</p>
                    <p className="text-xs text-slate-500">
                      {formatBytes(file.size)}
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={() => removeFile(idx)}
                    className="rounded-lg border border-slate-700 px-3 py-2 text-xs text-slate-300 transition hover:bg-slate-800"
                  >
                    Quitar
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        {error && (
          <div className="mt-4 rounded-xl border border-rose-800 bg-rose-950/40 px-4 py-3 text-sm text-rose-200">
            {error}
          </div>
        )}

        <div className="mt-4 flex justify-end">
          <button
            type="button"
            onClick={handleUpload}
            disabled={files.length === 0 || uploading}
            className="rounded-xl bg-cyan-500 px-5 py-3 font-medium text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {uploading ? "Iniciando carga..." : "Subir lote"}
          </button>
        </div>
      </div>

      {batch && summary && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <div className="flex flex-wrap gap-3 text-sm text-slate-300">
            <span>
              Lote:{" "}
              <code className="rounded bg-slate-800 px-1.5 py-0.5">
                {batch.batchId}
              </code>
            </span>
            <span>Total: {summary.total}</span>
            <span>Indexados: {summary.indexed}</span>
            <span>En proceso: {summary.processing}</span>
            <span>Fallidos: {summary.failed}</span>
          </div>

          <div className="mt-6 space-y-4">
            {Object.values(batch.items).map((item) => (
              <article
                key={item.document_id}
                className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <p className="truncate font-medium text-slate-100">
                      {item.filename}
                    </p>
                    <p className="mt-1 text-xs text-slate-400">
                      document_id: {item.document_id}
                    </p>
                    <p className="text-xs text-slate-400">
                      versión: {item.file_version}
                    </p>
                  </div>

                  <StatusBadge status={item.status} />
                </div>

                <div className="mt-4 h-3 overflow-hidden rounded-full bg-slate-800">
                  <div
                    className="h-full rounded-full bg-cyan-500 transition-all duration-300"
                    style={{ width: `${item.progress}%` }}
                  />
                </div>

                <div className="mt-3 flex items-center justify-between gap-4">
                  <p className="text-sm text-slate-300">{item.stage_message}</p>
                  <p className="text-xs text-slate-500">{item.progress}%</p>
                </div>

                <p className="mt-1 text-xs text-slate-500">
                  Actualizado: {new Date(item.updated_at).toLocaleString()}
                </p>

                {item.error && (
                  <p className="mt-2 text-sm text-rose-300">{item.error}</p>
                )}
              </article>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
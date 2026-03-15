import { useState } from "react";
import { askQuestion, type AskResponse } from "../lib/api";

type ChatMessage =
  | { role: "user"; text: string }
  | { role: "assistant"; text: string; sources?: AskResponse["sources"] };

type QueryStage =
  | "IDLE"
  | "RECEIVED"
  | "EMBEDDING_QUERY"
  | "RETRIEVAL"
  | "RERANKING"
  | "PROMPTING"
  | "GENERATING"
  | "DONE"
  | "FAILED";


export default function AskForm() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAsk() {
    const trimmed = question.trim();
    if (!trimmed || isLoading) return;

    setIsLoading(true);
    setError(null);

    setMessages((prev) => [...prev, { role: "user", text: trimmed }]);
    setQuestion("");

    try {
      const data = await askQuestion(trimmed);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.answer,
          sources: data.sources,
        },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo consultar el backend.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="mx-auto max-w-4xl">
      <div className="mb-8">
        <p className="text-sm uppercase tracking-[0.25em] text-cyan-400">
          Query
        </p>
        <h2 className="mt-2 text-3xl font-semibold">Preguntar al sistema RAG</h2>
        <p className="mt-3 max-w-2xl text-sm text-slate-400">
          Envía una pregunta al backend y revisa la respuesta junto con las fuentes recuperadas.
        </p>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl shadow-black/20">
        <div className="flex flex-col gap-3 md:flex-row">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Escribe tu pregunta..."
            rows={4}
            className="min-h-[120px] flex-1 rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-cyan-500"
          />

          <button
            type="button"
            disabled={isLoading || !question.trim()}
            onClick={handleAsk}
            className="rounded-xl bg-cyan-500 px-5 py-3 font-medium text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50 md:self-end"
          >
            {isLoading ? "Consultando..." : "Preguntar"}
          </button>
        </div>

        {error && (
          <div className="mt-4 rounded-xl border border-rose-800 bg-rose-950/40 px-4 py-3 text-sm text-rose-200">
            {error}
          </div>
        )}

        <div className="mt-6 space-y-4">
          {messages.length === 0 && (
            <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-6 text-sm text-slate-400">
              Aún no hay mensajes. Haz la primera consulta para probar el backend.
            </div>
          )}

          {messages.map((message, index) => (
            <article
              key={`${message.role}-${index}`}
              className={`rounded-2xl border p-4 ${
                message.role === "user"
                  ? "border-cyan-900 bg-cyan-950/20"
                  : "border-slate-800 bg-slate-950/70"
              }`}
            >
              <p className="mb-2 text-xs uppercase tracking-[0.2em] text-slate-400">
                {message.role === "user" ? "Usuario" : "Asistente"}
              </p>

              <p className="whitespace-pre-wrap text-sm leading-7 text-slate-100">
                {message.text}
              </p>

              {message.role === "assistant" &&
                message.sources &&
                message.sources.length > 0 && (
                  <div className="mt-4 rounded-xl border border-slate-800 bg-slate-900/60 p-4">
                    <p className="text-xs uppercase tracking-[0.2em] text-cyan-400">
                      Sources
                    </p>

                    <ul className="mt-3 space-y-3">
                      {message.sources.map((source, sourceIndex) => (
                        <li
                          key={`${source.filename ?? "source"}-${sourceIndex}`}
                          className="rounded-xl border border-slate-800 bg-slate-950/70 p-3 text-sm text-slate-300"
                        >
                          <p>
                            <span className="font-medium text-slate-100">
                              {source.filename ?? "Documento sin nombre"}
                            </span>
                          </p>

                          <div className="mt-2 flex flex-wrap gap-2 text-xs text-slate-400">
                            {typeof source.file_version !== "undefined" && (
                              <span className="rounded bg-slate-800 px-2 py-1">
                                v{source.file_version}
                              </span>
                            )}
                            {typeof source.page !== "undefined" && (
                              <span className="rounded bg-slate-800 px-2 py-1">
                                pág. {source.page}
                              </span>
                            )}
                            {typeof source.chunk_index !== "undefined" && (
                              <span className="rounded bg-slate-800 px-2 py-1">
                                chunk {source.chunk_index}
                              </span>
                            )}
                            {source.h1 && (
                              <span className="rounded bg-slate-800 px-2 py-1">
                                {source.h1}
                              </span>
                            )}
                            {source.h2 && (
                              <span className="rounded bg-slate-800 px-2 py-1">
                                {source.h2}
                              </span>
                            )}
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

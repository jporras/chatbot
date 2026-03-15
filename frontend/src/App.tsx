import { useState } from "react";
import UploadForm from "./components/UploadForm";
import AskForm from "./components/AskForm";

type View = "upload" | "chat";

export default function App() {
  const [view, setView] = useState<View>("upload");

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex min-h-screen max-w-7xl flex-col md:flex-row">
        <aside className="border-b border-slate-800 bg-slate-900/90 p-6 md:w-72 md:border-b-0 md:border-r">
          <div className="mb-8">
            <p className="text-xs uppercase tracking-[0.25em] text-cyan-400">
              Chatbot RAG
            </p>
            <h1 className="mt-2 text-2xl font-semibold">Panel del sistema</h1>
            <p className="mt-3 text-sm text-slate-400">
              Sube documentos, envíalos al pipeline y consulta el RAG desde una misma interfaz.
            </p>
          </div>

          <nav className="space-y-3">
            <button
              type="button"
              onClick={() => setView("upload")}
              className={`w-full rounded-xl px-4 py-3 text-left transition ${
                view === "upload"
                  ? "bg-cyan-500/15 text-cyan-300 ring-1 ring-cyan-500/30"
                  : "bg-slate-800 text-slate-200 hover:bg-slate-700"
              }`}
            >
              Subir documentos
            </button>

            <button
              type="button"
              onClick={() => setView("chat")}
              className={`w-full rounded-xl px-4 py-3 text-left transition ${
                view === "chat"
                  ? "bg-cyan-500/15 text-cyan-300 ring-1 ring-cyan-500/30"
                  : "bg-slate-800 text-slate-200 hover:bg-slate-700"
              }`}
            >
              Preguntar al RAG
            </button>
          </nav>
        </aside>

        <main className="flex-1 p-6 md:p-10">
          {view === "upload" ? <UploadForm /> : <AskForm />}
        </main>
      </div>
    </div>
  );
}

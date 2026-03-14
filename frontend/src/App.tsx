import { useState } from "react";
import UploadForm from "./components/UploadForm";
import Chat from "./components/AskForm";

export default function App() {
  const [view, setView] = useState("upload");
  const renderView = () => {
    if (view === "upload") return <UploadForm />;
    if (view === "chat") return <Chat />;
  };

  return (
    <div className="flex h-screen bg-slate-950 text-white">
      {/* Sidebar */}
      <div className="w-64 bg-slate-900 border-r border-slate-800 p-4">
        <h2 className="text-xl font-bold mb-6">
          RAG System
        </h2>
        <ul className="space-y-2">
          <li>
            <button onClick={() => setView("upload")} className="w-full text-left px-3 py-2 rounded hover:bg-slate-800">
              Subir documentos
            </button>
          </li>
          <li>
            <button onClick={() => setView("chat")} className="w-full text-left px-3 py-2 rounded hover:bg-slate-800">
              Preguntar al RAG
            </button>
          </li>
        </ul>
      </div>
      {/* Contenido central */}
      <div className="flex-1 p-6 overflow-auto">{renderView()}</div>
    </div>
  );
}
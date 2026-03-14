import { useState, useCallback } from "react";

export default function UploadForm() {
  const [files, setFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const validateFiles = (fileList: FileList | null) => {
    if (!fileList) return [];

    return Array.from(fileList).filter((file) => {
      const validTypes = ["application/pdf", "text/markdown"];
      return (
        validTypes.includes(file.type) ||
        file.name.endsWith(".pdf") ||
        file.name.endsWith(".md")
      );
    });
  };

  const handleFiles = (fileList: FileList | null) => {
    const valid = validateFiles(fileList);
    setFiles((prev) => [...prev, ...valid]);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    setIsUploading(true);

    const formData = new FormData();

    for (const file of files) {
      formData.append("files", file);
    }

    try {
      const res = await fetch("http://127.0.0.1:8000/api/upload", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Upload failed");
      }

      console.log("Upload result:", data);

    } catch (err) {
      console.error(err);
      if (err instanceof Error) {
        alert(err.message);
      }
    }

    setIsUploading(false);
    setFiles([]);
  };
  return (
    <div className="w-full min-h-screen bg-slate-950 text-white flex items-center justify-center p-6">
      <div className="w-full max-w-xl bg-slate-900 rounded-2xl shadow-2xl p-8 space-y-6">

        <h1 className="text-2xl font-bold text-center">
          Subir Documentos
        </h1>

        <div
          onDrop={handleDrop}
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          className={`border-2 border-dashed rounded-xl p-10 text-center transition-all duration-300
          ${isDragging 
            ? "border-blue-500 bg-slate-800 scale-105" 
            : "border-slate-600 bg-slate-800/50"}
          `}
        >
          <p className="text-slate-300">
            Arrastra tus archivos PDF o MD aquí
          </p>

          <p className="text-sm text-slate-500 mt-2">
            o selecciónalos manualmente
          </p>

          <input
            type="file"
            multiple
            accept=".pdf,.md"
            onChange={(e) => handleFiles(e.target.files)}
            className="hidden"
            id="fileInput"
          />

          <label
            htmlFor="fileInput"
            className="inline-block mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg cursor-pointer transition"
          >
            Seleccionar archivos
          </label>
        </div>

        {files.length > 0 && (
          <div className="bg-slate-800 rounded-lg p-4 max-h-40 overflow-y-auto">
            <ul className="space-y-2 text-sm">
              {files.map((file, index) => (
                <li
                  key={index}
                  className="flex justify-between items-center bg-slate-700 px-3 py-2 rounded-md"
                >
                  <span className="truncate">{file.name}</span>
                  <span className="text-xs text-slate-400">
                    {(file.size / 1024).toFixed(1)} KB
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={isUploading || files.length === 0}
          className={`w-full py-3 rounded-xl font-semibold transition-all duration-300
          ${isUploading
            ? "bg-slate-600 cursor-not-allowed"
            : "bg-emerald-600 hover:bg-emerald-700 hover:scale-[1.02]"}
          `}
        >
          {isUploading ? "Subiendo..." : "Subir archivos"}
        </button>

      </div>
    </div>
  );
}
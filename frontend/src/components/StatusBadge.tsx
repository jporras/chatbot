type Props = {
  status: string;
};

export default function StatusBadge({ status }: Props) {
  const colorMap: Record<string, string> = {
    QUEUED: "bg-slate-700 text-slate-100",
    UPLOADED: "bg-cyan-900 text-cyan-200",
    PARSING: "bg-amber-900 text-amber-200",
    CHUNKING: "bg-orange-900 text-orange-200",
    CHUNKED: "bg-indigo-900 text-indigo-200",
    EMBEDDING: "bg-violet-900 text-violet-200",
    INDEXED: "bg-emerald-900 text-emerald-200",
    FAILED: "bg-rose-900 text-rose-200",
    RECEIVED: "bg-cyan-900 text-cyan-200",
    EMBEDDING_QUERY: "bg-violet-900 text-violet-200",
    RETRIEVAL: "bg-indigo-900 text-indigo-200",
    PROMPT_BUILD: "bg-amber-900 text-amber-200",
    GENERATING: "bg-orange-900 text-orange-200",
    DONE: "bg-emerald-900 text-emerald-200",
  };

  return (
    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${colorMap[status] || "bg-slate-800 text-slate-200"}`}>
      {status}
    </span>
  );
}
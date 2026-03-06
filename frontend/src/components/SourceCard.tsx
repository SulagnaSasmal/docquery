"use client";

interface Source {
  title: string;
  url: string;
  section: string;
  score: number;
  doc_type: string;
  excerpt?: string;
}

export function SourceCard({ source }: { source: Source }) {
  const scorePercent = Math.round(source.score * 100);

  // Bar colour tiers
  const barColor =
    scorePercent >= 75
      ? "bg-emerald-500"
      : scorePercent >= 50
        ? "bg-amber-400"
        : "bg-red-400";

  const labelColor =
    scorePercent >= 75
      ? "text-emerald-700 dark:text-emerald-400"
      : scorePercent >= 50
        ? "text-amber-600 dark:text-amber-400"
        : "text-red-500 dark:text-red-400";

  return (
    <a
      href={source.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 hover:border-indigo-300 dark:hover:border-indigo-600 transition-colors group"
    >
      {/* Header row: type badge + section breadcrumb */}
      <div className="flex items-center gap-2 mb-1">
        <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 uppercase tracking-wider shrink-0">
          {source.doc_type || "docs"}
        </span>
        {source.section && (
          <span className="text-xs text-slate-400 dark:text-slate-500 truncate">
            {source.section}
          </span>
        )}
      </div>

      {/* Title */}
      <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors leading-snug">
        {source.title}
      </p>

      {/* Excerpt — Rovo-style quoted snippet */}
      {source.excerpt && (
        <p className="mt-1.5 text-xs text-slate-500 dark:text-slate-400 leading-relaxed border-l-2 border-slate-200 dark:border-slate-700 pl-2.5 line-clamp-2">
          {source.excerpt}
        </p>
      )}

      {/* Footer: URL + relevance bar */}
      <div className="mt-2 flex items-center justify-between gap-3">
        <span className="text-[11px] text-slate-400 dark:text-slate-500 truncate">
          {source.url}
        </span>
        <div className="flex items-center gap-1.5 shrink-0">
          {/* Mini bar */}
          <div className="w-14 h-1.5 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden">
            <div
              className={`h-full rounded-full ${barColor} transition-all`}
              style={{ width: `${scorePercent}%` }}
            />
          </div>
          <span className={`text-[11px] font-bold ${labelColor}`}>
            {scorePercent}%
          </span>
        </div>
      </div>
    </a>
  );
}

"use client";

interface Source {
  title: string;
  url: string;
  section: string;
  score: number;
  doc_type: string;
}

export function SourceCard({ source }: { source: Source }) {
  const scorePercent = Math.round(source.score * 100);
  const scoreColor =
    scorePercent >= 85
      ? "text-emerald-600 dark:text-emerald-400"
      : scorePercent >= 70
        ? "text-amber-600 dark:text-amber-400"
        : "text-red-500 dark:text-red-400";

  return (
    <a
      href={source.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 hover:border-indigo-300 dark:hover:border-indigo-600 transition-colors group"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 mb-0.5">
            <span className="text-xs font-medium px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 uppercase tracking-wide">
              {source.doc_type || "docs"}
            </span>
            <span className="text-xs text-slate-400 dark:text-slate-500 truncate">
              {source.section}
            </span>
          </div>
          <p className="text-sm font-medium text-slate-800 dark:text-slate-200 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors truncate">
            {source.title}
          </p>
          <p className="text-xs text-slate-400 dark:text-slate-500 truncate mt-0.5">
            {source.url}
          </p>
        </div>
        <div className="flex flex-col items-end shrink-0">
          <span className={`text-xs font-bold ${scoreColor}`}>
            {scorePercent}%
          </span>
          <span className="text-[10px] text-slate-400 dark:text-slate-500">
            match
          </span>
        </div>
      </div>
    </a>
  );
}

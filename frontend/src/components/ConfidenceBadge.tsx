"use client";

interface ConfidenceBadgeProps {
  level: string;
  score?: number;
}

export function ConfidenceBadge({ level, score }: ConfidenceBadgeProps) {
  const normalized = level.toUpperCase();

  const config: Record<string, { bg: string; text: string; dot: string; label: string }> = {
    HIGH: {
      bg: "bg-emerald-50 dark:bg-emerald-900/20",
      text: "text-emerald-700 dark:text-emerald-400",
      dot: "bg-emerald-500",
      label: "High confidence",
    },
    MEDIUM: {
      bg: "bg-amber-50 dark:bg-amber-900/20",
      text: "text-amber-700 dark:text-amber-400",
      dot: "bg-amber-500",
      label: "Medium confidence",
    },
    LOW: {
      bg: "bg-red-50 dark:bg-red-900/20",
      text: "text-red-700 dark:text-red-400",
      dot: "bg-red-500",
      label: "Low confidence",
    },
  };

  const c = config[normalized] || config.MEDIUM;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-medium ${c.bg} ${c.text}`}
      title={score !== undefined ? `Confidence score: ${Math.round(score * 100)}%` : c.label}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${c.dot}`} />
      {c.label}
      {score !== undefined && (
        <span className="opacity-70">({Math.round(score * 100)}%)</span>
      )}
    </span>
  );
}

"use client";

interface CollectionSelectorProps {
  value: string;
  onChange: (val: string) => void;
}

const COLLECTIONS = [
  { id: "vaultpay", label: "VaultPay", description: "Payment processing API" },
  { id: "sunbridge", label: "SunBridge Asset Atrium", description: "Enterprise investment platform" },
];

export function CollectionSelector({ value, onChange }: CollectionSelectorProps) {
  return (
    <div>
      <label className="block text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-2">
        Collection
      </label>
      <div className="space-y-1">
        {COLLECTIONS.map((col) => (
          <button
            key={col.id}
            onClick={() => onChange(col.id)}
            className={`w-full text-left px-3 py-2.5 rounded-lg text-sm transition-colors ${
              value === col.id
                ? "bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800"
                : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent"
            }`}
          >
            <div className="font-medium">{col.label}</div>
            <div className="text-xs opacity-60 mt-0.5">{col.description}</div>
          </button>
        ))}
      </div>
    </div>
  );
}

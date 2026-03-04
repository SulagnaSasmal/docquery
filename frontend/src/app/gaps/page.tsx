"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Gap {
  id: number;
  query: string;
  confidence_score: number;
  collection: string;
  timestamp: string;
  status: string;
  count: number;
}

export default function GapsPage() {
  const [gaps, setGaps] = useState<Gap[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("all");

  const fetchGaps = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filter !== "all") params.set("status", filter);
      const res = await fetch(`${API_URL}/api/gaps?${params}`);
      if (!res.ok) throw new Error("Failed");
      const data = await res.json();
      setGaps(data.gaps || []);
    } catch {
      setGaps([]);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    fetchGaps();
  }, [fetchGaps]);

  const updateStatus = async (id: number, status: string) => {
    try {
      await fetch(`${API_URL}/api/gaps/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status }),
      });
      fetchGaps();
    } catch {
      // ignore
    }
  };

  const statusColors: Record<string, string> = {
    open: "bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400",
    reviewing: "bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-400",
    resolved: "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400",
  };

  return (
    <div className="min-h-screen bg-white dark:bg-slate-950">
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <Link href="/" className="text-sm text-indigo-600 dark:text-indigo-400 hover:underline mb-2 inline-block">
              &larr; Back to chat
            </Link>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Content Gaps</h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
              Questions that received low-confidence answers, indicating missing documentation.
            </p>
          </div>
          <div className="text-right">
            <span className="text-3xl font-bold text-slate-900 dark:text-white">{gaps.length}</span>
            <p className="text-xs text-slate-500 dark:text-slate-400">gaps found</p>
          </div>
        </div>

        <div className="flex gap-2 mb-6">
          {["all", "open", "reviewing", "resolved"].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 text-sm rounded-lg capitalize transition-colors ${
                filter === f
                  ? "bg-indigo-600 text-white"
                  : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700"
              }`}
            >
              {f}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="text-center py-12 text-slate-500 dark:text-slate-400">Loading gaps...</div>
        ) : gaps.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-4xl mb-3">&#9989;</div>
            <p className="text-slate-600 dark:text-slate-400">No content gaps found. Documentation looks comprehensive!</p>
          </div>
        ) : (
          <div className="space-y-3">
            {gaps.map((gap) => (
              <div
                key={gap.id}
                className="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-slate-800 dark:text-slate-200 mb-1">
                      &ldquo;{gap.query}&rdquo;
                    </p>
                    <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
                      <span className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800">
                        {gap.collection}
                      </span>
                      <span>Score: {Math.round(gap.confidence_score * 100)}%</span>
                      <span>Asked {gap.count}x</span>
                      <span>{new Date(gap.timestamp).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[gap.status] || statusColors.open}`}>
                      {gap.status}
                    </span>
                    <select
                      value={gap.status}
                      onChange={(e) => updateStatus(gap.id, e.target.value)}
                      className="text-xs border border-slate-200 dark:border-slate-700 rounded-lg px-2 py-1 bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                    >
                      <option value="open">open</option>
                      <option value="reviewing">reviewing</option>
                      <option value="resolved">resolved</option>
                    </select>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

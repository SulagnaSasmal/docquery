"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Gap {
  id: number;
  question: string;
  confidence_score: number;
  collection: string;
  timestamp: string;
  status: string;
  count: number;
  nearest_section?: string;
}

interface GapCluster {
  representative: string;
  questions: string[];
  total_count: number;
  min_confidence: number;
  nearest_section: string;
  first_asked: string;
  last_asked: string;
  priority: "high" | "medium" | "low";
}

const PRIORITY_COLORS: Record<string, string> = {
  high: "bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400",
  medium: "bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-400",
  low: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400",
};

const STATUS_COLORS: Record<string, string> = {
  open: "bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400",
  reviewing: "bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-400",
  resolved: "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400",
};

export default function GapsPage() {
  const [collection, setCollection] = useState("default");
  const [filter, setFilter] = useState("open");
  const [viewMode, setViewMode] = useState<"cluster" | "flat">("cluster");
  const [gaps, setGaps] = useState<Gap[]>([]);
  const [clusters, setClusters] = useState<GapCluster[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ collection, status: filter });
      const [gapsRes, clustersRes] = await Promise.all([
        fetch(`${API_URL}/api/gaps?${params}`),
        fetch(`${API_URL}/api/gaps/clusters?${params}`),
      ]);
      if (gapsRes.ok) setGaps(await gapsRes.json());
      if (clustersRes.ok) setClusters(await clustersRes.json());
    } catch {
      setGaps([]);
      setClusters([]);
    } finally {
      setLoading(false);
    }
  }, [collection, filter]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const updateStatus = async (id: number, status: string) => {
    try {
      await fetch(`${API_URL}/api/gaps/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status }),
      });
      fetchData();
    } catch {
      // ignore
    }
  };

  const downloadMarkdown = async () => {
    const res = await fetch(`${API_URL}/api/gaps/report?collection=${collection}`);
    const text = await res.text();
    const blob = new Blob([text], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `gaps-${collection}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadCSV = async () => {
    const res = await fetch(`${API_URL}/api/gaps/export/csv?collection=${collection}`);
    const text = await res.text();
    const blob = new Blob([text], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `gaps-${collection}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const totalAsked = clusters.reduce((s, c) => s + c.total_count, 0);

  return (
    <div className="min-h-screen bg-white dark:bg-slate-950">
      <div className="max-w-4xl mx-auto px-6 py-8">

        {/* Header */}
        <div className="flex items-start justify-between mb-8">
          <div>
            <Link href="/" className="text-sm text-indigo-600 dark:text-indigo-400 hover:underline mb-2 inline-block">
              &larr; Back to chat
            </Link>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Content Gaps</h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
              Questions with low-confidence answers &mdash; topics missing from the documentation.
            </p>
          </div>
          <div className="text-right">
            <span className="text-3xl font-bold text-slate-900 dark:text-white">
              {viewMode === "cluster" ? clusters.length : gaps.length}
            </span>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {viewMode === "cluster"
                ? `clusters \u00b7 ${totalAsked} questions`
                : "distinct questions"}
            </p>
          </div>
        </div>

        {/* Controls */}
        <div className="flex flex-wrap items-center gap-3 mb-6">

          {/* Status filter */}
          <div className="flex gap-1">
            {["open", "reviewing", "resolved"].map((f) => (
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

          {/* View mode toggle */}
          <div className="flex gap-1 ml-auto">
            {(["cluster", "flat"] as const).map((mode) => (
              <button
                key={mode}
                onClick={() => setViewMode(mode)}
                className={`px-3 py-1.5 text-sm rounded-lg capitalize transition-colors ${
                  viewMode === mode
                    ? "bg-slate-800 dark:bg-slate-200 text-white dark:text-slate-900"
                    : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700"
                }`}
              >
                {mode === "cluster" ? "Clustered" : "All questions"}
              </button>
            ))}
          </div>

          {/* Export buttons */}
          <button
            onClick={downloadMarkdown}
            title="Download Markdown report"
            className="px-3 py-1.5 text-sm rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
          >
            &darr; Markdown
          </button>
          <button
            onClick={downloadCSV}
            title="Download CSV for spreadsheet"
            className="px-3 py-1.5 text-sm rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
          >
            &darr; CSV
          </button>
        </div>

        {/* Gap list */}
        {loading ? (
          <div className="text-center py-16 text-slate-500 dark:text-slate-400">
            Loading gaps&hellip;
          </div>
        ) : (viewMode === "cluster" ? clusters.length : gaps.length) === 0 ? (
          <div className="text-center py-16">
            <div className="text-4xl mb-3">&#x2705;</div>
            <p className="text-slate-600 dark:text-slate-400">
              No content gaps found. Documentation looks comprehensive!
            </p>
          </div>
        ) : viewMode === "cluster" ? (

          /* Cluster view */
          <div className="space-y-3">
            {clusters.map((cluster, i) => (
              <div
                key={i}
                className="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 mb-1">
                      &ldquo;{cluster.representative}&rdquo;
                    </p>
                    {cluster.questions.length > 1 && (
                      <div className="mb-2 space-y-0.5 pl-3 border-l-2 border-slate-200 dark:border-slate-700">
                        {cluster.questions.slice(1).map((q, j) => (
                          <p key={j} className="text-xs text-slate-500 dark:text-slate-500">
                            &ldquo;{q}&rdquo;
                          </p>
                        ))}
                      </div>
                    )}
                    <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 dark:text-slate-400 mt-1">
                      {cluster.nearest_section && (
                        <span className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800">
                          {cluster.nearest_section}
                        </span>
                      )}
                      <span>Asked {cluster.total_count}&times;</span>
                      <span>Confidence {Math.round(cluster.min_confidence * 100)}%</span>
                      {cluster.last_asked && (
                        <span>Last: {new Date(cluster.last_asked).toLocaleDateString()}</span>
                      )}
                    </div>
                  </div>
                  <span
                    className={`shrink-0 px-2 py-0.5 rounded-full text-xs font-medium ${PRIORITY_COLORS[cluster.priority]}`}
                  >
                    {cluster.priority}
                  </span>
                </div>
              </div>
            ))}
          </div>

        ) : (

          /* Flat view */
          <div className="space-y-3">
            {gaps.map((gap) => (
              <div
                key={gap.id}
                className="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-slate-800 dark:text-slate-200 mb-1">
                      &ldquo;{gap.question}&rdquo;
                    </p>
                    <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
                      <span className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800">
                        {gap.collection}
                      </span>
                      <span>Confidence {Math.round(gap.confidence_score * 100)}%</span>
                      <span>Asked {gap.count}&times;</span>
                      <span>{new Date(gap.timestamp).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_COLORS[gap.status] || STATUS_COLORS.open}`}
                    >
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

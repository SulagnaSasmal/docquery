"use client";

import { useState, useRef, useEffect } from "react";
import { ChatMessage } from "@/components/ChatMessage";
import { SourceCard } from "@/components/SourceCard";
import { ConfidenceBadge } from "@/components/ConfidenceBadge";
import { CollectionSelector } from "@/components/CollectionSelector";
import { ThemeToggle } from "@/components/ThemeToggle";
import { getDemoResponse, DEMO_BANNER } from "@/lib/demo";

const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");

interface Source {
  title: string;
  url: string;
  section: string;
  score: number;
  doc_type: string;
  excerpt?: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  confidence?: string;
  confidence_score?: number;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [collection, setCollection] = useState("vaultpay");
  const [sessionId, setSessionId] = useState("");
  const [demoMode, setDemoMode] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setSessionId(`session_${Math.random().toString(36).substring(2, 10)}`);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const question = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, session_id: sessionId, collection }),
        signal: AbortSignal.timeout(5000),
      });
      if (!res.ok) throw new Error("Failed");
      const data = await res.json();
      setDemoMode(false);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
          confidence: data.confidence,
          confidence_score: data.confidence_score,
        },
      ]);
    } catch {
      // Backend unavailable — fall back to pre-loaded demo responses
      setDemoMode(true);
      const demo = getDemoResponse(question, collection);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: demo.answer,
          sources: demo.sources,
          confidence: demo.confidence,
          confidence_score: demo.confidence_score,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setSessionId(`session_${Math.random().toString(36).substring(2, 10)}`);
  };

  return (
    <div className="flex h-screen bg-white dark:bg-slate-950">
      {/* Sidebar */}
      <div className="w-64 border-r border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 flex flex-col shrink-0">
        <div className="p-4 border-b border-slate-200 dark:border-slate-800">
          <h1 className="text-lg font-bold text-slate-900 dark:text-white">DocQuery</h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">RAG documentation chatbot</p>
        </div>
        <div className="p-4 flex-1">
          <CollectionSelector value={collection} onChange={(val) => { setCollection(val); clearChat(); }} />
        </div>
        <div className="p-4 border-t border-slate-200 dark:border-slate-800 space-y-2">
          <button onClick={clearChat} className="w-full px-3 py-2 text-sm text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-lg transition-colors">
            Clear conversation
          </button>
          <a href="/gaps" className="block w-full px-3 py-2 text-sm text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-lg transition-colors text-center">
            Content Gaps
          </a>
          <ThemeToggle />
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <div className="px-6 py-3 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 flex items-center justify-between gap-4">
          <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
            Querying: <span className="text-indigo-600 dark:text-indigo-400">{collection}</span>
          </span>
          {demoMode && (
            <span className="text-xs text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-full px-3 py-1 shrink-0">
              {DEMO_BANNER}
            </span>
          )}
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {messages.length === 0 && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center max-w-md">
                <div className="text-5xl mb-4">&#128218;</div>
                <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200 mb-2">Ask about your documentation</h2>
                <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">Answers come with source citations and confidence scores.</p>
                <div className="space-y-2 text-left">
                  {["How does OAuth authentication work?", "What are the webhook event types?", "How do I handle failed payments?"].map((q) => (
                    <button key={q} onClick={() => setInput(q)} className="w-full text-left px-4 py-2.5 text-sm text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i}>
              <ChatMessage role={msg.role} content={msg.content} />
              {msg.sources && msg.sources.length > 0 && (
                <div className="ml-11 mt-2 space-y-1.5">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium text-slate-500 dark:text-slate-400">Sources</span>
                    {msg.confidence && <ConfidenceBadge level={msg.confidence} score={msg.confidence_score} />}
                  </div>
                  {msg.sources.map((src, j) => <SourceCard key={j} source={src} />)}
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center text-xs font-bold text-indigo-600 dark:text-indigo-400 shrink-0">DQ</div>
              <div className="px-4 py-3 rounded-2xl bg-slate-100 dark:bg-slate-800">
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: "0ms" }} />
                  <div className="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: "150ms" }} />
                  <div className="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="px-6 py-4 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask a question about your documentation..." disabled={loading}
              className="flex-1 px-4 py-2.5 text-sm border border-slate-300 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent" />
            <button type="submit" disabled={loading || !input.trim()} className="px-5 py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">Send</button>
          </form>
        </div>
      </div>
    </div>
  );
}

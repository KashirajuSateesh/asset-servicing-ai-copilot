"use client";

import { useState } from "react";

type Citation = {
  source_number: number;
  document_name: string;
  page_number: number;
  chunk_index: number;
  business_domain: string;
  source_blob_name: string;
  score: number;
};

type CopilotResponse = {
  query: string;
  conversation_id?: string;
  route: string;
  record_id?: string | null;
  memory_used?: boolean;
  memory_saved?: boolean;
  response: {
    answer?: string;
    confidence_score?: number;
    confidence_label?: string;
    human_review_required?: boolean;
    citations?: Citation[];
    policy_guidance?: {
      answer: string;
      confidence_score: number;
      confidence_label: string;
      human_review_required: boolean;
      citations: Citation[];
    };
  };
};

export default function Home() {
  const [query, setQuery] = useState("What should I do for EXC-000001?");
  const [conversationId, setConversationId] = useState("conv_demo_ui_001");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CopilotResponse | null>(null);
  const [error, setError] = useState("");

  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

  const answer =
    result?.response?.policy_guidance?.answer || result?.response?.answer || "";

  const confidenceScore =
    result?.response?.policy_guidance?.confidence_score ||
    result?.response?.confidence_score;

  const confidenceLabel =
    result?.response?.policy_guidance?.confidence_label ||
    result?.response?.confidence_label;

  const humanReviewRequired =
    result?.response?.policy_guidance?.human_review_required ??
    result?.response?.human_review_required;

  const citations =
    result?.response?.policy_guidance?.citations ||
    result?.response?.citations ||
    [];

  async function askCopilot() {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const params = new URLSearchParams({
        query,
        top_k: "8",
        conversation_id: conversationId,
      });

      const response = await fetch(`${apiBaseUrl}/copilot/ask?${params}`);

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong while calling the copilot."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-100 text-slate-900">
      <div className="mx-auto max-w-7xl p-6">
        <header className="mb-6 rounded-3xl bg-slate-950 p-6 text-white shadow-lg">
          <p className="text-sm font-medium text-blue-300">
            Asset Servicing AI Copilot
          </p>
          <h1 className="mt-2 text-3xl font-bold">
            Operational Guidance, Policy RAG, and Persistent Agent Memory
          </h1>
          <p className="mt-3 max-w-3xl text-sm text-slate-300">
            Ask policy questions or record-specific questions. The orchestrator
            routes the request to SQL + RAG or document RAG and saves state into
            Cosmos DB.
          </p>
        </header>

        <div className="grid gap-6 lg:grid-cols-[1.4fr_0.8fr]">
          <section className="rounded-3xl bg-white p-6 shadow">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold">Copilot Chat</h2>
                <p className="text-sm text-slate-500">
                  Main endpoint: /copilot/ask
                </p>
              </div>
              <span className="rounded-full bg-green-100 px-3 py-1 text-sm font-medium text-green-700">
                Backend Connected
              </span>
            </div>

            <label className="text-sm font-medium">Conversation ID</label>
            <input
              className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-blue-500"
              value={conversationId}
              onChange={(event) => setConversationId(event.target.value)}
            />

            <label className="mt-4 block text-sm font-medium">Question</label>
            <textarea
              className="mt-2 min-h-28 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-blue-500"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />

            <div className="mt-4 flex flex-wrap gap-3">
              <button
                onClick={askCopilot}
                disabled={loading || !query.trim()}
                className="rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
              >
                {loading ? "Thinking..." : "Ask Copilot"}
              </button>

              <button
                onClick={() => setQuery("What should I do next?")}
                className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold hover:bg-slate-50"
              >
                Test Follow-up
              </button>

              <button
                onClick={() =>
                  setQuery("When should settlement exceptions be escalated?")
                }
                className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold hover:bg-slate-50"
              >
                Test Policy RAG
              </button>
            </div>

            {error && (
              <div className="mt-5 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                {error}
              </div>
            )}

            {result && (
              <div className="mt-6 rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <h3 className="text-lg font-semibold">Answer</h3>
                <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                  {answer}
                </p>
              </div>
            )}
          </section>

          <aside className="space-y-6">
            <section className="rounded-3xl bg-white p-6 shadow">
              <h2 className="text-lg font-semibold">Route & Memory</h2>

              <div className="mt-4 space-y-3 text-sm">
                <InfoRow label="Route" value={result?.route || "-"} />
                <InfoRow label="Record ID" value={result?.record_id || "-"} />
                <InfoRow
                  label="Memory Used"
                  value={String(result?.memory_used ?? false)}
                />
                <InfoRow
                  label="Memory Saved"
                  value={String(result?.memory_saved ?? false)}
                />
                <InfoRow
                  label="Confidence"
                  value={
                    confidenceScore !== undefined
                      ? `${confidenceScore} (${confidenceLabel})`
                      : "-"
                  }
                />
                <InfoRow
                  label="Human Review"
                  value={String(humanReviewRequired ?? "-")}
                />
              </div>
            </section>

            <section className="rounded-3xl bg-white p-6 shadow">
              <h2 className="text-lg font-semibold">Citations</h2>

              <div className="mt-4 space-y-3">
                {citations.length === 0 && (
                  <p className="text-sm text-slate-500">
                    Citations will appear after an answer is generated.
                  </p>
                )}

                {citations.map((citation) => (
                  <div
                    key={`${citation.source_number}-${citation.document_name}-${citation.chunk_index}`}
                    className="rounded-xl border border-slate-200 p-3"
                  >
                    <p className="text-sm font-semibold">
                      [{citation.source_number}] {citation.document_name}
                    </p>
                    <p className="mt-1 text-xs text-slate-500">
                      Page {citation.page_number} · Chunk{" "}
                      {citation.chunk_index} · {citation.business_domain}
                    </p>
                    <p className="mt-1 text-xs text-slate-400">
                      Score: {citation.score}
                    </p>
                  </div>
                ))}
              </div>
            </section>

            <section className="rounded-3xl bg-white p-6 shadow">
              <h2 className="text-lg font-semibold">Security & Observability</h2>
              <div className="mt-4 grid gap-3 text-sm">
                <StatusItem label="RBAC / Auth planned" status="Planned" />
                <StatusItem label="Audit logs planned" status="Planned" />
                <StatusItem label="Request tracing planned" status="Planned" />
                <StatusItem label="Error monitoring planned" status="Planned" />
              </div>
            </section>
          </aside>
        </div>
      </div>
    </main>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between border-b border-slate-100 pb-2">
      <span className="text-slate-500">{label}</span>
      <span className="font-medium text-slate-900">{value}</span>
    </div>
  );
}

function StatusItem({ label, status }: { label: string; status: string }) {
  return (
    <div className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-2">
      <span>{label}</span>
      <span className="rounded-full bg-blue-100 px-2 py-1 text-xs font-medium text-blue-700">
        {status}
      </span>
    </div>
  );
}
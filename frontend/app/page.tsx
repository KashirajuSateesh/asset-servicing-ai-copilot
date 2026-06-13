"use client";

import {
  AlertTriangle,
  BarChart3,
  Bot,
  BriefcaseBusiness,
  Database,
  FileText,
  FolderOpen,
  Gauge,
  LayoutDashboard,
  RefreshCcw,
  Search,
  Settings,
  ShieldCheck,
  Shuffle,
} from "lucide-react";
import { useState, type ReactNode } from "react";

type PageKey =
  | "dashboard"
  | "copilot"
  | "documents"
  | "exceptions"
  | "reconciliation"
  | "cases"
  | "analytics"
  | "admin";

type NavigationItem = {
  key: PageKey;
  label: string;
  icon: ReactNode;
};

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
  request_id?: string | null;
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

type SystemHealthResponse = {
  overall_status: string;
  components: {
    backend?: {
      status: string;
      message: string;
    };
    azure_sql?: {
      status: string;
      message: string;
    };
    azure_ai_search?: {
      status: string;
      message: string;
    };
    cosmos_memory_audit?: {
      status: string;
      message: string;
    };
    api_key_security?: {
      status: string;
      message: string;
    };
    audit_logging?: {
      status: string;
      message: string;
    };
  };
};

const navigationItems: NavigationItem[] = [
  {
    key: "dashboard",
    label: "Dashboard",
    icon: <LayoutDashboard className="h-5 w-5" />,
  },
  {
    key: "copilot",
    label: "Ask Copilot",
    icon: <Bot className="h-5 w-5" />,
  },
  {
    key: "documents",
    label: "Documents",
    icon: <FileText className="h-5 w-5" />,
  },
  {
    key: "exceptions",
    label: "Exceptions",
    icon: <AlertTriangle className="h-5 w-5" />,
  },
  {
    key: "reconciliation",
    label: "Reconciliation",
    icon: <Shuffle className="h-5 w-5" />,
  },
  {
    key: "cases",
    label: "Cases",
    icon: <FolderOpen className="h-5 w-5" />,
  },
  {
    key: "analytics",
    label: "Analytics",
    icon: <BarChart3 className="h-5 w-5" />,
  },
  {
    key: "admin",
    label: "Admin",
    icon: <Settings className="h-5 w-5" />,
  },
];

export default function Home() {
  const [activePage, setActivePage] = useState<PageKey>("dashboard");

  return (
    <main className="h-screen overflow-hidden bg-slate-100 text-slate-950">
      <div className="flex h-screen overflow-hidden">
        <Sidebar activePage={activePage} setActivePage={setActivePage} />

        <div className="flex h-screen min-w-0 flex-1 flex-col overflow-hidden">
          <Topbar />

          <section className="flex-1 overflow-y-auto p-8">
            {activePage === "dashboard" && <DashboardPage />}
            {activePage === "copilot" && <CopilotPage />}
            {activePage === "documents" && <DocumentsPage />}
            {activePage === "exceptions" && <ExceptionsPage />}
            {activePage === "reconciliation" && <ReconciliationPage />}
            {activePage === "cases" && <CasesPage />}
            {activePage === "analytics" && <AnalyticsPage />}
            {activePage === "admin" && <AdminPage />}
          </section>
        </div>
      </div>
    </main>
  );
}

function Sidebar({
  activePage,
  setActivePage,
}: {
  activePage: PageKey;
  setActivePage: (page: PageKey) => void;
}) {
  return (
    <aside className="sticky top-0 flex h-screen w-72 shrink-0 flex-col overflow-hidden bg-[#061a3a] text-white">
      <div className="flex h-20 shrink-0 items-center gap-3 border-b border-white/10 px-6">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-400/20 text-cyan-300">
          <Bot className="h-6 w-6" />
        </div>

        <div>
          <h1 className="text-lg font-bold">Asset Servicing</h1>
          <p className="text-xs text-slate-300">AI Copilot</p>
        </div>
      </div>

      <nav className="flex-1 space-y-2 overflow-y-auto px-4 py-6">
        {navigationItems.map((item) => {
          const isActive = activePage === item.key;

          return (
            <button
              key={item.key}
              onClick={() => setActivePage(item.key)}
              className={`flex w-full items-center gap-3 rounded-2xl px-4 py-3 text-left text-sm font-semibold transition ${
                isActive
                  ? "bg-cyan-500/25 text-white shadow"
                  : "text-slate-300 hover:bg-white/10 hover:text-white"
              }`}
            >
              {item.icon}
              {item.label}
            </button>
          );
        })}
      </nav>

      <div className="shrink-0 border-t border-white/10 p-5 text-xs text-slate-300">
        <div className="flex items-center gap-2">
          <RefreshCcw className="h-4 w-4" />
          <span>Data refreshed from live services</span>
        </div>

        <p className="mt-3 text-slate-400">
          Azure SQL • AI Search • Cosmos DB
        </p>
      </div>
    </aside>
  );
}

function Topbar() {
  return (
    <header className="flex h-20 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-8 shadow-sm">
      <div className="flex w-full max-w-2xl items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
        <Search className="h-5 w-5 text-slate-400" />
        <input
          className="w-full bg-transparent text-sm outline-none placeholder:text-slate-400"
          placeholder="Search for cases, exceptions, documents, policies..."
        />
      </div>

      <div className="flex items-center gap-5">
        <div className="hidden items-center gap-2 rounded-full bg-green-50 px-3 py-2 text-xs font-semibold text-green-700 md:flex">
          <ShieldCheck className="h-4 w-4" />
          Secure Demo
        </div>

        <div className="flex h-11 w-11 items-center justify-center rounded-full bg-blue-100 font-bold text-blue-800">
          MM
        </div>

        <div className="hidden md:block">
          <p className="text-sm font-semibold">Maria Martinez</p>
          <p className="text-xs text-slate-500">Operations Manager</p>
        </div>
      </div>
    </header>
  );
}

function DashboardPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Operations Overview"
        description="Your AI copilot for custody, settlement, reconciliation, and policy lookup."
      />

      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-5">
        <KpiCard
          title="Open Exceptions"
          value="1,248"
          change="+8.2%"
          tone="warning"
        />
        <KpiCard
          title="Reconciliation Breaks"
          value="762"
          change="-6.1%"
          tone="success"
        />
        <KpiCard title="Active Cases" value="320" change="+5.4%" tone="info" />
        <KpiCard
          title="SLA Risk Cases"
          value="48"
          change="+14.3%"
          tone="danger"
        />
        <KpiCard
          title="Avg Response Time Saved"
          value="2.6 hrs"
          change="+22%"
          tone="success"
        />
      </div>

      <div className="grid gap-6 xl:grid-cols-[2fr_1fr]">
        <section className="rounded-3xl bg-white p-6 shadow-sm">
          <h2 className="text-lg font-bold">Exceptions & Breaks Trend</h2>

          <div className="mt-5 flex h-72 items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50 text-sm text-slate-500">
            Trend chart placeholder
          </div>
        </section>

        <section className="rounded-3xl bg-white p-6 shadow-sm">
          <h2 className="text-lg font-bold">What this project does</h2>

          <div className="mt-5 space-y-5">
            <CapabilityItem
              icon={<FileText className="h-5 w-5" />}
              title="Citation-backed policy answers"
              description="Answers from policy documents, procedures, and SLAs."
            />
            <CapabilityItem
              icon={<Database className="h-5 w-5" />}
              title="Live trade & case lookup"
              description="Uses Azure SQL for operational records."
            />
            <CapabilityItem
              icon={<AlertTriangle className="h-5 w-5" />}
              title="Exception triage"
              description="Explains exceptions and recommends next actions."
            />
            <CapabilityItem
              icon={<Gauge className="h-5 w-5" />}
              title="Operations observability"
              description="Tracks health, audit events, and request IDs."
            />
          </div>
        </section>
      </div>

      <section className="rounded-3xl bg-white p-6 shadow-sm">
        <h2 className="text-lg font-bold">Priority Queues</h2>

        <div className="mt-5 overflow-hidden rounded-2xl border border-slate-200">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500">
              <tr>
                <th className="px-4 py-3">Queue</th>
                <th className="px-4 py-3">Open Items</th>
                <th className="px-4 py-3">SLA Risk</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Owner</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-200">
              <QueueRow
                queue="Settlement Exceptions"
                items="1,248"
                risk="126"
                status="At Risk"
                owner="Jason Smith"
              />
              <QueueRow
                queue="Reconciliation Breaks"
                items="762"
                risk="72"
                status="At Risk"
                owner="Aisha Lee"
              />
              <QueueRow
                queue="Corporate Actions"
                items="315"
                risk="18"
                status="Monitor"
                owner="Ravi Patel"
              />
              <QueueRow
                queue="Policy Queries"
                items="89"
                risk="2"
                status="On Track"
                owner="Maria Martinez"
              />
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function CopilotPage() {
  const [query, setQuery] = useState("");
  const [lastAskedQuestion, setLastAskedQuestion] = useState("");
  const [conversationId, setConversationId] = useState("conv_demo_ui_001");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CopilotResponse | null>(null);
  const [error, setError] = useState("");
  const [auditEvents, setAuditEvents] = useState<any[]>([]);

  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

  const copilotApiKey =
    process.env.NEXT_PUBLIC_COPILOT_API_KEY || "dev-copilot-key-123";

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
    setLastAskedQuestion(query);

    try {
      const params = new URLSearchParams({
        query,
        top_k: "8",
        conversation_id: conversationId,
      });

      const response = await fetch(`${apiBaseUrl}/copilot/ask?${params}`, {
        headers: {
          "x-copilot-api-key": copilotApiKey,
        },
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
      setQuery("");

      const auditResponse = await fetch(
        `${apiBaseUrl}/audit/events/${conversationId}?limit=5`
      );

      if (auditResponse.ok) {
        const auditData = await auditResponse.json();
        setAuditEvents(auditData.events || []);
      }
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
    <div className="space-y-8">
      <PageHeader
        title="Ask Copilot"
        description="Ask policy questions or record-specific questions. The orchestrator routes requests to SQL + RAG or document RAG."
      />

      <div className="grid gap-6 xl:grid-cols-[1.35fr_0.85fr]">
        <section className="rounded-3xl bg-white p-6 shadow-sm">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold">Copilot Chat</h2>
              <p className="text-sm text-slate-500">
                Protected endpoint: /copilot/ask
              </p>
            </div>

            <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-bold text-green-700">
              Backend Connected
            </span>
          </div>

          <label className="text-sm font-semibold">Conversation ID</label>
          <input
            className="mt-2 w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-cyan-500"
            value={conversationId}
            onChange={(event) => setConversationId(event.target.value)}
          />

          <label className="mt-5 block text-sm font-semibold">Question</label>
          <textarea
            className="mt-2 min-h-32 w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-cyan-500"
            value={query}
            placeholder="Ask about settlement exceptions, reconciliation breaks, custody policies, or enter an ID like EXC-000001, BRK-0000001, TRD-0000001..."
            onChange={(event) => setQuery(event.target.value)}
          />

          <div className="mt-5 flex flex-wrap gap-3">
            <button
              onClick={askCopilot}
              disabled={loading || !query.trim()}
              className="rounded-2xl bg-[#061a3a] px-5 py-3 text-sm font-bold text-white hover:bg-[#0b2855] disabled:cursor-not-allowed disabled:bg-slate-400"
            >
              {loading ? "Thinking..." : "Ask Copilot"}
            </button>

            <button
              onClick={() => setQuery("What should I do next?")}
              className="rounded-2xl border border-slate-300 px-5 py-3 text-sm font-bold hover:bg-slate-50"
            >
              Example: Follow-up
            </button>

            <button
              onClick={() =>
                setQuery("When should settlement exceptions be escalated?")
              }
              className="rounded-2xl border border-slate-300 px-5 py-3 text-sm font-bold hover:bg-slate-50"
            >
              Example: Policy Question
            </button>
          </div>

          {error && (
            <div className="mt-5 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              {error}
            </div>
          )}

          {result && (
            <div className="mt-6 rounded-3xl border border-slate-200 bg-slate-50 p-6">
              {lastAskedQuestion && (
                <div className="mb-4 rounded-2xl border border-blue-100 bg-blue-50 p-4">
                  <p className="text-xs font-bold uppercase text-blue-600">
                    You asked
                  </p>
                  <p className="mt-1 text-sm font-semibold text-blue-950">
                    {lastAskedQuestion}
                  </p>
                </div>
              )}

              <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold">Answer</h3>

                <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-bold text-blue-700">
                  {confidenceLabel || "unknown"}
                </span>
              </div>

              <p className="mt-4 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                {answer}
              </p>

              {citations.length > 0 && (
                <div className="mt-6">
                  <h4 className="text-sm font-bold">Citations</h4>

                  <div className="mt-3 grid gap-3">
                    {citations.map((citation) => (
                      <div
                        key={`${citation.document_name}-${citation.chunk_index}-${citation.source_number}`}
                        className="rounded-2xl border border-slate-200 bg-white p-4 text-xs"
                      >
                        <div className="flex items-center justify-between gap-3">
                          <p className="font-bold text-slate-800">
                            Source {citation.source_number}:{" "}
                            {citation.document_name}
                          </p>

                          <span className="rounded-full bg-slate-100 px-2 py-1 font-semibold text-slate-600">
                            Page {citation.page_number}
                          </span>
                        </div>

                        <p className="mt-2 text-slate-500">
                          Domain: {citation.business_domain} • Chunk:{" "}
                          {citation.chunk_index} • Score:{" "}
                          {citation.score?.toFixed
                            ? citation.score.toFixed(4)
                            : citation.score}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </section>

        <aside className="space-y-6">
          <section className="rounded-3xl bg-white p-6 shadow-sm">
            <h2 className="text-lg font-bold">Route & Memory</h2>

            <div className="mt-4 space-y-3 text-sm">
              <InfoRow label="Request ID" value={result?.request_id || "-"} />
              <InfoRow label="Route" value={result?.route || "-"} />
              <InfoRow label="Record ID" value={result?.record_id || "-"} />
              <InfoRow
                label="Memory Used"
                value={String(result?.memory_used ?? "-")}
              />
              <InfoRow
                label="Memory Saved"
                value={String(result?.memory_saved ?? "-")}
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

          <section className="rounded-3xl bg-white p-6 shadow-sm">
            <h2 className="text-lg font-bold">Security & Observability</h2>

            <div className="mt-4 grid gap-3 text-sm">
              <StatusItem label="API key protection" status="Active" />
              <StatusItem label="Audit logs" status="Active" />
              <StatusItem label="Cosmos memory tracking" status="Active" />
              <StatusItem label="Confidence monitoring" status="Active" />
              <StatusItem label="Human review flag" status="Active" />
              <StatusItem label="Azure Entra ID / RBAC" status="Future" />
            </div>

            <div className="mt-6">
              <h3 className="text-sm font-bold text-slate-700">
                Latest Audit Events
              </h3>

              <div className="mt-3 space-y-3">
                {auditEvents.length === 0 && (
                  <p className="text-sm text-slate-500">
                    Audit events will appear after a copilot request.
                  </p>
                )}

                {auditEvents.map((event) => (
                  <div
                    key={event.id}
                    className="rounded-2xl border border-slate-200 bg-slate-50 p-4"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-sm font-bold">
                        {event.event_type || "audit_event"}
                      </p>

                      <span className="rounded-full bg-green-100 px-2 py-1 text-xs font-bold text-green-700">
                        {event.status}
                      </span>
                    </div>

                    <div className="mt-3 space-y-1 text-xs text-slate-600">
                      <p>Request ID: {event.request_id || "-"}</p>
                      <p>Route: {event.route || "-"}</p>
                      <p>Record ID: {event.record_id || "-"}</p>
                      <p>Domain: {event.business_domain || "-"}</p>
                      <p>
                        Confidence:{" "}
                        {event.confidence_score !== null
                          ? `${event.confidence_score} (${event.confidence_label})`
                          : "-"}
                      </p>
                      <p>Memory used: {String(event.memory_used)}</p>
                      <p>Memory saved: {String(event.memory_saved)}</p>
                      <p className="text-slate-400">{event.created_at}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>
        </aside>
      </div>
    </div>
  );
}

function DocumentsPage() {
  return (
    <PlaceholderPage
      title="Documents"
      description="Policy PDFs, SOPs, SLA documents, indexing status, and document search will live here."
    />
  );
}

function ExceptionsPage() {
  return (
    <PlaceholderPage
      title="Exceptions"
      description="Settlement exceptions list, exception detail, AI insights, SLA risk, and recommended actions."
    />
  );
}

function ReconciliationPage() {
  return (
    <PlaceholderPage
      title="Reconciliation Breaks"
      description="Breaks table, AI match suggestions, aging, and resolution actions."
    />
  );
}

function CasesPage() {
  return (
    <PlaceholderPage
      title="Cases"
      description="Case queue, case history, linked trades, notes, and operational workflow."
    />
  );
}

function AnalyticsPage() {
  return (
    <PlaceholderPage
      title="Analytics"
      description="Operational KPIs, trend charts, SLA performance, response time saved, and team workload."
    />
  );
}

function AdminPage() {
  const [systemHealth, setSystemHealth] =
    useState<SystemHealthResponse | null>(null);
  const [conversationId, setConversationId] = useState("conv_demo_ui_001");
  const [auditEvents, setAuditEvents] = useState<any[]>([]);
  const [loadingHealth, setLoadingHealth] = useState(false);
  const [loadingAudit, setLoadingAudit] = useState(false);
  const [error, setError] = useState("");

  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

  async function fetchSystemHealth() {
    setLoadingHealth(true);
    setError("");

    try {
      const response = await fetch(`${apiBaseUrl}/system/health`);

      if (!response.ok) {
        throw new Error(`System health error: ${response.status}`);
      }

      const data = await response.json();
      setSystemHealth(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to fetch system health."
      );
    } finally {
      setLoadingHealth(false);
    }
  }

  async function fetchAuditEvents() {
    setLoadingAudit(true);
    setError("");

    try {
      const response = await fetch(
        `${apiBaseUrl}/audit/events/${conversationId}?limit=50`
      );

      if (!response.ok) {
        throw new Error(`Audit fetch error: ${response.status}`);
      }

      const data = await response.json();
      setAuditEvents(data.events || []);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to fetch audit events."
      );
    } finally {
      setLoadingAudit(false);
    }
  }

  return (
    <div className="space-y-8">
      <PageHeader
        title="Admin & Observability"
        description="Monitor service health, security status, audit logs, request tracing, and operational readiness."
      />

      {error && (
        <div className="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <section className="rounded-3xl bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-bold">System Health</h2>
              <p className="text-sm text-slate-500">
                Live status from /system/health
              </p>
            </div>

            <button
              onClick={fetchSystemHealth}
              disabled={loadingHealth}
              className="rounded-2xl bg-[#061a3a] px-4 py-2 text-sm font-bold text-white hover:bg-[#0b2855] disabled:bg-slate-400"
            >
              {loadingHealth ? "Checking..." : "Refresh"}
            </button>
          </div>

          <div className="mt-6 rounded-2xl border border-slate-200 bg-slate-50 p-5">
            <p className="text-xs font-bold uppercase text-slate-500">
              Overall Status
            </p>
            <p className="mt-2 text-3xl font-bold capitalize text-slate-950">
              {systemHealth?.overall_status || "Not checked"}
            </p>
          </div>

          <div className="mt-5 max-h-[520px] space-y-3 overflow-y-auto pr-2">
            <HealthRow
              label="Backend API"
              status={systemHealth?.components?.backend?.status || "-"}
              message={systemHealth?.components?.backend?.message || "-"}
            />
            <HealthRow
              label="Azure SQL"
              status={systemHealth?.components?.azure_sql?.status || "-"}
              message={systemHealth?.components?.azure_sql?.message || "-"}
            />
            <HealthRow
              label="Azure AI Search"
              status={systemHealth?.components?.azure_ai_search?.status || "-"}
              message={
                systemHealth?.components?.azure_ai_search?.message || "-"
              }
            />
            <HealthRow
              label="Cosmos Memory / Audit"
              status={
                systemHealth?.components?.cosmos_memory_audit?.status || "-"
              }
              message={
                systemHealth?.components?.cosmos_memory_audit?.message || "-"
              }
            />
            <HealthRow
              label="API Key Security"
              status={
                systemHealth?.components?.api_key_security?.status || "-"
              }
              message={
                systemHealth?.components?.api_key_security?.message || "-"
              }
            />
            <HealthRow
              label="Audit Logging"
              status={systemHealth?.components?.audit_logging?.status || "-"}
              message={systemHealth?.components?.audit_logging?.message || "-"}
            />
          </div>
        </section>

        <section className="rounded-3xl bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold">Security & Governance</h2>
          <p className="text-sm text-slate-500">
            Demo controls implemented for enterprise readiness.
          </p>

          <div className="mt-6 max-h-[520px] space-y-4 overflow-y-auto pr-2">
            <GovernanceCard
              title="API Key Protection"
              status="Active"
              description="Protected copilot endpoint requires x-copilot-api-key header."
            />
            <GovernanceCard
              title="Request Tracing"
              status="Active"
              description="Each request receives x-request-id and stores it in audit logs."
            />
            <GovernanceCard
              title="Audit Logging"
              status="Active"
              description="Successful and failed copilot requests are stored in Cosmos DB."
            />
            <GovernanceCard
              title="Human Review Flag"
              status="Active"
              description="Low-confidence or failed workflows can be marked for review."
            />
            <GovernanceCard
              title="Cosmos Memory"
              status="Active"
              description="Conversation state is stored for follow-up questions."
            />
            <GovernanceCard
              title="Azure Entra ID / RBAC"
              status="Future"
              description="Production upgrade path for role-based enterprise authentication."
            />
          </div>
        </section>
      </div>

      <section className="rounded-3xl bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <h2 className="text-xl font-bold">Audit Event Explorer</h2>
            <p className="text-sm text-slate-500">
              Search Cosmos audit records by conversation ID.
            </p>
          </div>

          <div className="flex flex-1 gap-3 md:max-w-xl">
            <input
              className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-cyan-500"
              value={conversationId}
              onChange={(event) => setConversationId(event.target.value)}
              placeholder="Enter conversation ID"
            />

            <button
              onClick={fetchAuditEvents}
              disabled={loadingAudit}
              className="rounded-2xl bg-[#061a3a] px-5 py-3 text-sm font-bold text-white hover:bg-[#0b2855] disabled:bg-slate-400"
            >
              {loadingAudit ? "Loading..." : "Search"}
            </button>
          </div>
        </div>

        <div className="mt-6 max-h-[430px] overflow-auto rounded-2xl border border-slate-200">
          <table className="w-full min-w-[980px] text-left text-sm">
            <thead className="sticky top-0 z-10 bg-slate-50 text-slate-500">
              <tr>
                <th className="px-4 py-3">Time</th>
                <th className="px-4 py-3">Request ID</th>
                <th className="px-4 py-3">Route</th>
                <th className="px-4 py-3">Record ID</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Confidence</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-200">
              {auditEvents.length === 0 && (
                <tr>
                  <td
                    colSpan={6}
                    className="px-4 py-8 text-center text-slate-500"
                  >
                    No audit events loaded yet.
                  </td>
                </tr>
              )}

              {auditEvents.map((event) => (
                <tr key={event.id}>
                  <td className="max-w-[250px] px-4 py-4 text-xs text-slate-500">
                    <span className="line-clamp-2 break-words">
                      {event.created_at || "-"}
                    </span>
                  </td>
                  <td className="max-w-[220px] px-4 py-4 font-semibold">
                    <span className="line-clamp-2 break-words">
                      {event.request_id || "-"}
                    </span>
                  </td>
                  <td className="px-4 py-4">{event.route || "-"}</td>
                  <td className="px-4 py-4">{event.record_id || "-"}</td>
                  <td className="px-4 py-4">
                    <span
                      className={`rounded-full px-2 py-1 text-xs font-bold ${
                        event.status === "success"
                          ? "bg-green-100 text-green-700"
                          : "bg-red-100 text-red-700"
                      }`}
                    >
                      {event.status || "-"}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    {event.confidence_score !== null
                      ? `${event.confidence_score} (${event.confidence_label})`
                      : "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <p className="mt-3 text-xs text-slate-500">
          Showing 6 visible rows. Additional records are available by scrolling.
        </p>
      </section>
    </div>
  );
}

function PlaceholderPage({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="space-y-8">
      <PageHeader title={title} description={description} />

      <section className="rounded-3xl bg-white p-10 shadow-sm">
        <div className="flex min-h-[420px] flex-col items-center justify-center rounded-3xl border border-dashed border-slate-300 bg-slate-50 text-center">
          <BriefcaseBusiness className="h-12 w-12 text-slate-400" />

          <h2 className="mt-4 text-xl font-bold">{title}</h2>

          <p className="mt-2 max-w-xl text-sm text-slate-500">{description}</p>
        </div>
      </section>
    </div>
  );
}

function PageHeader({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div>
      <h1 className="text-3xl font-bold tracking-tight text-slate-950">
        {title}
      </h1>

      <p className="mt-2 text-sm text-slate-600">{description}</p>
    </div>
  );
}

function KpiCard({
  title,
  value,
  change,
  tone,
}: {
  title: string;
  value: string;
  change: string;
  tone: "success" | "warning" | "danger" | "info";
}) {
  const toneClass =
    tone === "success"
      ? "bg-green-50 text-green-700"
      : tone === "warning"
      ? "bg-orange-50 text-orange-700"
      : tone === "danger"
      ? "bg-red-50 text-red-700"
      : "bg-blue-50 text-blue-700";

  return (
    <section className="rounded-3xl bg-white p-5 shadow-sm">
      <p className="text-sm font-semibold text-slate-600">{title}</p>

      <div className="mt-4 flex items-end justify-between">
        <p className="text-3xl font-bold">{value}</p>

        <span
          className={`rounded-full px-3 py-1 text-xs font-bold ${toneClass}`}
        >
          {change}
        </span>
      </div>
    </section>
  );
}

function CapabilityItem({
  icon,
  title,
  description,
}: {
  icon: ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="flex gap-4">
      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-cyan-50 text-cyan-700">
        {icon}
      </div>

      <div>
        <p className="font-semibold">{title}</p>
        <p className="mt-1 text-sm text-slate-500">{description}</p>
      </div>
    </div>
  );
}

function QueueRow({
  queue,
  items,
  risk,
  status,
  owner,
}: {
  queue: string;
  items: string;
  risk: string;
  status: string;
  owner: string;
}) {
  return (
    <tr>
      <td className="px-4 py-4 font-semibold">{queue}</td>
      <td className="px-4 py-4 text-blue-700">{items}</td>
      <td className="px-4 py-4 text-red-600">{risk}</td>
      <td className="px-4 py-4">{status}</td>
      <td className="px-4 py-4">{owner}</td>
    </tr>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between border-b border-slate-100 pb-2">
      <span className="text-slate-500">{label}</span>

      <span className="max-w-[220px] truncate text-right font-semibold text-slate-900">
        {value}
      </span>
    </div>
  );
}

function StatusItem({ label, status }: { label: string; status: string }) {
  return (
    <div className="flex items-center justify-between rounded-2xl bg-slate-50 px-3 py-2">
      <span>{label}</span>

      <span className="rounded-full bg-blue-100 px-2 py-1 text-xs font-bold text-blue-700">
        {status}
      </span>
    </div>
  );
}

function HealthRow({
  label,
  status,
  message,
}: {
  label: string;
  status: string;
  message: string;
}) {
  const statusClass =
    status === "healthy" || status === "active"
      ? "bg-green-100 text-green-700"
      : status === "warning" || status === "future"
      ? "bg-orange-100 text-orange-700"
      : status === "-"
      ? "bg-slate-100 text-slate-600"
      : "bg-red-100 text-red-700";

  return (
    <div className="rounded-2xl border border-slate-200 p-4">
      <div className="flex items-center justify-between gap-3">
        <p className="font-semibold">{label}</p>
        <span
          className={`rounded-full px-2 py-1 text-xs font-bold capitalize ${statusClass}`}
        >
          {status}
        </span>
      </div>
      <p className="mt-2 line-clamp-3 text-xs text-slate-500">{message}</p>
    </div>
  );
}

function GovernanceCard({
  title,
  status,
  description,
}: {
  title: string;
  status: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
      <div className="flex items-center justify-between gap-3">
        <p className="font-semibold">{title}</p>
        <span className="rounded-full bg-blue-100 px-2 py-1 text-xs font-bold text-blue-700">
          {status}
        </span>
      </div>
      <p className="mt-2 line-clamp-3 text-sm text-slate-500">{description}</p>
    </div>
  );
}
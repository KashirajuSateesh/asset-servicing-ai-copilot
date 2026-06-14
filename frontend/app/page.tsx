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
  PanelLeftClose,
  PanelLeftOpen,
} from "lucide-react";
import { useEffect, useState, type ReactNode } from "react";

type PageKey =
  | "dashboard"
  | "copilot"
  | "documents"
  | "exceptions"
  | "reconciliation"
  | "cases"
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

type AnalyticsSummaryResponse = {
  operations: {
    settlement_exceptions: number;
    reconciliation_breaks: number;
    case_tickets: number;
    corporate_actions: number;
    trade_status: number;
    custody_accounts: number;
  };
  ai_usage: {
    total_requests: number;
    successful_requests: number;
    failed_requests: number;
    human_review_required: number;
    average_confidence: number | null;
    route_counts: Record<string, number>;
  };
  retrieval: {
    uploaded_pdfs: number;
    indexed_chunks: number;
    retrieval_mode: string;
    embedding_model: string;
  };
  summary: {
    total_operational_records: number;
    system_readiness: string;
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
    key: "admin",
    label: "Admin",
    icon: <Settings className="h-5 w-5" />,
  },
];

export default function Home() {
  const [activePage, setActivePage] = useState<PageKey>("dashboard");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <main className="h-screen overflow-hidden bg-slate-100 text-slate-950">
      <div className="flex h-screen overflow-hidden">
        <Sidebar
          activePage={activePage}
          setActivePage={setActivePage}
          collapsed={sidebarCollapsed}
          setCollapsed={setSidebarCollapsed}
        />

        <div className="flex h-screen min-w-0 flex-1 flex-col overflow-hidden">
          <Topbar />

          <section className="flex-1 overflow-y-auto p-5 lg:p-6">
            {activePage === "dashboard" && <DashboardPage />}
            {activePage === "copilot" && <CopilotPage />}
            {activePage === "documents" && <DocumentsPage />}
            {activePage === "exceptions" && <ExceptionsPage />}
            {activePage === "reconciliation" && <ReconciliationPage />}
            {activePage === "cases" && <CasesPage />}
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
  collapsed,
  setCollapsed,
}: {
  activePage: PageKey;
  setActivePage: (page: PageKey) => void;
  collapsed: boolean;
  setCollapsed: (value: boolean) => void;
}) {
  return (
    <aside
      className={`sticky top-0 flex h-screen shrink-0 flex-col overflow-hidden bg-[#061a3a] text-white transition-all duration-300 ${
        collapsed ? "w-24" : "w-72"
      }`}
    >
      <div className="flex h-20 shrink-0 items-center justify-between border-b border-white/10 px-5">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-400/20 text-cyan-300">
            <Bot className="h-6 w-6" />
          </div>

          {!collapsed && (
            <div>
              <h1 className="text-lg font-bold">Asset Servicing</h1>
              <p className="text-xs text-slate-300">AI Copilot</p>
            </div>
          )}
        </div>

        <button
          onClick={() => setCollapsed(!collapsed)}
          className="rounded-xl p-2 text-slate-300 hover:bg-white/10 hover:text-white"
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? (
            <PanelLeftOpen className="h-5 w-5" />
          ) : (
            <PanelLeftClose className="h-5 w-5" />
          )}
        </button>
      </div>

      <nav className="flex-1 space-y-2 overflow-y-auto px-4 py-6 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {navigationItems.map((item) => {
          const isActive = activePage === item.key;

          return (
            <button
              key={item.key}
              onClick={() => setActivePage(item.key)}
              className={`flex w-full items-center rounded-2xl py-3 text-sm font-semibold transition ${
                collapsed ? "justify-center px-0" : "gap-3 px-4 text-left"
              } ${
                isActive
                  ? "bg-cyan-500/25 text-white shadow"
                  : "text-slate-300 hover:bg-white/10 hover:text-white"
              }`}
            >
              {item.icon}
              {!collapsed && item.label}
            </button>
          );
        })}
      </nav>

      <div className="shrink-0 border-t border-white/10 p-5 text-xs text-slate-300">
        <div className={`flex items-center gap-2 ${collapsed ? "justify-center" : ""}`}>
          <RefreshCcw className="h-4 w-4" />
          {!collapsed && <span>Data refreshed from live services</span>}
        </div>

        {!collapsed && (
          <p className="mt-3 text-slate-400">
            Azure SQL • AI Search • Cosmos DB
          </p>
        )}
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
  const [analytics, setAnalytics] = useState<AnalyticsSummaryResponse | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

  async function fetchDashboardData() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${apiBaseUrl}/analytics/summary`);

      if (!response.ok) {
        throw new Error(`Dashboard analytics error: ${response.status}`);
      }

      const data = await response.json();
      setAnalytics(data);
      sessionStorage.setItem("dashboardAnalytics", JSON.stringify(data));
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load dashboard data."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const cachedData = sessionStorage.getItem("dashboardAnalytics");

    if (cachedData) {
      setAnalytics(JSON.parse(cachedData));
      return;
    }

    fetchDashboardData();
  }, []);

  const operations = analytics?.operations;
  const aiUsage = analytics?.ai_usage;
  const retrieval = analytics?.retrieval;
  const summary = analytics?.summary;

  const avgConfidence =
    aiUsage?.average_confidence !== null &&
    aiUsage?.average_confidence !== undefined
      ? `${Math.round(aiUsage.average_confidence * 100)}%`
      : "-";

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <PageHeader
          title="Operations Overview"
          description="Enterprise AI copilot for custody, settlement, reconciliation, cases, policy search, and operational guidance."
        />

        <button
          onClick={fetchDashboardData}
          disabled={loading}
          className="w-fit rounded-2xl bg-[#061a3a] px-5 py-3 text-sm font-bold text-white hover:bg-[#0b2855] disabled:bg-slate-400"
        >
          {loading ? "Loading..." : "Refresh Dashboard"}
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {!analytics && (
        <section className="rounded-2xl bg-white p-5 shadow-sm">
          <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-8 text-center text-sm text-slate-500">
            Click Refresh Dashboard to load real metrics from Azure SQL, Cosmos
            audit logs, and Azure AI Search summary.
          </div>
        </section>
      )}

      {analytics && (
        <>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
            <KpiCard
              title="Settlement Exceptions"
              value={String(operations?.settlement_exceptions ?? "-")}
              change="SQL"
              tone="warning"
            />
            <KpiCard
              title="Reconciliation Breaks"
              value={String(operations?.reconciliation_breaks ?? "-")}
              change="SQL"
              tone="info"
            />
            <KpiCard
              title="Case Tickets"
              value={String(operations?.case_tickets ?? "-")}
              change="SQL"
              tone="success"
            />
            <KpiCard
              title="AI Requests"
              value={String(aiUsage?.total_requests ?? "-")}
              change={avgConfidence}
              tone="success"
            />
            <KpiCard
              title="Indexed Chunks"
              value={String(retrieval?.indexed_chunks ?? "-")}
              change={retrieval?.retrieval_mode || "-"}
              tone="info"
            />
          </div>

          <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
            <section className="rounded-2xl bg-white p-5 shadow-sm">
              <h2 className="text-lg font-bold">Operational Data Summary</h2>
              <p className="text-sm text-slate-500">
                Real table counts from Azure SQL operational data.
              </p>

              <div className="mt-5 grid gap-3">
                <TrendBar
                  label="Trade Status Records"
                  value={calculatePercent(
                    operations?.trade_status || 0,
                    summary?.total_operational_records || 1
                  )}
                  count={String(operations?.trade_status ?? "-")}
                  tone="info"
                />
                <TrendBar
                  label="Reconciliation Breaks"
                  value={calculatePercent(
                    operations?.reconciliation_breaks || 0,
                    summary?.total_operational_records || 1
                  )}
                  count={String(operations?.reconciliation_breaks ?? "-")}
                  tone="warning"
                />
                <TrendBar
                  label="Case Tickets"
                  value={calculatePercent(
                    operations?.case_tickets || 0,
                    summary?.total_operational_records || 1
                  )}
                  count={String(operations?.case_tickets ?? "-")}
                  tone="success"
                />
                <TrendBar
                  label="Custody Accounts"
                  value={calculatePercent(
                    operations?.custody_accounts || 0,
                    summary?.total_operational_records || 1
                  )}
                  count={String(operations?.custody_accounts ?? "-")}
                  tone="info"
                />
                <TrendBar
                  label="Settlement Exceptions"
                  value={calculatePercent(
                    operations?.settlement_exceptions || 0,
                    summary?.total_operational_records || 1
                  )}
                  count={String(operations?.settlement_exceptions ?? "-")}
                  tone="warning"
                />
                <TrendBar
                  label="Corporate Actions"
                  value={calculatePercent(
                    operations?.corporate_actions || 0,
                    summary?.total_operational_records || 1
                  )}
                  count={String(operations?.corporate_actions ?? "-")}
                  tone="info"
                />
              </div>
            </section>

            <section className="rounded-2xl bg-white p-5 shadow-sm">
              <h2 className="text-lg font-bold">What this project does</h2>
              <p className="text-sm text-slate-500">
                Core capabilities implemented in this AI copilot.
              </p>

              <div className="mt-5 space-y-4">
                <CapabilityItem
                  icon={<FileText className="h-5 w-5" />}
                  title="Citation-backed policy answers"
                  description="Answers are generated from indexed PDF policy chunks."
                />
                <CapabilityItem
                  icon={<Database className="h-5 w-5" />}
                  title="Live operational lookup"
                  description="Azure SQL provides trade, exception, break, and case records."
                />
                <CapabilityItem
                  icon={<Bot className="h-5 w-5" />}
                  title="Orchestrated AI workflow"
                  description="The orchestrator routes between SQL + RAG and document-only RAG."
                />
                <CapabilityItem
                  icon={<Gauge className="h-5 w-5" />}
                  title="Observability and governance"
                  description="Audit events, request IDs, confidence, and human review flags are tracked."
                />
              </div>
            </section>
          </div>

          <div className="grid gap-6 xl:grid-cols-3">
            <section className="rounded-2xl bg-white p-5 shadow-sm">
              <h2 className="text-lg font-bold">AI Usage</h2>
              <div className="mt-5 space-y-3">
                <InfoRow
                  label="Total requests"
                  value={String(aiUsage?.total_requests ?? "-")}
                />
                <InfoRow
                  label="Successful requests"
                  value={String(aiUsage?.successful_requests ?? "-")}
                />
                <InfoRow
                  label="Failed requests"
                  value={String(aiUsage?.failed_requests ?? "-")}
                />
                <InfoRow
                  label="Human review required"
                  value={String(aiUsage?.human_review_required ?? "-")}
                />
              </div>
            </section>

            <section className="rounded-2xl bg-white p-5 shadow-sm">
              <h2 className="text-lg font-bold">Retrieval Readiness</h2>
              <div className="mt-5 space-y-3">
                <InfoRow
                  label="Uploaded PDFs"
                  value={String(retrieval?.uploaded_pdfs ?? "-")}
                />
                <InfoRow
                  label="Indexed chunks"
                  value={String(retrieval?.indexed_chunks ?? "-")}
                />
                <InfoRow
                  label="Retrieval mode"
                  value={retrieval?.retrieval_mode || "-"}
                />
                <InfoRow
                  label="Embedding model"
                  value={retrieval?.embedding_model || "-"}
                />
              </div>
            </section>

            <section className="rounded-2xl bg-white p-5 shadow-sm">
              <h2 className="text-lg font-bold">System Readiness</h2>
              <div className="mt-5 space-y-3">
                <InfoRow
                  label="Total operational records"
                  value={String(summary?.total_operational_records ?? "-")}
                />
                <InfoRow
                  label="System status"
                  value={summary?.system_readiness || "-"}
                />
                <InfoRow label="Security" value="API key active" />
                <InfoRow label="Audit logging" value="Active" />
              </div>
            </section>
          </div>
        </>
      )}
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
        <section className="rounded-2xl bg-white p-5 shadow-sm">
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
          <section className="rounded-2xl bg-white p-5 shadow-sm">
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

          <section className="rounded-2xl bg-white p-5 shadow-sm">
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
  const [documents, setDocuments] = useState<Record<string, unknown>[]>([]);
  const [documentSearch, setDocumentSearch] = useState("");
  const [loadingDocs, setLoadingDocs] = useState(false);
  const [documentsError, setDocumentsError] = useState("");

  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

  async function fetchDocuments() {
    setLoadingDocs(true);
    setDocumentsError("");

    try {
      const response = await fetch(`${apiBaseUrl}/documents/blobs/raw-pdfs`);

      if (!response.ok) {
        throw new Error(`Documents API error: ${response.status}`);
      }

      const data = await response.json();

      /*
        Backend may return:
        1. an array directly
        2. an object like { documents: [...] }
        3. an object like { blobs: [...] }
        4. an object like { files: [...] }

        This code safely converts all formats into an array.
      */
      const documentsArray = Array.isArray(data)
        ? data
        : Array.isArray(data.documents)
          ? data.documents
          : Array.isArray(data.blobs)
            ? data.blobs
            : Array.isArray(data.files)
              ? data.files
              : [];

      setDocuments(documentsArray);
      sessionStorage.setItem(
        "documentsInventory",
        JSON.stringify(documentsArray)
      );
    } catch (err) {
      setDocumentsError(
        err instanceof Error ? err.message : "Failed to load documents."
      );
      setDocuments([]);
    } finally {
      setLoadingDocs(false);
    }
  }

  useEffect(() => {
    const cachedData = sessionStorage.getItem("documentsInventory");

    if (cachedData) {
      try {
        const parsedData = JSON.parse(cachedData);

        const documentsArray = Array.isArray(parsedData)
          ? parsedData
          : Array.isArray(parsedData.documents)
            ? parsedData.documents
            : [];

        setDocuments(documentsArray);
        return;
      } catch {
        sessionStorage.removeItem("documentsInventory");
      }
    }

    fetchDocuments();
  }, []);

  const safeDocuments = Array.isArray(documents) ? documents : [];

  const filteredDocuments = safeDocuments.filter((doc, index) => {
    const name = getDocumentName(doc, index);
    const domain = detectDocumentDomain(name);

    const search = documentSearch.toLowerCase();

    return (
      name.toLowerCase().includes(search) ||
      domain.toLowerCase().includes(search)
    );
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <PageHeader
          title="Documents"
          description="Knowledge base inventory for policy PDFs, SOPs, SLA documents, and indexed retrieval sources."
        />

        <button
          onClick={fetchDocuments}
          disabled={loadingDocs}
          className="w-fit rounded-2xl bg-[#061a3a] px-5 py-3 text-sm font-bold text-white hover:bg-[#0b2855] disabled:bg-slate-400"
        >
          {loadingDocs ? "Loading..." : "Refresh Documents"}
        </button>
      </div>

      {documentsError && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {documentsError}
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <KpiCard
          title="Uploaded PDFs"
          value={String(safeDocuments.length)}
          change="Azure Blob"
          tone="info"
        />
        <KpiCard
          title="Indexed Chunks"
          value="75"
          change="Azure AI Search"
          tone="success"
        />
        <KpiCard
          title="Retrieval Mode"
          value="Hybrid"
          change="Vector + keyword"
          tone="success"
        />
        <KpiCard
          title="Embedding Model"
          value="OpenAI"
          change="text-embedding-3-small"
          tone="info"
        />
      </div>

      <section className="rounded-2xl bg-white p-5 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h2 className="text-lg font-bold">Knowledge Base Inventory</h2>
            <p className="text-sm text-slate-500">
              Documents load automatically. Use Refresh Documents to reload from
              Azure Blob.
            </p>
          </div>

          <div className="relative w-full lg:w-80">
            <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
            <input
              value={documentSearch}
              onChange={(event) => setDocumentSearch(event.target.value)}
              placeholder="Search documents..."
              className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2 pl-9 pr-3 text-sm outline-none focus:border-blue-400 focus:bg-white"
            />
          </div>
        </div>

        <div className="mt-5 max-h-[360px] overflow-auto rounded-2xl border border-slate-200">
          <table className="w-full text-left text-sm">
            <thead className="sticky top-0 z-10 bg-slate-50 text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">Document Name</th>
                <th className="px-4 py-3">Domain</th>
                <th className="px-4 py-3">Source</th>
                <th className="px-4 py-3">Index Status</th>
                <th className="px-4 py-3">RAG Ready</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-100">
              {filteredDocuments.length === 0 && (
                <tr>
                  <td
                    colSpan={5}
                    className="px-4 py-8 text-center text-sm text-slate-500"
                  >
                    {loadingDocs
                      ? "Loading documents..."
                      : "No documents found."}
                  </td>
                </tr>
              )}

              {filteredDocuments.map((doc, index) => {
                const name = getDocumentName(doc, index);
                const domain = detectDocumentDomain(name);

                return (
                  <tr key={`${name}-${index}`} className="hover:bg-slate-50">
                    <td className="px-4 py-3 font-semibold text-slate-800">
                      {name}
                    </td>
                    <td className="px-4 py-3 text-slate-600">{domain}</td>
                    <td className="px-4 py-3 text-slate-600">Azure Blob</td>
                    <td className="px-4 py-3">
                      <span className="rounded-full bg-green-50 px-3 py-1 text-xs font-bold text-green-700">
                        Indexed
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-bold text-blue-700">
                        Ready
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-4">
        <GovernanceCard
          title="Blob Storage Source"
          status="raw-pdfs container"
          description="Original source documents are stored in Azure Blob Storage."
        />
        <GovernanceCard
          title="OCR / Parsing"
          status="Document Intelligence"
          description="PDF content is extracted with layout-aware parsing before chunking."
        />
        <GovernanceCard
          title="Metadata Tagging"
          status="Domain + document type"
          description="Chunks are tagged for policy, SLA, reconciliation, custody, and exception workflows."
        />
        <GovernanceCard
          title="Vector Index"
          status="Azure AI Search"
          description="Hybrid search supports citation-backed answers in the copilot."
        />
      </div>
    </div>
  );
}

function ExceptionsPage() {
  const [exceptionId, setExceptionId] = useState("EXC-000001");
  const [exceptionContext, setExceptionContext] = useState<any | null>(null);
  const [guidanceResult, setGuidanceResult] = useState<any | null>(null);
  const [loadingContext, setLoadingContext] = useState(false);
  const [loadingGuidance, setLoadingGuidance] = useState(false);
  const [error, setError] = useState("");

  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

  async function loadExceptionContext() {
    setLoadingContext(true);
    setError("");
    setGuidanceResult(null);

    try {
      const response = await fetch(
        `${apiBaseUrl}/operations/context/${exceptionId}`
      );

      if (!response.ok) {
        throw new Error(`Exception lookup error: ${response.status}`);
      }

      const data = await response.json();
      setExceptionContext(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load exception details."
      );
    } finally {
      setLoadingContext(false);
    }
  }

  async function getAiGuidance() {
    setLoadingGuidance(true);
    setError("");

    try {
      const response = await fetch(
        `${apiBaseUrl}/operations/guidance/${exceptionId}?top_k=8`
      );

      if (!response.ok) {
        throw new Error(`Guidance error: ${response.status}`);
      }

      const data = await response.json();
      setGuidanceResult(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to generate AI guidance."
      );
    } finally {
      setLoadingGuidance(false);
    }
  }

  const recordData = exceptionContext?.record_data || {};
  const guidance = guidanceResult?.policy_guidance || {};

  return (
    <div className="space-y-8">
      <PageHeader
        title="Settlement Exceptions"
        description="Search exception records, review operational context, and generate AI-guided next actions."
      />

      {error && (
        <div className="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      <section className="rounded-2xl bg-white p-5 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h2 className="text-xl font-bold">Exception Lookup</h2>
            <p className="text-sm text-slate-500">
              Search settlement exception records from Azure SQL.
            </p>
          </div>

          <div className="flex w-full flex-col gap-3 sm:flex-row lg:max-w-xl">
            <input
              className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-cyan-500"
              value={exceptionId}
              placeholder="Example: EXC-000001"
              onChange={(event) => setExceptionId(event.target.value)}
            />

            <button
              onClick={loadExceptionContext}
              disabled={loadingContext || !exceptionId.trim()}
              className="rounded-2xl bg-[#061a3a] px-5 py-3 text-sm font-bold text-white hover:bg-[#0b2855] disabled:bg-slate-400"
            >
              {loadingContext ? "Loading..." : "Load Exception"}
            </button>
          </div>
        </div>

        <div className="mt-6 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
          <KpiCard
            title="Open Exceptions"
            value="140"
            change="SQL"
            tone="warning"
          />
          <KpiCard
            title="High Exposure"
            value="$3.7M"
            change="Selected"
            tone="danger"
          />
          <KpiCard
            title="Current Status"
            value={recordData.exception_status || "-"}
            change="Live"
            tone="info"
          />
          <KpiCard
            title="AI Guidance"
            value={guidanceResult ? "Ready" : "Pending"}
            change={guidanceResult ? "Generated" : "Not Run"}
            tone={guidanceResult ? "success" : "warning"}
          />
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <section className="rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="text-xl font-bold">Exception Details</h2>
          <p className="text-sm text-slate-500">
            Operational context retrieved from structured SQL records.
          </p>

          {!exceptionContext && (
            <div className="mt-6 rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-8 text-center text-sm text-slate-500">
              Load an exception to view details.
            </div>
          )}

          {exceptionContext && (
            <div className="mt-6 space-y-4">
              <div className="rounded-2xl border border-blue-100 bg-blue-50 p-4">
                <p className="text-xs font-bold uppercase text-blue-600">
                  Context Summary
                </p>
                <p className="mt-2 text-sm font-semibold text-blue-950">
                  {exceptionContext.context_summary}
                </p>
              </div>

              <div className="grid gap-3 text-sm">
                <InfoRow
                  label="Exception ID"
                  value={recordData.exception_id || exceptionId}
                />
                <InfoRow label="Trade ID" value={recordData.trade_id || "-"} />
                <InfoRow
                  label="Account ID"
                  value={recordData.account_id || "-"}
                />
                <InfoRow
                  label="Reason"
                  value={recordData.exception_reason || "-"}
                />
                <InfoRow label="Severity" value={recordData.severity || "-"} />
                <InfoRow
                  label="Status"
                  value={recordData.exception_status || "-"}
                />
                <InfoRow
                  label="Assigned Team"
                  value={recordData.assigned_team || "-"}
                />
                <InfoRow
                  label="SLA Due Date"
                  value={recordData.sla_due_date || "-"}
                />
                <InfoRow
                  label="Exposure USD"
                  value={
                    recordData.estimated_exposure_usd
                      ? `$${Number(
                          recordData.estimated_exposure_usd
                        ).toLocaleString()}`
                      : "-"
                  }
                />
              </div>

              <button
                onClick={getAiGuidance}
                disabled={loadingGuidance}
                className="mt-3 w-full rounded-2xl bg-[#061a3a] px-5 py-3 text-sm font-bold text-white hover:bg-[#0b2855] disabled:bg-slate-400"
              >
                {loadingGuidance ? "Generating..." : "Get AI Guidance"}
              </button>
            </div>
          )}
        </section>

        <section className="rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="text-xl font-bold">AI Recommendation</h2>
          <p className="text-sm text-slate-500">
            Combines SQL context with settlement policy documents.
          </p>

          {!guidanceResult && (
            <div className="mt-6 rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-8 text-center text-sm text-slate-500">
              Load an exception and click Get AI Guidance.
            </div>
          )}

          {guidanceResult && (
            <div className="mt-6 rounded-3xl border border-slate-200 bg-slate-50 p-6">
              <div className="flex items-center justify-between gap-3">
                <h3 className="text-lg font-bold">Recommended Next Action</h3>

                <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-bold text-blue-700">
                  {guidance.confidence_label || "unknown"}
                </span>
              </div>

              <p className="mt-4 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                {guidance.answer}
              </p>

              <div className="mt-5 grid gap-3 text-sm">
                <InfoRow
                  label="Business Domain"
                  value={guidanceResult.business_domain || "-"}
                />
                <InfoRow
                  label="Confidence"
                  value={
                    guidance.confidence_score !== undefined
                      ? `${guidance.confidence_score} (${guidance.confidence_label})`
                      : "-"
                  }
                />
                <InfoRow
                  label="Human Review"
                  value={String(guidance.human_review_required ?? "-")}
                />
                <InfoRow
                  label="Record Type"
                  value={guidanceResult.record_type || "-"}
                />
              </div>

              {guidance.citations?.length > 0 && (
                <div className="mt-6">
                  <h4 className="text-sm font-bold">Policy Citations</h4>

                  <div className="mt-3 max-h-[360px] space-y-3 overflow-y-auto pr-2">
                    {guidance.citations.map((citation: Citation) => (
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
      </div>
    </div>
  );
}

function ReconciliationPage() {
  const [breakId, setBreakId] = useState("BRK-0000001");
  const [breakContext, setBreakContext] = useState<any | null>(null);
  const [guidanceResult, setGuidanceResult] = useState<any | null>(null);
  const [loadingContext, setLoadingContext] = useState(false);
  const [loadingGuidance, setLoadingGuidance] = useState(false);
  const [error, setError] = useState("");

  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

  async function loadBreakContext() {
    setLoadingContext(true);
    setError("");
    setGuidanceResult(null);

    try {
      const response = await fetch(`${apiBaseUrl}/operations/context/${breakId}`);

      if (!response.ok) {
        throw new Error(`Reconciliation break lookup error: ${response.status}`);
      }

      const data = await response.json();
      setBreakContext(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load reconciliation break details."
      );
    } finally {
      setLoadingContext(false);
    }
  }

  async function getAiGuidance() {
    setLoadingGuidance(true);
    setError("");

    try {
      const response = await fetch(
        `${apiBaseUrl}/operations/guidance/${breakId}?top_k=8`
      );

      if (!response.ok) {
        throw new Error(`Guidance error: ${response.status}`);
      }

      const data = await response.json();
      setGuidanceResult(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to generate AI guidance."
      );
    } finally {
      setLoadingGuidance(false);
    }
  }

  const recordData = breakContext?.record_data || {};
  const guidance = guidanceResult?.policy_guidance || {};

  return (
    <div className="space-y-8">
      <PageHeader
        title="Reconciliation Breaks"
        description="Review reconciliation breaks, inspect SQL context, and generate AI-guided resolution recommendations."
      />

      {error && (
        <div className="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      <section className="rounded-2xl bg-white p-5 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h2 className="text-xl font-bold">Break Lookup</h2>
            <p className="text-sm text-slate-500">
              Search reconciliation break records from Azure SQL.
            </p>
          </div>

          <div className="flex w-full flex-col gap-3 sm:flex-row lg:max-w-xl">
            <input
              className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-cyan-500"
              value={breakId}
              placeholder="Example: BRK-0000001"
              onChange={(event) => setBreakId(event.target.value)}
            />

            <button
              onClick={loadBreakContext}
              disabled={loadingContext || !breakId.trim()}
              className="rounded-2xl bg-[#061a3a] px-5 py-3 text-sm font-bold text-white hover:bg-[#0b2855] disabled:bg-slate-400"
            >
              {loadingContext ? "Loading..." : "Load Break"}
            </button>
          </div>
        </div>

        <div className="mt-6 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
          <KpiCard
            title="Open Breaks"
            value="400"
            change="SQL"
            tone="warning"
          />
          <KpiCard
            title="Selected Break"
            value={recordData.break_id || breakId}
            change="Live"
            tone="info"
          />
          <KpiCard
            title="Break Status"
            value={recordData.break_status || recordData.status || "-"}
            change="Current"
            tone="warning"
          />
          <KpiCard
            title="AI Guidance"
            value={guidanceResult ? "Ready" : "Pending"}
            change={guidanceResult ? "Generated" : "Not Run"}
            tone={guidanceResult ? "success" : "warning"}
          />
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <section className="rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="text-xl font-bold">Break Details</h2>
          <p className="text-sm text-slate-500">
            Operational context retrieved from structured reconciliation records.
          </p>

          {!breakContext && (
            <div className="mt-6 rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-8 text-center text-sm text-slate-500">
              Load a reconciliation break to view details.
            </div>
          )}

          {breakContext && (
            <div className="mt-6 space-y-4">
              <div className="rounded-2xl border border-blue-100 bg-blue-50 p-4">
                <p className="text-xs font-bold uppercase text-blue-600">
                  Context Summary
                </p>
                <p className="mt-2 text-sm font-semibold text-blue-950">
                  {breakContext.context_summary}
                </p>
              </div>

              <div className="grid gap-3 text-sm">
                <InfoRow
                  label="Break ID"
                  value={recordData.break_id || breakId}
                />
                <InfoRow
                  label="Account ID"
                  value={recordData.account_id || "-"}
                />
                <InfoRow
                  label="Trade ID"
                  value={recordData.trade_id || "-"}
                />
                <InfoRow
                  label="Break Type"
                  value={recordData.break_type || recordData.recon_type || "-"}
                />
                <InfoRow
                  label="Source System"
                  value={recordData.source_system || "-"}
                />
                <InfoRow
                  label="Status"
                  value={recordData.break_status || recordData.status || "-"}
                />
                <InfoRow
                  label="Assigned Team"
                  value={recordData.assigned_team || "-"}
                />
                <InfoRow
                  label="Detected Date"
                  value={recordData.detected_date || "-"}
                />
                <InfoRow
                  label="Aging Days"
                  value={String(recordData.aging_days ?? "-")}
                />
                <InfoRow
                  label="Amount Difference"
                  value={
                    recordData.amount_difference_usd
                      ? `$${Number(
                          recordData.amount_difference_usd
                        ).toLocaleString()}`
                      : recordData.difference_amount
                      ? `$${Number(recordData.difference_amount).toLocaleString()}`
                      : "-"
                  }
                />
              </div>

              <button
                onClick={getAiGuidance}
                disabled={loadingGuidance}
                className="mt-3 w-full rounded-2xl bg-[#061a3a] px-5 py-3 text-sm font-bold text-white hover:bg-[#0b2855] disabled:bg-slate-400"
              >
                {loadingGuidance ? "Generating..." : "Get AI Guidance"}
              </button>
            </div>
          )}
        </section>

        <section className="rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="text-xl font-bold">AI Resolution Recommendation</h2>
          <p className="text-sm text-slate-500">
            Combines reconciliation break context with policy and SOP documents.
          </p>

          {!guidanceResult && (
            <div className="mt-6 rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-8 text-center text-sm text-slate-500">
              Load a break and click Get AI Guidance.
            </div>
          )}

          {guidanceResult && (
            <div className="mt-6 rounded-3xl border border-slate-200 bg-slate-50 p-6">
              <div className="flex items-center justify-between gap-3">
                <h3 className="text-lg font-bold">Recommended Resolution</h3>

                <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-bold text-blue-700">
                  {guidance.confidence_label || "unknown"}
                </span>
              </div>

              <p className="mt-4 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                {guidance.answer}
              </p>

              <div className="mt-5 grid gap-3 text-sm">
                <InfoRow
                  label="Business Domain"
                  value={guidanceResult.business_domain || "-"}
                />
                <InfoRow
                  label="Confidence"
                  value={
                    guidance.confidence_score !== undefined
                      ? `${guidance.confidence_score} (${guidance.confidence_label})`
                      : "-"
                  }
                />
                <InfoRow
                  label="Human Review"
                  value={String(guidance.human_review_required ?? "-")}
                />
                <InfoRow
                  label="Record Type"
                  value={guidanceResult.record_type || "-"}
                />
              </div>

              {guidance.citations?.length > 0 && (
                <div className="mt-6">
                  <h4 className="text-sm font-bold">Policy Citations</h4>

                  <div className="mt-3 max-h-[360px] space-y-3 overflow-y-auto pr-2">
                    {guidance.citations.map((citation: Citation) => (
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
      </div>
    </div>
  );
}

function CasesPage() {
  const [caseId, setCaseId] = useState("CASE-0000001");
  const [caseContext, setCaseContext] = useState<any | null>(null);
  const [guidanceResult, setGuidanceResult] = useState<any | null>(null);
  const [loadingContext, setLoadingContext] = useState(false);
  const [loadingGuidance, setLoadingGuidance] = useState(false);
  const [error, setError] = useState("");

  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

  async function loadCaseContext() {
    setLoadingContext(true);
    setError("");
    setGuidanceResult(null);

    try {
      const response = await fetch(`${apiBaseUrl}/operations/context/${caseId}`);

      if (!response.ok) {
        throw new Error(`Case lookup error: ${response.status}`);
      }

      const data = await response.json();
      setCaseContext(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load case.");
    } finally {
      setLoadingContext(false);
    }
  }

  async function getAiGuidance() {
    setLoadingGuidance(true);
    setError("");

    try {
      const response = await fetch(
        `${apiBaseUrl}/operations/guidance/${caseId}?top_k=8`
      );

      if (!response.ok) {
        throw new Error(`Guidance error: ${response.status}`);
      }

      const data = await response.json();
      setGuidanceResult(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to generate case guidance."
      );
    } finally {
      setLoadingGuidance(false);
    }
  }

  const recordData = caseContext?.record_data || {};
  const guidance = guidanceResult?.policy_guidance || {};

  return (
    <div className="space-y-6">
      <PageHeader
        title="Cases"
        description="Search operational cases, review case context, and generate AI-assisted next actions."
      />

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <section className="rounded-2xl bg-white p-5 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h2 className="text-lg font-bold">Case Lookup</h2>
            <p className="text-sm text-slate-500">
              Search case records from Azure SQL.
            </p>
          </div>

          <div className="flex w-full flex-col gap-3 sm:flex-row lg:max-w-xl">
            <input
              className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-cyan-500"
              value={caseId}
              placeholder="Example: CASE-0000001"
              onChange={(event) => setCaseId(event.target.value)}
            />

            <button
              onClick={loadCaseContext}
              disabled={loadingContext || !caseId.trim()}
              className="rounded-2xl bg-[#061a3a] px-5 py-3 text-sm font-bold text-white hover:bg-[#0b2855] disabled:bg-slate-400"
            >
              {loadingContext ? "Loading..." : "Load Case"}
            </button>
          </div>
        </div>

        <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <KpiCard title="Total Cases" value="290" change="SQL" tone="info" />
          <KpiCard
            title="Selected Case"
            value={recordData.case_id || caseId}
            change="Live"
            tone="info"
          />
          <KpiCard
            title="Case Status"
            value={recordData.case_status || recordData.status || "-"}
            change="Current"
            tone="warning"
          />
          <KpiCard
            title="AI Guidance"
            value={guidanceResult ? "Ready" : "Pending"}
            change={guidanceResult ? "Generated" : "Not Run"}
            tone={guidanceResult ? "success" : "warning"}
          />
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <section className="rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="text-lg font-bold">Case Details</h2>
          <p className="text-sm text-slate-500">
            Operational case context retrieved from structured records.
          </p>

          {!caseContext && (
            <div className="mt-5 rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-8 text-center text-sm text-slate-500">
              Load a case to view details.
            </div>
          )}

          {caseContext && (
            <div className="mt-5 space-y-4">
              <div className="rounded-2xl border border-blue-100 bg-blue-50 p-4">
                <p className="text-xs font-bold uppercase text-blue-600">
                  Context Summary
                </p>
                <p className="mt-2 text-sm font-semibold text-blue-950">
                  {caseContext.context_summary}
                </p>
              </div>

              <div className="grid gap-3 text-sm">
                <InfoRow label="Case ID" value={recordData.case_id || caseId} />
                <InfoRow
                  label="Linked Trade"
                  value={recordData.trade_id || "-"}
                />
                <InfoRow
                  label="Linked Exception"
                  value={recordData.exception_id || "-"}
                />
                <InfoRow
                  label="Linked Break"
                  value={recordData.break_id || "-"}
                />
                <InfoRow
                  label="Case Type"
                  value={recordData.case_type || "-"}
                />
                <InfoRow
                  label="Priority"
                  value={recordData.priority || "-"}
                />
                <InfoRow
                  label="Status"
                  value={recordData.case_status || recordData.status || "-"}
                />
                <InfoRow
                  label="Assigned Team"
                  value={recordData.assigned_team || "-"}
                />
                <InfoRow
                  label="Created Date"
                  value={recordData.created_date || "-"}
                />
                <InfoRow
                  label="Resolution Notes"
                  value={recordData.resolution_notes || recordData.notes || "-"}
                />
              </div>

              <button
                onClick={getAiGuidance}
                disabled={loadingGuidance}
                className="mt-3 w-full rounded-2xl bg-[#061a3a] px-5 py-3 text-sm font-bold text-white hover:bg-[#0b2855] disabled:bg-slate-400"
              >
                {loadingGuidance ? "Generating..." : "Get AI Guidance"}
              </button>
            </div>
          )}
        </section>

        <section className="rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="text-lg font-bold">AI Case Guidance</h2>
          <p className="text-sm text-slate-500">
            Uses case context and available policy knowledge to recommend next steps.
          </p>

          {!guidanceResult && (
            <div className="mt-5 rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-8 text-center text-sm text-slate-500">
              Load a case and click Get AI Guidance.
            </div>
          )}

          {guidanceResult && (
            <div className="mt-5 rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="flex items-center justify-between gap-3">
                <h3 className="text-base font-bold">Recommended Action</h3>

                <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-bold text-blue-700">
                  {guidance.confidence_label || "unknown"}
                </span>
              </div>

              <p className="mt-4 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                {guidance.answer}
              </p>

              <div className="mt-5 grid gap-3 text-sm">
                <InfoRow
                  label="Business Domain"
                  value={guidanceResult.business_domain || "-"}
                />
                <InfoRow
                  label="Confidence"
                  value={
                    guidance.confidence_score !== undefined
                      ? `${guidance.confidence_score} (${guidance.confidence_label})`
                      : "-"
                  }
                />
                <InfoRow
                  label="Human Review"
                  value={String(guidance.human_review_required ?? "-")}
                />
                <InfoRow
                  label="Record Type"
                  value={guidanceResult.record_type || "-"}
                />
              </div>

              {guidance.citations?.length > 0 && (
                <div className="mt-5">
                  <h4 className="text-sm font-bold">Policy Citations</h4>

                  <div className="mt-3 max-h-[340px] space-y-3 overflow-y-auto pr-2">
                    {guidance.citations.map((citation: Citation) => (
                      <div
                        key={`${citation.document_name}-${citation.chunk_index}-${citation.source_number}`}
                        className="rounded-xl border border-slate-200 bg-white p-3 text-xs"
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
      </div>
    </div>
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
        <section className="rounded-2xl bg-white p-5 shadow-sm">
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

        <section className="rounded-2xl bg-white p-5 shadow-sm">
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

      <section className="rounded-2xl bg-white p-5 shadow-sm">
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
                <th className="px-3 py-2">Time</th>
                <th className="px-3 py-2">Request ID</th>
                <th className="px-3 py-2">Route</th>
                <th className="px-3 py-2">Record ID</th>
                <th className="px-3 py-2">Status</th>
                <th className="px-3 py-2">Confidence</th>
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
                  <td className="px-3 py-3">{event.route || "-"}</td>
                  <td className="px-3 py-3">{event.record_id || "-"}</td>
                  <td className="px-3 py-3">
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
                  <td className="px-3 py-3">
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
      <h1 className="text-2xl font-bold tracking-tight text-slate-950">
        {title}
      </h1>

      <p className="mt-1 text-sm text-slate-600">{description}</p>
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
    <section className="rounded-2xl bg-white p-4 shadow-sm">
      <p className="truncate text-xs font-semibold uppercase tracking-wide text-slate-500">
        {title}
      </p>

      <div className="mt-3 flex items-end justify-between gap-3">
        <p className="truncate text-2xl font-bold leading-none text-slate-950">
          {value}
        </p>

        <span
          className={`shrink-0 rounded-full px-2 py-1 text-[11px] font-bold ${toneClass}`}
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
      <td className="px-3 py-3">{status}</td>
      <td className="px-3 py-3">{owner}</td>
    </tr>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3 border-b border-slate-100 pb-2">
      <span className="text-xs font-medium text-slate-500">{label}</span>

      <span className="max-w-[220px] truncate text-right text-xs font-semibold text-slate-900">
        {value}
      </span>
    </div>
  );
}

function StatusItem({ label, status }: { label: string; status: string }) {
  return (
    <div className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-2">
      <span className="text-xs font-medium text-slate-600">{label}</span>

      <span className="rounded-full bg-blue-100 px-2 py-1 text-[11px] font-bold text-blue-700">
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
    <div className="rounded-xl border border-slate-200 p-3">
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm font-semibold">{label}</p>
        <span
          className={`rounded-full px-2 py-1 text-[11px] font-bold capitalize ${statusClass}`}
        >
          {status}
        </span>
      </div>
      <p className="mt-1 line-clamp-2 text-xs text-slate-500">{message}</p>
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
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm font-semibold">{title}</p>
        <span className="rounded-full bg-blue-100 px-2 py-1 text-[11px] font-bold text-blue-700">
          {status}
        </span>
      </div>
      <p className="mt-1 line-clamp-2 text-xs text-slate-500">{description}</p>
    </div>
  );
}


function TrendBar({
  label,
  value,
  count,
  tone,
}: {
  label: string;
  value: string;
  count: string;
  tone: "success" | "warning" | "danger" | "info";
}) {
  const widthValue = Number(value.replace("%", ""));

  const barClass =
    tone === "success"
      ? "bg-green-500"
      : tone === "warning"
      ? "bg-orange-500"
      : tone === "danger"
      ? "bg-red-500"
      : "bg-blue-500";

  return (
    <div className="rounded-xl border border-slate-200 p-3">
      <div className="flex items-center justify-between text-sm">
        <p className="font-semibold">{label}</p>
        <p className="text-xs font-bold text-slate-500">{count}</p>
      </div>

      <div className="mt-3 h-2 rounded-full bg-slate-100">
        <div
          className={`h-2 rounded-full ${barClass}`}
          style={{ width: `${widthValue}%` }}
        />
      </div>
    </div>
  );
}

function RiskItem({
  queue,
  risk,
  count,
}: {
  queue: string;
  risk: string;
  count: string;
}) {
  const riskClass =
    risk === "High"
      ? "bg-red-100 text-red-700"
      : risk === "Medium"
      ? "bg-orange-100 text-orange-700"
      : "bg-green-100 text-green-700";

  return (
    <div className="flex items-center justify-between rounded-xl border border-slate-200 p-3">
      <div>
        <p className="text-sm font-semibold">{queue}</p>
        <p className="text-xs text-slate-500">{count} items at risk</p>
      </div>

      <span className={`rounded-full px-2 py-1 text-xs font-bold ${riskClass}`}>
        {risk}
      </span>
    </div>
  );
}

function calculatePercent(value: number, total: number) {
  if (!total || total <= 0) {
    return "0%";
  }

  return `${Math.max(5, Math.round((value / total) * 100))}%`;
}

function getDocumentName(doc: Record<string, unknown>, index: number) {
  const possibleName =
    doc.name ||
    doc.filename ||
    doc.file_name ||
    doc.blob_name ||
    doc.path ||
    doc.url;

  if (typeof possibleName === "string" && possibleName.trim().length > 0) {
    return possibleName.split("/").pop() || possibleName;
  }

  return `Document ${index + 1}`;
}

function detectDocumentDomain(documentName: string) {
  const name = documentName.toLowerCase();

  if (name.includes("recon") || name.includes("break")) {
    return "Reconciliation";
  }

  if (name.includes("settlement") || name.includes("exception")) {
    return "Settlement";
  }

  if (name.includes("custody") || name.includes("account")) {
    return "Custody";
  }

  if (name.includes("sla")) {
    return "SLA";
  }

  if (name.includes("policy")) {
    return "Policy";
  }

  if (name.includes("case")) {
    return "Case Management";
  }

  return "Operations";
}
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
import { useState } from "react";

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
  icon: React.ReactNode;
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
    <main className="min-h-screen bg-slate-100 text-slate-950">
      <div className="flex min-h-screen">
        <Sidebar activePage={activePage} setActivePage={setActivePage} />

        <div className="flex min-h-screen flex-1 flex-col">
          <Topbar />

          <section className="flex-1 overflow-y-auto p-8">
            {activePage === "dashboard" && <DashboardPage />}
            {activePage === "copilot" && <CopilotPagePlaceholder />}
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
    <aside className="flex w-72 flex-col bg-[#061a3a] text-white">
      <div className="flex h-20 items-center gap-3 border-b border-white/10 px-6">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-400/20 text-cyan-300">
          <Bot className="h-6 w-6" />
        </div>
        <div>
          <h1 className="text-lg font-bold">Asset Servicing</h1>
          <p className="text-xs text-slate-300">AI Copilot</p>
        </div>
      </div>

      <nav className="flex-1 space-y-2 px-4 py-6">
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

      <div className="border-t border-white/10 p-5 text-xs text-slate-300">
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
    <header className="flex h-20 items-center justify-between border-b border-slate-200 bg-white px-8 shadow-sm">
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
        <KpiCard title="SLA Risk Cases" value="48" change="+14.3%" tone="danger" />
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

function CopilotPagePlaceholder() {
  return (
    <PlaceholderPage
      title="Ask Copilot"
      description="Next step: move your working copilot chat, citations, audit logs, request ID, and system health panels into this page."
    />
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
  return (
    <PlaceholderPage
      title="Admin & Observability"
      description="System health, audit logs, security status, request tracing, and configuration checks."
    />
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
        <span className={`rounded-full px-3 py-1 text-xs font-bold ${toneClass}`}>
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
  icon: React.ReactNode;
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
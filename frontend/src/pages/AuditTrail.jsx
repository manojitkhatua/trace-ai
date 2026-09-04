import { useMemo, useState } from "react";
import { Search, X, ArrowUpDown, ListChecks, ShieldCheck, ShieldAlert, ShieldX, Eye } from "lucide-react";
import { AppLayout } from "../components/layout/AppLayout";
import { Card } from "../components/ui/Card";
import { StatCard } from "../components/ui/StatCard";
import { DecisionBadge, RiskLevelBadge } from "../components/ui/Badge";
import { PipelineTrack } from "../components/ui/Pipeline";
import { ShapEvidenceCard } from "../components/trace/ShapEvidence";
import { AnomalyIntelligenceCard } from "../components/trace/AnomalyIntelligence";
import { EntityIntelligenceCard } from "../components/trace/EntityIntelligence";
import { RiskCompositionCard } from "../components/trace/RiskComposition";
import { GeminiExplanationCard } from "../components/trace/GeminiExplanation";
import { RiskGauge } from "../components/ui/RiskGauge";
import { useTrace } from "../context/TraceContext";
import { formatCurrency, formatDateTime, truncateMiddle } from "../utils/format";

const COLUMNS = [
  { key: "id", label: "Transaction" },
  { key: "timestamp", label: "Time" },
  { key: "fraudProbability", label: "Fraud Probability" },
  { key: "anomalyScore", label: "Anomaly" },
  { key: "entityRisk", label: "Entity Risk" },
  { key: "riskScore", label: "Risk Score" },
  { key: "decision", label: "Decision" },
];

export default function AuditTrail() {
  const { history } = useTrace();
  const [search, setSearch] = useState("");
  const [decisionFilter, setDecisionFilter] = useState("ALL");
  const [levelFilter, setLevelFilter] = useState("ALL");
  const [sortKey, setSortKey] = useState("timestamp");
  const [sortDir, setSortDir] = useState("desc");
  const [selected, setSelected] = useState(null);

  const stats = useMemo(() => {
    const total = history.length;
    const allowed = history.filter((r) => r.decision === "ALLOW").length;
    const review = history.filter((r) => r.decision === "REVIEW").length;
    const blocked = history.filter((r) => r.decision === "BLOCK").length;
    return { total, allowed, review, blocked };
  }, [history]);

  const filtered = useMemo(() => {
    let rows = [...history];
    if (search.trim()) {
      const q = search.trim().toLowerCase();
      rows = rows.filter(
        (r) =>
          r.id.toLowerCase().includes(q) ||
          (r.input?.cardId || "").toLowerCase().includes(q) ||
          String(r.input?.amount || "").includes(q)
      );
    }
    if (decisionFilter !== "ALL") rows = rows.filter((r) => r.decision === decisionFilter);
    if (levelFilter !== "ALL") rows = rows.filter((r) => r.riskLevel === levelFilter);

    rows.sort((a, b) => {
      let av, bv;
      switch (sortKey) {
        case "timestamp":
          av = new Date(a.timestamp).getTime();
          bv = new Date(b.timestamp).getTime();
          break;
        case "fraudProbability":
          av = a.scores.fraudProbability;
          bv = b.scores.fraudProbability;
          break;
        case "anomalyScore":
          av = a.scores.anomalyScore;
          bv = b.scores.anomalyScore;
          break;
        case "entityRisk":
          av = a.scores.entityRisk;
          bv = b.scores.entityRisk;
          break;
        case "riskScore":
          av = a.scores.riskScore;
          bv = b.scores.riskScore;
          break;
        case "decision":
          av = a.decision;
          bv = b.decision;
          break;
        default:
          av = a.id;
          bv = b.id;
      }
      if (av < bv) return sortDir === "asc" ? -1 : 1;
      if (av > bv) return sortDir === "asc" ? 1 : -1;
      return 0;
    });
    return rows;
  }, [history, search, decisionFilter, levelFilter, sortKey, sortDir]);

  function toggleSort(key) {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("desc");
    }
  }

  return (
    <AppLayout title="Audit Trail" subtitle="Searchable, filterable history of every TRACE decision">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Total" value={stats.total} icon={ListChecks} tone="default" />
        <StatCard label="Allowed" value={stats.allowed} icon={ShieldCheck} tone="green" />
        <StatCard label="Review" value={stats.review} icon={ShieldAlert} tone="amber" />
        <StatCard label="Blocked" value={stats.blocked} icon={ShieldX} tone="red" />
      </div>

      <Card className="mt-6" padded={false}>
        <div className="flex flex-col gap-3 border-b border-[#E5E7EB] p-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="relative w-full sm:max-w-xs">
            <Search size={15} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[#98A2B3]" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search transaction, card, amount…"
              className="w-full rounded-lg border border-[#D0D5DD] bg-white py-2 pl-9 pr-3 text-sm focus:border-[#2563EB] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/15"
            />
          </div>
          <div className="flex flex-wrap gap-2">
            <select
              value={decisionFilter}
              onChange={(e) => setDecisionFilter(e.target.value)}
              className="rounded-lg border border-[#D0D5DD] bg-white px-3 py-2 text-xs font-medium text-[#344054] focus:border-[#2563EB] focus:outline-none"
            >
              <option value="ALL">All Decisions</option>
              <option value="ALLOW">Allow</option>
              <option value="REVIEW">Review</option>
              <option value="BLOCK">Block</option>
            </select>
            <select
              value={levelFilter}
              onChange={(e) => setLevelFilter(e.target.value)}
              className="rounded-lg border border-[#D0D5DD] bg-white px-3 py-2 text-xs font-medium text-[#344054] focus:border-[#2563EB] focus:outline-none"
            >
              <option value="ALL">All Risk Levels</option>
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[820px] text-left text-sm">
            <thead>
              <tr className="border-b border-[#E5E7EB] text-xs uppercase tracking-wide text-[#98A2B3]">
                {COLUMNS.map((c) => (
                  <th key={c.key} className="px-4 py-2.5 font-medium">
                    <button className="inline-flex items-center gap-1 hover:text-[#344054]" onClick={() => toggleSort(c.key)}>
                      {c.label}
                      <ArrowUpDown size={11} />
                    </button>
                  </th>
                ))}
                <th className="px-4 py-2.5 font-medium">Details</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={8} className="px-4 py-10 text-center text-sm text-[#98A2B3]">
                    No transactions match your filters.
                  </td>
                </tr>
              )}
              {filtered.map((r) => (
                <tr key={r.id} className="border-b border-[#F2F4F7] last:border-0 hover:bg-[#F7F9FC]">
                  <td className="px-4 py-3 font-mono text-xs text-[#344054]">{truncateMiddle(r.id, 18)}</td>
                  <td className="px-4 py-3 text-xs text-[#667085]">{formatDateTime(r.timestamp)}</td>
                  <td className="px-4 py-3 text-[#344054]">{(r.scores.fraudProbability * 100).toFixed(2)}%</td>
                  <td className="px-4 py-3 text-[#344054]">{(r.scores.anomalyScore * 100).toFixed(2)}%</td>
                  <td className="px-4 py-3 text-[#344054]">{(r.scores.entityRisk * 100).toFixed(2)}%</td>
                  <td className="px-4 py-3 font-semibold text-[#111827]">{r.scores.riskScore.toFixed(2)}</td>
                  <td className="px-4 py-3">
                    <DecisionBadge decision={r.decision} />
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => setSelected(r)}
                      className="inline-flex items-center gap-1 rounded-md border border-[#D0D5DD] px-2 py-1 text-xs font-medium text-[#344054] hover:bg-white"
                    >
                      <Eye size={13} /> View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="border-t border-[#E5E7EB] px-4 py-3 text-xs text-[#98A2B3]">
          Showing {filtered.length} of {history.length} transactions
        </div>
      </Card>

      {selected && <DetailDrawer record={selected} onClose={() => setSelected(null)} />}
    </AppLayout>
  );
}

function DetailDrawer({ record, onClose }) {
  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-black/30" onClick={onClose} />
      <div className="relative flex h-full w-full max-w-xl flex-col overflow-y-auto bg-[#F7F9FC] shadow-2xl">
        <div className="sticky top-0 z-10 flex items-center justify-between border-b border-[#E5E7EB] bg-white px-5 py-4">
          <div>
            <p className="font-mono text-sm font-semibold text-[#111827]">{record.id}</p>
            <p className="text-xs text-[#667085]">{formatDateTime(record.timestamp)}</p>
          </div>
          <button onClick={onClose} className="text-[#667085] hover:text-[#111827]">
            <X size={20} />
          </button>
        </div>

        <div className="space-y-5 p-5">
          <div className="rounded-xl border border-[#E5E7EB] bg-white p-4">
            <PipelineTrack activeKey="audit" completedKeys={["transaction", "ml", "shap", "anomaly", "entity", "risk", "decision", "gemini"]} />
          </div>

          <Card>
            <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-between">
              <div className="flex items-center gap-3">
                <DecisionBadge decision={record.decision} size="lg" />
                <RiskLevelBadge level={record.riskLevel} />
              </div>
              <RiskGauge score={record.scores.riskScore} level={record.riskLevel} size={140} />
            </div>
          </Card>

          <Card>
            <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-[#667085]">Transaction Details</p>
            <dl className="grid grid-cols-2 gap-3 text-sm">
              <Detail label="Amount" value={formatCurrency(record.input?.amount)} />
              <Detail label="Card" value={record.input?.cardId} />
              <Detail label="Network / Type" value={`${record.input?.cardNetwork || "—"} / ${record.input?.cardType || "—"}`} />
              <Detail label="Product Category" value={record.input?.productCategory} />
              <Detail label="Device" value={`${record.input?.deviceType || "—"} · ${record.input?.deviceInfo || "n/a"}`} />
              <Detail
                label="Billing"
                value={[record.input?.billingAddress?.city, record.input?.billingAddress?.country].filter(Boolean).join(", ") || "—"}
              />
            </dl>
          </Card>

          <Card>
            <ShapEvidenceCard factors={record.ml.shapFactors} />
          </Card>
          <Card>
            <AnomalyIntelligenceCard anomaly={record.anomaly} />
          </Card>
          <Card>
            <EntityIntelligenceCard entity={record.entity} />
          </Card>
          <Card>
            <RiskCompositionCard composition={record.riskComposition} />
          </Card>
          <GeminiExplanationCard gemini={record.gemini} />
        </div>
      </div>
    </div>
  );
}

function Detail({ label, value }) {
  return (
    <div>
      <dt className="text-[11px] uppercase tracking-wide text-[#98A2B3]">{label}</dt>
      <dd className="font-medium text-[#344054]">{value || "—"}</dd>
    </div>
  );
}

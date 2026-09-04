import { useMemo, useState } from "react";
import { Users2, CheckCircle2, Flag, ShieldOff, Info } from "lucide-react";
import { AppLayout } from "../components/layout/AppLayout";
import { Card, CardHeader } from "../components/ui/Card";
import { PipelineTrack } from "../components/ui/Pipeline";
import { DecisionBadge, RiskLevelBadge } from "../components/ui/Badge";
import { GeminiExplanationCard } from "../components/trace/GeminiExplanation";
import { EmptyState } from "../components/ui/States";
import { useTrace } from "../context/TraceContext";
import { formatCurrency, formatDateTime, truncateMiddle } from "../utils/format";

export default function Investigation() {
  const { history, current } = useTrace();
  const [selectedId, setSelectedId] = useState(null);
  const [action, setAction] = useState(null);
  const [comment, setComment] = useState("");

  const selected = useMemo(
    () => history.find((r) => r.id === selectedId) || current || history[0] || null,
    [history, selectedId, current]
  );

  if (!selected) {
    return (
      <AppLayout title="Investigation" subtitle="Analyst workspace for TRACE decisions">
        <EmptyState icon={Users2} title="No transactions available" description="Analyze a transaction first." />
      </AppLayout>
    );
  }

  const topFactors = (selected.ml.shapFactors || []).slice(0, 4);
  const evidence = [
    ...(selected.anomaly?.signals || []).map((s) => s.detail),
    ...(selected.entity?.notes || []),
  ].filter(Boolean);

  function recordAction(type) {
    setAction(type);
  }

  return (
    <AppLayout title="Investigation" subtitle="Analyst workspace + Gemini explanation">
      <div className="mb-5 rounded-xl border border-[#E5E7EB] bg-white p-5">
        <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-sm font-semibold text-[#111827]">TRACE makes the decision. Gemini explains it.</h2>
            <p className="mt-1 text-xs text-[#667085]">
              The decision below was produced entirely by the ML, anomaly, entity, and risk engine pipeline. Gemini
              only adds a human-readable narrative afterward.
            </p>
          </div>
          <select
            value={selected.id}
            onChange={(e) => setSelectedId(e.target.value)}
            className="w-full rounded-lg border border-[#D0D5DD] bg-white px-3 py-2 text-sm text-[#344054] focus:border-[#2563EB] focus:outline-none sm:w-72"
          >
            {history.map((r) => (
              <option key={r.id} value={r.id}>
                {truncateMiddle(r.id, 20)} · {formatCurrency(r.input?.amount)}
              </option>
            ))}
          </select>
        </div>
        <div className="mt-5 border-t border-[#F2F4F7] pt-5">
          <PipelineTrack activeKey="audit" completedKeys={["transaction", "ml", "shap", "anomaly", "entity", "risk", "decision", "gemini"]} />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
        <div className="space-y-5">
          <Card>
            <CardHeader title="Case Summary" subtitle={`${selected.id} · ${formatDateTime(selected.timestamp)}`} />
            <div className="mb-4 flex flex-wrap items-center gap-2">
              <DecisionBadge decision={selected.decision} size="lg" />
              <RiskLevelBadge level={selected.riskLevel} />
              <span className="text-sm font-semibold text-[#111827]">Score {selected.scores.riskScore.toFixed(1)}/100</span>
            </div>

            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-[#667085]">Key Factors</p>
            <ul className="mb-4 space-y-1.5">
              {topFactors.map((f, i) => (
                <li key={i} className="text-sm text-[#344054]">
                  • {f.feature} <span className="text-xs text-[#98A2B3]">({f.direction === "increases" ? "increases risk" : "decreases risk"})</span>
                </li>
              ))}
            </ul>

            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-[#667085]">Supporting Evidence</p>
            <ul className="mb-4 space-y-1.5">
              {evidence.slice(0, 5).map((e, i) => (
                <li key={i} className="text-sm text-[#667085]">
                  • {e}
                </li>
              ))}
            </ul>

            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-[#667085]">Transaction Details</p>
            <dl className="grid grid-cols-2 gap-3 text-sm">
              <Detail label="Amount" value={formatCurrency(selected.input?.amount)} />
              <Detail label="Card" value={selected.input?.cardId} />
              <Detail label="Network / Type" value={`${selected.input?.cardNetwork || "—"} / ${selected.input?.cardType || "—"}`} />
              <Detail label="Product Category" value={selected.input?.productCategory} />
              <Detail label="Device" value={`${selected.input?.deviceType || "—"} · ${selected.input?.deviceInfo || "n/a"}`} />
              <Detail
                label="Billing"
                value={[selected.input?.billingAddress?.city, selected.input?.billingAddress?.country].filter(Boolean).join(", ") || "—"}
              />
            </dl>
          </Card>

          <Card>
            <CardHeader title="Analyst Action" subtitle="Record your review decision for this case" />
            <div className="mb-4 flex flex-wrap gap-2">
              <ActionButton icon={CheckCircle2} label="Confirm Decision" tone="green" active={action === "confirm"} onClick={() => recordAction("confirm")} />
              <ActionButton icon={Flag} label="Escalate for Manual Review" tone="amber" active={action === "escalate"} onClick={() => recordAction("escalate")} />
              <ActionButton icon={ShieldOff} label="Mark as False Positive" tone="red" active={action === "false_positive"} onClick={() => recordAction("false_positive")} />
            </div>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Add analyst notes for the audit record (optional)…"
              rows={3}
              className="w-full rounded-lg border border-[#D0D5DD] px-3 py-2 text-sm text-[#111827] placeholder:text-[#98A2B3] focus:border-[#2563EB] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/15"
            />
            {action && (
              <div className="mt-3 flex items-start gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-emerald-700">
                <Info size={14} className="mt-0.5 shrink-0" />
                Action "{actionLabel(action)}" recorded locally for this session and attached to the case notes.
              </div>
            )}
          </Card>
        </div>

        <GeminiExplanationCard gemini={selected.gemini} />
      </div>
    </AppLayout>
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

function ActionButton({ icon: Icon, label, tone, active, onClick }) {
  const toneMap = {
    green: active ? "border-emerald-300 bg-emerald-50 text-emerald-700" : "border-[#D0D5DD] text-[#344054]",
    amber: active ? "border-amber-300 bg-amber-50 text-amber-700" : "border-[#D0D5DD] text-[#344054]",
    red: active ? "border-rose-300 bg-rose-50 text-rose-700" : "border-[#D0D5DD] text-[#344054]",
  };
  return (
    <button
      type="button"
      onClick={onClick}
      className={`inline-flex items-center gap-1.5 rounded-lg border px-3 py-2 text-xs font-semibold transition-colors hover:bg-[#F7F9FC] ${toneMap[tone]}`}
    >
      <Icon size={14} />
      {label}
    </button>
  );
}

function actionLabel(action) {
  return { confirm: "Confirm Decision", escalate: "Escalate for Manual Review", false_positive: "Mark as False Positive" }[action];
}

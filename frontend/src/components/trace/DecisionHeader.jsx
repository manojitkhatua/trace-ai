import { ShieldCheck, ShieldAlert, ShieldX } from "lucide-react";
import { RiskGauge } from "../ui/RiskGauge";
import { DecisionBadge, RiskLevelBadge, ModeBadge } from "../ui/Badge";
import { MetricBar } from "../ui/MetricBar";
import { InfoTooltip } from "../ui/InfoTooltip";
import { formatDateTime } from "../../utils/format";
import { styleForDecision } from "../../utils/risk";

const DECISION_ICON = { ALLOW: ShieldCheck, REVIEW: ShieldAlert, BLOCK: ShieldX };

const DECISION_COPY = {
  ALLOW: "Transaction cleared automatically. No analyst action required.",
  REVIEW: "Routed to manual review before funds are released.",
  BLOCK: "Transaction stopped automatically due to high fraud risk.",
};

export function DecisionHeader({ result, compact = false }) {
  if (!result) return null;
  const { scores, riskLevel, decision, timestamp, id, source } = result;
  const Icon = DECISION_ICON[decision] || ShieldCheck;
  const style = styleForDecision(decision);

  return (
    <div className="space-y-5">
      <div className={`flex flex-col gap-4 rounded-xl border p-5 sm:flex-row sm:items-center sm:justify-between ${style.bg} ${style.border}`}>
        <div className="flex items-start gap-3">
          <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-white ${style.text}`}>
            <Icon size={22} />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <DecisionBadge decision={decision} size="lg" />
              <RiskLevelBadge level={riskLevel} />
            </div>
            <p className={`mt-1.5 text-sm font-medium ${style.text}`}>{DECISION_COPY[decision]}</p>
            <p className="mt-1 text-xs text-[#667085]">
              {id} • {formatDateTime(timestamp)}
            </p>
          </div>
        </div>
        {!compact && <ModeBadge mode={source === "live" ? "live" : "demo"} />}
      </div>

      <div className="grid grid-cols-1 gap-5 rounded-xl border border-[#E5E7EB] bg-white p-5 sm:grid-cols-[auto_1fr]">
        <div className="flex justify-center sm:justify-start">
          <RiskGauge score={scores.riskScore} level={riskLevel} size={compact ? 180 : 220} />
        </div>
        <div className="flex flex-col justify-center gap-4">
          <MetricBar
            label="Fraud Probability"
            value={scores.fraudProbability * 100}
            color="#2563EB"
            tooltip="Likelihood of fraud predicted directly by the ML model."
          />
          <MetricBar
            label="Anomaly Score"
            value={scores.anomalyScore * 100}
            color="#7C3AED"
            tooltip="How unusual this transaction is versus typical behavior patterns."
          />
          <MetricBar
            label="Entity Risk"
            value={scores.entityRisk * 100}
            color="#DB2777"
            tooltip="Combined risk of the card, device, address, and network relationships involved."
          />
        </div>
      </div>
    </div>
  );
}

export function InlineMetric({ label, value, tooltip }) {
  return (
    <div className="rounded-lg border border-[#E5E7EB] bg-[#F7F9FC] px-3 py-2">
      <div className="flex items-center gap-1 text-[11px] font-medium text-[#667085]">
        {label} {tooltip && <InfoTooltip text={tooltip} />}
      </div>
      <div className="text-sm font-semibold text-[#111827]">{value}</div>
    </div>
  );
}



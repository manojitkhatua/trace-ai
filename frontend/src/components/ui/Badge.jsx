import { styleForDecision, styleForLevel, DECISION_LABELS, RISK_LEVEL_LABELS } from "../../utils/risk";

export function DecisionBadge({ decision, size = "md" }) {
  const style = styleForDecision(decision);
  const sizing = size === "lg" ? "px-3.5 py-1.5 text-sm" : "px-2.5 py-1 text-xs";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border font-semibold ${sizing} ${style.bg} ${style.text} ${style.border}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${style.dot}`} />
      {DECISION_LABELS[decision] || decision || "Unknown"}
    </span>
  );
}

export function RiskLevelBadge({ level, size = "md" }) {
  const style = styleForLevel(level);
  const sizing = size === "lg" ? "px-3.5 py-1.5 text-sm" : "px-2.5 py-1 text-xs";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border font-semibold ${sizing} ${style.bg} ${style.text} ${style.border}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${style.dot}`} />
      {RISK_LEVEL_LABELS[level] || level || "Unknown"}
    </span>
  );
}

export function SeverityBadge({ severity }) {
  const map = {
    low: "bg-emerald-50 text-emerald-700 border-emerald-200",
    medium: "bg-amber-50 text-amber-700 border-amber-200",
    high: "bg-rose-50 text-rose-700 border-rose-200",
  };
  const cls = map[severity] || map.medium;
  return (
    <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-medium uppercase tracking-wide ${cls}`}>
      {severity || "medium"}
    </span>
  );
}

export function ModeBadge({ mode }) {
  if (mode === "live") {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">
        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-500" />
        LIVE
      </span>
    );
  }
  if (mode === "demo") {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-200 bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-700">
        <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
        DEMO MODE
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-gray-200 bg-gray-50 px-2.5 py-1 text-xs font-semibold text-gray-500">
      <span className="h-1.5 w-1.5 rounded-full bg-gray-400" />
      NOT CONNECTED
    </span>
  );
}

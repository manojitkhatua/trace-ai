import { Radar } from "lucide-react";
import { CardHeader } from "../ui/Card";
import { SeverityBadge } from "../ui/Badge";
import { MetricBar } from "../ui/MetricBar";
import { InfoTooltip } from "../ui/InfoTooltip";

export function AnomalyIntelligenceCard({ anomaly }) {
  if (!anomaly) return null;
  const { score, level, signals, amountAnomaly, entityAnomaly, missingness } = anomaly;
  return (
    <div>
      <CardHeader
        icon={Radar}
        title="Anomaly Intelligence"
        subtitle="Statistical deviation from expected transaction behavior"
      />
      <div className="mb-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <MetricBar label="Amount Anomaly" value={(amountAnomaly ?? score) * 100} color="#7C3AED" />
        <MetricBar label="Entity Anomaly" value={(entityAnomaly ?? score) * 100} color="#7C3AED" />
        <MetricBar
          label="Data Missingness"
          value={(missingness ?? 0) * 100}
          color="#7C3AED"
          tooltip="Share of expected fields that were missing or malformed."
        />
      </div>
      <div className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-[#667085]">
        Detected Signals
        <InfoTooltip text="Behavioral checks the anomaly engine runs against historical baselines for this account and device." />
      </div>
      {(!signals || signals.length === 0) && (
        <p className="text-xs text-[#98A2B3]">No anomaly signals reported for this transaction.</p>
      )}
      <div className="space-y-2">
        {signals?.map((s, idx) => (
          <div key={idx} className="flex items-start justify-between gap-3 rounded-lg border border-[#E5E7EB] p-3">
            <div>
              <p className="text-sm font-medium text-[#111827]">{s.label}</p>
              <p className="mt-0.5 text-xs text-[#667085]">{s.detail}</p>
            </div>
            <SeverityBadge severity={s.severity} />
          </div>
        ))}
      </div>
      <p className="mt-3 text-[11px] text-[#98A2B3]">
        Overall anomaly level: <span className="font-semibold text-[#475467]">{level}</span> · score{" "}
        {(score * 100).toFixed(1)}/100
      </p>
    </div>
  );
}

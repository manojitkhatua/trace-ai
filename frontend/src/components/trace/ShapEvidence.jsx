import { ArrowUpRight, ArrowDownRight, Brain } from "lucide-react";
import { CardHeader } from "../ui/Card";
import { EmptyState } from "../ui/States";

export function ShapEvidence({ factors }) {
  if (!factors || factors.length === 0) {
    return (
      <EmptyState
        icon={Brain}
        title="No model evidence provided"
        description="The API response did not include SHAP factors for this transaction."
      />
    );
  }
  const maxImpact = Math.max(...factors.map((f) => f.impact), 0.01);
  return (
    <div className="space-y-3">
      {factors.map((f, idx) => {
        const increases = f.direction === "increases";
        const pct = (f.impact / maxImpact) * 100;
        return (
          <div key={idx} className="rounded-lg border border-[#E5E7EB] p-3">
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <span
                  className={`flex h-6 w-6 items-center justify-center rounded-full ${
                    increases ? "bg-rose-50 text-rose-600" : "bg-emerald-50 text-emerald-600"
                  }`}
                >
                  {increases ? <ArrowUpRight size={13} /> : <ArrowDownRight size={13} />}
                </span>
                <span className="text-sm font-medium text-[#111827]">{f.feature}</span>
              </div>
              <span className={`text-xs font-semibold ${increases ? "text-rose-600" : "text-emerald-600"}`}>
                {increases ? "Increases risk" : "Decreases risk"}
              </span>
            </div>
            <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-[#F2F4F7]">
              <div
                className={`h-full rounded-full ${increases ? "bg-rose-500" : "bg-emerald-500"}`}
                style={{ width: `${Math.max(6, pct)}%` }}
              />
            </div>
            {f.description && <p className="mt-2 text-xs leading-relaxed text-[#667085]">{f.description}</p>}
          </div>
        );
      })}
    </div>
  );
}

export function ShapEvidenceCard({ factors }) {
  return (
    <div>
      <CardHeader
        icon={Brain}
        title="ML Model Evidence"
        subtitle="Top factors from SHAP explaining the model's fraud probability"
      />
      <ShapEvidence factors={factors} />
    </div>
  );
}

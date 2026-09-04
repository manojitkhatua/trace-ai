import { CreditCard, Brain, Gauge, Radar, Users, ShieldHalf, GitBranch, Sparkles, Archive } from "lucide-react";

export const PIPELINE_STEPS = [
  { key: "transaction", label: "Transaction", icon: CreditCard },
  { key: "ml", label: "ML Model", icon: Brain },
  { key: "shap", label: "SHAP", icon: Gauge },
  { key: "anomaly", label: "Anomaly", icon: Radar },
  { key: "entity", label: "Entity", icon: Users },
  { key: "risk", label: "Risk Engine", icon: ShieldHalf },
  { key: "decision", label: "Decision", icon: GitBranch },
  { key: "gemini", label: "Gemini", icon: Sparkles },
  { key: "audit", label: "Audit", icon: Archive },
];

export function PipelineTrack({ activeKey = "audit", completedKeys = [] }) {
  const activeIndex = PIPELINE_STEPS.findIndex((s) => s.key === activeKey);
  return (
    <div className="flex w-full items-start overflow-x-auto pb-1">
      {PIPELINE_STEPS.map((step, idx) => {
        const isDone = completedKeys.includes(step.key) || idx < activeIndex;
        const isActive = step.key === activeKey;
        const Icon = step.icon;
        return (
          <div key={step.key} className="flex min-w-[86px] flex-1 flex-col items-center">
            <div className="flex w-full items-center">
              <div className={`h-px flex-1 ${idx === 0 ? "opacity-0" : isDone || isActive ? "bg-[#2563EB]" : "bg-[#E5E7EB]"}`} />
            </div>
            <div
              className={`mt-[-13px] flex h-7 w-7 items-center justify-center rounded-full border-2 text-[11px] font-semibold ${
                isActive
                  ? "border-[#2563EB] bg-[#2563EB] text-white"
                  : isDone
                  ? "border-[#2563EB] bg-white text-[#2563EB]"
                  : "border-[#E5E7EB] bg-white text-[#98A2B3]"
              }`}
            >
              <Icon size={14} />
            </div>
            <span className={`mt-2 text-center text-[11px] font-medium ${isActive ? "text-[#111827]" : "text-[#667085]"}`}>
              {step.label}
            </span>
          </div>
        );
      })}
    </div>
  );
}

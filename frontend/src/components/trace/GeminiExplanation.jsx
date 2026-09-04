import { Sparkles, AlertCircle, CheckCircle2 } from "lucide-react";
import { CardHeader } from "../ui/Card";

export function GeminiExplanationCard({ gemini }) {
  return (
    <div>
      <CardHeader
        icon={Sparkles}
        title="Gemini Explanation"
        subtitle="Plain-language narrative generated after the TRACE decision"
      />
      {!gemini || !gemini.available ? (
        <div className="flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 p-4">
          <AlertCircle size={18} className="mt-0.5 shrink-0 text-amber-600" />
          <div>
            <p className="text-sm font-medium text-amber-800">AI explanation unavailable</p>
            <p className="mt-1 text-xs text-amber-700">
              {gemini?.error || "Gemini could not generate a narrative for this transaction."} The TRACE decision
              above is unaffected and remains valid.
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <p className="rounded-lg bg-[#F7F9FC] p-3.5 text-sm leading-relaxed text-[#344054]">{gemini.summary}</p>

          {gemini.keyFactors?.length > 0 && (
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-[#667085]">Key Factors</p>
              <ul className="space-y-1.5">
                {gemini.keyFactors.map((f, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-[#344054]">
                    <CheckCircle2 size={14} className="mt-0.5 shrink-0 text-[#2563EB]" />
                    {f}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {gemini.evidence?.length > 0 && (
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-[#667085]">Supporting Evidence</p>
              <ul className="space-y-1.5">
                {gemini.evidence.map((e, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-[#667085]">
                    <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-[#98A2B3]" />
                    {e}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {gemini.recommendedAction && (
            <div className="rounded-lg border border-[#E5E7EB] bg-[#EFF4FF] p-3.5">
              <p className="text-xs font-semibold uppercase tracking-wide text-[#2563EB]">Recommended Analyst Action</p>
              <p className="mt-1 text-sm text-[#1D4ED8]">{gemini.recommendedAction}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

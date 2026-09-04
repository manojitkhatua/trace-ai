import { Users2, CreditCard, Smartphone, MapPin, Share2, Network } from "lucide-react";
import { CardHeader } from "../ui/Card";
import { InfoTooltip } from "../ui/InfoTooltip";

const ENTITY_FIELDS = [
  { key: "cardRisk", label: "Card Risk", icon: CreditCard, tooltip: "Risk derived from this card's transaction history and prior flags." },
  { key: "deviceRisk", label: "Device Risk", icon: Smartphone, tooltip: "Risk derived from device recognition and session history." },
  { key: "addressRisk", label: "Address Risk", icon: MapPin, tooltip: "Risk derived from billing address consistency with the account." },
  { key: "relationshipRisk", label: "Relationship Risk", icon: Share2, tooltip: "Risk from shared links between this card, device, or address and other accounts." },
  { key: "networkRisk", label: "Network Risk", icon: Network, tooltip: "Risk from the broader network of entities connected to this transaction." },
];

function riskTone(value) {
  if (value === null || value === undefined) return { text: "text-[#98A2B3]", bg: "bg-[#F2F4F7]" };
  if (value >= 0.7) return { text: "text-rose-600", bg: "bg-rose-50" };
  if (value >= 0.4) return { text: "text-amber-600", bg: "bg-amber-50" };
  return { text: "text-emerald-600", bg: "bg-emerald-50" };
}

export function EntityIntelligenceCard({ entity }) {
  if (!entity) return null;
  return (
    <div>
      <CardHeader
        icon={Users2}
        title="Entity Intelligence"
        subtitle="How the card, device, address, and network relationships contribute to risk"
      />
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        {ENTITY_FIELDS.map(({ key, label, icon: Icon, tooltip }) => {
          const value = entity[key];
          const tone = riskTone(value);
          return (
            <div key={key} className="rounded-lg border border-[#E5E7EB] p-3 text-center">
              <div className={`mx-auto mb-2 flex h-8 w-8 items-center justify-center rounded-full ${tone.bg} ${tone.text}`}>
                <Icon size={15} />
              </div>
              <p className="flex items-center justify-center gap-1 text-[11px] font-medium text-[#667085]">
                {label} <InfoTooltip text={tooltip} />
              </p>
              <p className={`mt-0.5 text-sm font-semibold ${tone.text}`}>
                {value === null || value === undefined ? "N/A" : `${(value * 100).toFixed(0)}%`}
              </p>
            </div>
          );
        })}
      </div>
      {entity.notes && entity.notes.length > 0 && (
        <div className="mt-4 space-y-1.5 border-t border-[#F2F4F7] pt-3">
          {entity.notes.map((n, i) => (
            <p key={i} className="text-xs leading-relaxed text-[#667085]">
              • {n}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}

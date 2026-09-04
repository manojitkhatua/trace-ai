import { useMemo, useState } from "react";
import { Radar } from "lucide-react";
import { AppLayout } from "../components/layout/AppLayout";
import { Card, CardHeader } from "../components/ui/Card";
import { DecisionHeader } from "../components/trace/DecisionHeader";
import { ShapEvidenceCard } from "../components/trace/ShapEvidence";
import { AnomalyIntelligenceCard } from "../components/trace/AnomalyIntelligence";
import { EntityIntelligenceCard } from "../components/trace/EntityIntelligence";
import { RiskCompositionCard } from "../components/trace/RiskComposition";
import { EmptyState } from "../components/ui/States";
import { useTrace } from "../context/TraceContext";
import { formatCurrency, formatDateTime, truncateMiddle } from "../utils/format";

export default function RiskIntelligence() {
  const { history, current } = useTrace();
  const [selectedId, setSelectedId] = useState(null);

  const selected = useMemo(() => {
    return history.find((r) => r.id === selectedId) || current || history[0] || null;
  }, [history, selectedId, current]);

  if (!selected) {
    return (
      <AppLayout title="Risk Intelligence" subtitle="Deep ML, anomaly, and entity evidence behind every decision">
        <EmptyState icon={Radar} title="No transactions available" description="Analyze a transaction first." />
      </AppLayout>
    );
  }

  return (
    <AppLayout title="Risk Intelligence" subtitle="Deep ML, anomaly, and entity evidence behind every decision">
      <div className="mb-5 flex flex-col gap-3 rounded-xl border border-[#E5E7EB] bg-white p-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-[#667085]">Viewing Transaction</p>
          <p className="font-mono text-sm text-[#111827]">{selected.id}</p>
        </div>
        <select
          value={selected.id}
          onChange={(e) => setSelectedId(e.target.value)}
          className="w-full rounded-lg border border-[#D0D5DD] bg-white px-3 py-2 text-sm text-[#344054] focus:border-[#2563EB] focus:outline-none sm:w-80"
        >
          {history.map((r) => (
            <option key={r.id} value={r.id}>
              {truncateMiddle(r.id, 20)} · {formatCurrency(r.input?.amount)} · {formatDateTime(r.timestamp)}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-5">
        <DecisionHeader result={selected} />

        <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
          <Card>
            <ShapEvidenceCard factors={selected.ml.shapFactors} />
          </Card>
          <Card>
            <AnomalyIntelligenceCard anomaly={selected.anomaly} />
          </Card>
          <Card>
            <EntityIntelligenceCard entity={selected.entity} />
          </Card>
          <Card>
            <RiskCompositionCard composition={selected.riskComposition} />
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}

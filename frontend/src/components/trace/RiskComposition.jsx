import { PieChart, Pie, Cell, Tooltip as RTooltip, ResponsiveContainer } from "recharts";
import { PieChart as PieIcon } from "lucide-react";
import { CardHeader } from "../ui/Card";

const COLORS = { fraud: "#2563EB", anomaly: "#7C3AED", entity: "#DB2777" };

export function RiskCompositionCard({ composition }) {
  if (!composition) return null;
  const { weights, contributions } = composition;
  const data = [
    { key: "fraud", name: "ML Fraud Model", weight: weights.fraud, value: contributions.fraud },
    { key: "anomaly", name: "Anomaly Engine", weight: weights.anomaly, value: contributions.anomaly },
    { key: "entity", name: "Entity Intelligence", weight: weights.entity, value: contributions.entity },
  ];

  return (
    <div>
      <CardHeader
        icon={PieIcon}
        title="Risk Composition"
        subtitle="How each pipeline stage contributes to the final TRACE risk score"
      />
      <div className="flex flex-col items-center gap-6 sm:flex-row">
        <div className="h-[180px] w-[180px] shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                dataKey="value"
                nameKey="name"
                innerRadius={52}
                outerRadius={78}
                paddingAngle={3}
                strokeWidth={0}
              >
                {data.map((d) => (
                  <Cell key={d.key} fill={COLORS[d.key]} />
                ))}
              </Pie>
              <RTooltip
                formatter={(value, name) => [`${Number(value).toFixed(2)} pts`, name]}
                contentStyle={{ borderRadius: 8, border: "1px solid #E5E7EB", fontSize: 12 }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="w-full space-y-3">
          {data.map((d) => (
            <div key={d.key} className="flex items-center justify-between rounded-lg border border-[#E5E7EB] px-3 py-2">
              <div className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: COLORS[d.key] }} />
                <span className="text-sm text-[#344054]">{d.name}</span>
              </div>
              <div className="text-right">
                <p className="text-sm font-semibold text-[#111827]">{d.value.toFixed(2)} pts</p>
                <p className="text-[11px] text-[#98A2B3]">{d.weight}% policy weight</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

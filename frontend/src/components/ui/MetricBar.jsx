export function MetricBar({ label, value, tooltip, color = "#2563EB", suffix = "%" }) {
  const pct = Math.max(0, Math.min(100, value));
  return (
    <div>
      <div className="mb-1.5 flex items-center justify-between text-xs">
        <span className="font-medium text-[#344054]">{label}</span>
        <span className="font-semibold text-[#111827]">
          {pct.toFixed(1)}
          {suffix}
        </span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-[#F2F4F7]">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
      {tooltip && <p className="mt-1 text-[11px] text-[#98A2B3]">{tooltip}</p>}
    </div>
  );
}

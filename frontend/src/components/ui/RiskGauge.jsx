import { styleForLevel } from "../../utils/risk";

// A calm, precise semicircular gauge for the 0-100 TRACE risk score.
export function RiskGauge({ score = 0, level = "LOW", size = 220 }) {
  const clamped = Math.max(0, Math.min(100, Number(score) || 0));
  const style = styleForLevel(level);
  const r = size / 2 - 14;
  const cx = size / 2;
  const cy = size / 2;
  const totalLength = Math.PI * r;
  const dashOffset = totalLength * (1 - clamped / 100);

  const arcPath = `M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`;

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size / 2 + 20} viewBox={`0 0 ${size} ${size / 2 + 20}`}>
        <path d={arcPath} fill="none" stroke="#EEF1F5" strokeWidth={14} strokeLinecap="round" />
        {/* threshold ticks at 40 and 70 */}
        {[40, 70].map((tick) => {
          const angle = Math.PI - (Math.PI * tick) / 100;
          const x1 = cx + (r - 10) * Math.cos(angle);
          const y1 = cy - (r - 10) * Math.sin(angle);
          const x2 = cx + (r + 10) * Math.cos(angle);
          const y2 = cy - (r + 10) * Math.sin(angle);
          return <line key={tick} x1={x1} y1={y1} x2={x2} y2={y2} stroke="#D0D5DD" strokeWidth={2} />;
        })}
        <path
          d={arcPath}
          fill="none"
          stroke={style.hex}
          strokeWidth={14}
          strokeLinecap="round"
          strokeDasharray={totalLength}
          strokeDashoffset={dashOffset}
          style={{ transition: "stroke-dashoffset 0.8s ease, stroke 0.4s ease" }}
        />
      </svg>
      <div className="-mt-6 flex flex-col items-center">
        <span className="text-4xl font-bold tabular-nums text-[#111827]">{clamped.toFixed(1)}</span>
        <span className="text-xs font-medium uppercase tracking-wide text-[#667085]">Risk Score / 100</span>
      </div>
    </div>
  );
}

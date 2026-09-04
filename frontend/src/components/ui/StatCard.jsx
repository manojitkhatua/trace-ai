export function StatCard({ label, value, icon: Icon, tone = "default", hint }) {
  const toneMap = {
    default: "bg-[#EFF4FF] text-[#2563EB]",
    green: "bg-emerald-50 text-emerald-600",
    amber: "bg-amber-50 text-amber-600",
    red: "bg-rose-50 text-rose-600",
  };
  return (
    <div className="rounded-xl border border-[#E5E7EB] bg-white p-5">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wide text-[#667085]">{label}</span>
        {Icon && (
          <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${toneMap[tone]}`}>
            <Icon size={16} strokeWidth={2.25} />
          </div>
        )}
      </div>
      <div className="mt-3 text-2xl font-semibold text-[#111827]">{value}</div>
      {hint && <div className="mt-1 text-xs text-[#667085]">{hint}</div>}
    </div>
  );
}

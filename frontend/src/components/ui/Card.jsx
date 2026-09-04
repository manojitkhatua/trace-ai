export function Card({ children, className = "", padded = true }) {
  return (
    <div
      className={`rounded-xl border border-[#E5E7EB] bg-white ${padded ? "p-5" : ""} ${className}`}
    >
      {children}
    </div>
  );
}

export function CardHeader({ title, subtitle, icon: Icon, action }) {
  return (
    <div className="mb-4 flex items-start justify-between gap-3">
      <div className="flex items-start gap-3">
        {Icon && (
          <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-[#EFF4FF] text-[#2563EB]">
            <Icon size={18} strokeWidth={2} />
          </div>
        )}
        <div>
          <h3 className="text-sm font-semibold text-[#111827]">{title}</h3>
          {subtitle && <p className="mt-0.5 text-xs text-[#667085]">{subtitle}</p>}
        </div>
      </div>
      {action}
    </div>
  );
}

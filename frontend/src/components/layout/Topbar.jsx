import { Menu } from "lucide-react";
import { ModeBadge } from "../ui/Badge";
import { useTrace } from "../../context/TraceContext";
import { API_BASE_URL } from "../../services/api";

export function Topbar({ title, subtitle, onMenuClick }) {
  const { apiStatus } = useTrace();
  return (
    <header className="sticky top-0 z-20 flex items-center justify-between gap-4 border-b border-[#E5E7EB] bg-white/90 px-4 py-3.5 backdrop-blur sm:px-6">
      <div className="flex items-center gap-3">
        <button className="text-[#475467] lg:hidden" onClick={onMenuClick} aria-label="Open menu">
          <Menu size={20} />
        </button>
        <div>
          <h1 className="text-base font-semibold text-[#111827] sm:text-lg">{title}</h1>
          {subtitle && <p className="hidden text-xs text-[#667085] sm:block">{subtitle}</p>}
        </div>
      </div>
      <div className="flex items-center gap-3">
        <div className="group relative hidden sm:block">
          <ModeBadge mode={apiStatus.mode} />
          <div className="pointer-events-none absolute right-0 top-full z-20 mt-2 w-64 rounded-lg border border-[#E5E7EB] bg-white p-2.5 text-[11px] text-[#475467] opacity-0 shadow-lg transition-opacity group-hover:opacity-100">
            API endpoint: <span className="font-mono text-[#2563EB]">{API_BASE_URL}/predict</span>
            {apiStatus.error && <div className="mt-1 text-rose-600">{apiStatus.error}</div>}
          </div>
        </div>
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#111827] text-xs font-semibold text-white">
          AN
        </div>
      </div>
    </header>
  );
}

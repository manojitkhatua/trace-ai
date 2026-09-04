import { NavLink } from "react-router-dom";
import { LayoutGrid, ScanSearch, Radar, Users2, History, ShieldCheck, X } from "lucide-react";

const NAV_ITEMS = [
  { to: "/", label: "Overview", icon: LayoutGrid, end: true },
  { to: "/analyze", label: "Analyze Transaction", icon: ScanSearch },
  { to: "/risk-intelligence", label: "Risk Intelligence", icon: Radar },
  { to: "/investigation", label: "Investigation", icon: Users2 },
  { to: "/audit-trail", label: "Audit Trail", icon: History },
];

export function Sidebar({ open, onClose }) {
  return (
    <>
      {open && (
        <div
          className="fixed inset-0 z-30 bg-black/30 lg:hidden"
          onClick={onClose}
        />
      )}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-64 shrink-0 transform flex-col border-r border-[#E5E7EB] bg-white transition-transform duration-200 lg:static lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between gap-2 border-b border-[#E5E7EB] px-5 py-5">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#2563EB] text-white">
              <ShieldCheck size={19} strokeWidth={2.25} />
            </div>
            <div>
              <p className="text-[15px] font-bold leading-tight text-[#111827]">TRACE</p>
              <p className="text-[11px] leading-tight text-[#667085]">Fraud Intelligence</p>
            </div>
          </div>
          <button className="text-[#667085] lg:hidden" onClick={onClose} aria-label="Close menu">
            <X size={18} />
          </button>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-[#EFF4FF] text-[#2563EB]"
                    : "text-[#475467] hover:bg-[#F7F9FC] hover:text-[#111827]"
                }`
              }
            >
              <item.icon size={17} strokeWidth={2} />
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-[#E5E7EB] px-5 py-4">
          <p className="text-[11px] leading-relaxed text-[#98A2B3]">
            TRACE decisions are produced by an ML + rules risk pipeline. Gemini explanations supplement — never
            override — the decision.
          </p>
        </div>
      </aside>
    </>
  );
}

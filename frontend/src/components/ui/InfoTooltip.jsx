import { useState } from "react";
import { Info } from "lucide-react";

export function InfoTooltip({ text }) {
  const [open, setOpen] = useState(false);
  return (
    <span className="relative inline-flex">
      <button
        type="button"
        aria-label="More information"
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        onClick={() => setOpen((o) => !o)}
        className="inline-flex text-[#98A2B3] hover:text-[#2563EB] focus:outline-none"
      >
        <Info size={13} />
      </button>
      {open && (
        <span className="absolute bottom-full left-1/2 z-20 mb-2 w-56 -translate-x-1/2 rounded-lg border border-[#E5E7EB] bg-white p-2.5 text-[11px] font-normal leading-relaxed text-[#475467] shadow-lg">
          {text}
        </span>
      )}
    </span>
  );
}

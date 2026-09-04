export function FormField({ label, tooltip, children, hint }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-xs font-semibold text-[#344054]">{label}</span>
      {children}
      {hint && <span className="mt-1 block text-[11px] text-[#98A2B3]">{hint}</span>}
    </label>
  );
}

const baseInputClass =
  "w-full rounded-lg border border-[#D0D5DD] bg-white px-3 py-2 text-sm text-[#111827] placeholder:text-[#98A2B3] focus:border-[#2563EB] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/15";

export function TextInput(props) {
  return <input {...props} className={`${baseInputClass} ${props.className || ""}`} />;
}

export function SelectInput({ options, ...props }) {
  return (
    <select {...props} className={`${baseInputClass} ${props.className || ""}`}>
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
  );
}

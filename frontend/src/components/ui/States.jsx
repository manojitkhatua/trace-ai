import { Loader2, ShieldQuestion, AlertTriangle, Inbox } from "lucide-react";

export function LoadingState({ label = "Running TRACE pipeline…" }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-[#E5E7EB] bg-white py-16 text-center">
      <Loader2 size={28} className="animate-spin text-[#2563EB]" />
      <p className="text-sm font-medium text-[#344054]">{label}</p>
      <p className="max-w-xs text-xs text-[#667085]">
        Scoring the transaction across the ML, anomaly, entity, and risk decision stages.
      </p>
    </div>
  );
}

export function EmptyState({ icon: Icon = Inbox, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-[#E5E7EB] bg-white py-16 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#F2F4F7] text-[#98A2B3]">
        <Icon size={22} />
      </div>
      <p className="text-sm font-semibold text-[#344054]">{title}</p>
      {description && <p className="max-w-sm text-xs text-[#667085]">{description}</p>}
      {action}
    </div>
  );
}

export function ErrorState({ title = "Something went wrong", description, action }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-rose-200 bg-rose-50/40 py-16 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-rose-100 text-rose-600">
        <AlertTriangle size={22} />
      </div>
      <p className="text-sm font-semibold text-rose-700">{title}</p>
      {description && <p className="max-w-sm text-xs text-rose-600/80">{description}</p>}
      {action}
    </div>
  );
}

export function NoResultState({ action }) {
  return (
    <EmptyState
      icon={ShieldQuestion}
      title="No transaction analyzed yet"
      description="Submit a transaction on the left to see TRACE's live risk assessment, decision, and evidence."
      action={action}
    />
  );
}

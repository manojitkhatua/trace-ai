export function formatCurrency(value, currency = "USD") {
  const n = Number(value);
  if (Number.isNaN(n)) return "—";
  try {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency,
      maximumFractionDigits: 2,
    }).format(n);
  } catch {
    return `$${n.toFixed(2)}`;
  }
}

// Accepts a fraction (0-1) or already-percent number and returns "12.3%"
export function formatPercent(value, digits = 1) {
  const n = Number(value);
  if (Number.isNaN(n)) return "—";
  const pct = n <= 1 ? n * 100 : n;
  return `${pct.toFixed(digits)}%`;
}

export function formatScore(value, digits = 2) {
  const n = Number(value);
  if (Number.isNaN(n)) return "—";
  return n.toFixed(digits);
}

export function formatDateTime(input) {
  if (!input) return "—";
  const d = new Date(input);
  if (Number.isNaN(d.getTime())) return String(input);
  return d.toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatRelativeTime(input) {
  if (!input) return "—";
  const d = new Date(input);
  if (Number.isNaN(d.getTime())) return String(input);
  const diffMs = Date.now() - d.getTime();
  const diffSec = Math.round(diffMs / 1000);
  if (diffSec < 60) return "just now";
  const diffMin = Math.round(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.round(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  const diffDay = Math.round(diffHr / 24);
  if (diffDay < 30) return `${diffDay}d ago`;
  return formatDateTime(input);
}

export function truncateMiddle(str, len = 18) {
  if (!str) return "—";
  const s = String(str);
  if (s.length <= len) return s;
  const half = Math.floor((len - 3) / 2);
  return `${s.slice(0, half)}...${s.slice(s.length - half)}`;
}

export function generateTxnId() {
  const rand = Math.random().toString(36).slice(2, 8).toUpperCase();
  return `TXN-${Date.now().toString().slice(-6)}${rand}`;
}

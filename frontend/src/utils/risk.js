// Central risk policy definitions shared across the whole app.
// 0 - 39.99  -> LOW    -> ALLOW
// 40 - 69.99 -> MEDIUM -> REVIEW
// 70 - 100   -> HIGH   -> BLOCK

export function levelFromScore(score) {
  const s = Number(score) || 0;
  if (s >= 70) return "HIGH";
  if (s >= 40) return "MEDIUM";
  return "LOW";
}

export function decisionFromLevel(level) {
  if (level === "HIGH") return "BLOCK";
  if (level === "MEDIUM") return "REVIEW";
  return "ALLOW";
}

export function decisionFromScore(score) {
  return decisionFromLevel(levelFromScore(score));
}

// Tailwind-friendly color tokens for each risk level.
export const RISK_LEVEL_STYLES = {
  LOW: {
    text: "text-emerald-700",
    bg: "bg-emerald-50",
    border: "border-emerald-200",
    dot: "bg-emerald-500",
    ring: "ring-emerald-200",
    hex: "#059669",
    soft: "#ECFDF5",
  },
  MEDIUM: {
    text: "text-amber-700",
    bg: "bg-amber-50",
    border: "border-amber-200",
    dot: "bg-amber-500",
    ring: "ring-amber-200",
    hex: "#D97706",
    soft: "#FFFBEB",
  },
  HIGH: {
    text: "text-rose-700",
    bg: "bg-rose-50",
    border: "border-rose-200",
    dot: "bg-rose-500",
    ring: "ring-rose-200",
    hex: "#DC2626",
    soft: "#FEF2F2",
  },
};

export const DECISION_STYLES = {
  ALLOW: RISK_LEVEL_STYLES.LOW,
  REVIEW: RISK_LEVEL_STYLES.MEDIUM,
  BLOCK: RISK_LEVEL_STYLES.HIGH,
};

export const DECISION_LABELS = {
  ALLOW: "Allow",
  REVIEW: "Manual Review",
  BLOCK: "Block",
};

export const RISK_LEVEL_LABELS = {
  LOW: "Low Risk",
  MEDIUM: "Medium Risk",
  HIGH: "High Risk",
};

export function styleForLevel(level) {
  return RISK_LEVEL_STYLES[level] || RISK_LEVEL_STYLES.LOW;
}

export function styleForDecision(decision) {
  return DECISION_STYLES[decision] || DECISION_STYLES.ALLOW;
}

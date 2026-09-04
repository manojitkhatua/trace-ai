import { levelFromScore, decisionFromScore } from "../utils/risk";
import { generateTxnId } from "../utils/format";
import {
  DEMO_RESULT,
  buildRiskComposition,
  computeRiskScore,
} from "../utils/demoData";

export const API_BASE_URL =
  (typeof import.meta !== "undefined" &&
    import.meta.env &&
    import.meta.env.VITE_API_BASE_URL) ||
  "http://127.0.0.1:5000";

const PREDICT_ENDPOINT = `${API_BASE_URL.replace(/\/$/, "")}/predict`;
const DEFAULT_TIMEOUT_MS = 15000;

const FEATURE_LABELS = {
  TransactionAmt: "Transaction Amount",
  ProductCD: "Product Category",
  card1: "Payment / Card ID",
  card2: "Card Attribute",
  card4: "Card Network",
  card6: "Card Type",
  addr1: "Billing Region",
  addr2: "Secondary Region",
  DeviceType: "Device Type",
  DeviceInfo: "Device Information",
  D7: "Model Signal D7",
  D12: "Model Signal D12",
  D13: "Model Signal D13",
  D14: "Model Signal D14",
};

function getPath(obj, path) {
  return path.split(".").reduce((current, key) => {
    if (current && typeof current === "object") {
      return current[key];
    }
    return undefined;
  }, obj);
}

function firstDefined(obj, paths, fallback = undefined) {
  for (const path of paths) {
    const value = getPath(obj, path);
    if (value !== undefined && value !== null && value !== "") {
      return value;
    }
  }
  return fallback;
}

function toNumber(value, fallback = null) {
  if (value === undefined || value === null || value === "") {
    return fallback;
  }

  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function toFraction(value, fallback = 0) {
  const number = toNumber(value, null);

  if (number === null) {
    return fallback;
  }

  return number > 1 ? number / 100 : number;
}

function toScore100(value, fallback = 0) {
  const number = toNumber(value, null);

  if (number === null) {
    return fallback;
  }

  return number <= 1 ? number * 100 : number;
}

function humanizeFeatureName(name) {
  if (FEATURE_LABELS[name]) {
    return FEATURE_LABELS[name];
  }

  if (typeof name !== "string") {
    return String(name);
  }

  const text = name
    .replace(/_/g, " ")
    .replace(/([a-z])([A-Z])/g, "$1 $2");

  return text.charAt(0).toUpperCase() + text.slice(1);
}

function normalizeShapFactors(raw) {
  if (!raw) {
    return null;
  }

  let list = raw;

  if (!Array.isArray(raw) && typeof raw === "object") {
    list = Object.entries(raw).map(([feature, value]) => ({
      feature,
      value,
    }));
  }

  if (!Array.isArray(list)) {
    return null;
  }

  return list.map((item) => {
    const feature =
      item?.feature ||
      item?.name ||
      item?.key ||
      "Model Feature";

    const rawImpact =
      item?.impact ??
      item?.shap_value ??
      item?.value ??
      item?.weight ??
      0;

    const numericImpact = Number(rawImpact) || 0;

    return {
      feature: humanizeFeatureName(feature),
      direction:
        item?.direction ||
        (numericImpact < 0 ? "decreases" : "increases"),
      impact: Math.abs(numericImpact),
      description:
        item?.description ||
        item?.explanation ||
        null,
    };
  });
}

function normalizeSignals(raw) {
  if (!raw) {
    return [];
  }

  if (Array.isArray(raw)) {
    return raw.map((signal) => ({
      name: signal?.name || signal?.key || signal?.label || "Signal",
      label:
        signal?.label ||
        humanizeFeatureName(
          signal?.name || signal?.key || "Signal"
        ),
      detail:
        signal?.detail ||
        signal?.description ||
        "",
      severity: signal?.severity || "medium",
    }));
  }

  if (typeof raw === "object") {
    return Object.entries(raw).map(([name, detail]) => ({
      name,
      label: humanizeFeatureName(name),
      detail:
        typeof detail === "string"
          ? detail
          : JSON.stringify(detail),
      severity: "medium",
    }));
  }

  return [];
}

function normalizeApiResponse(raw, input, meta = {}) {
  const fraudProbability = toFraction(
    firstDefined(raw, [
      "fraud_probability",
      "fraudProbability",
      "probability",
    ]),
    0
  );

  const anomalyScore = toFraction(
    firstDefined(raw, [
      "anomaly_score",
      "anomalyScore",
    ]),
    0
  );

  const entityRisk = toFraction(
    firstDefined(raw, [
      "entity_risk",
      "entityRisk",
    ]),
    0
  );

  const computedScore = computeRiskScore(
    fraudProbability,
    anomalyScore,
    entityRisk
  );

  const riskScore = toScore100(
    firstDefined(raw, [
      "risk_score",
      "riskScore",
    ]),
    computedScore
  );

  const riskLevel =
    firstDefined(raw, [
      "risk_level",
      "riskLevel",
    ]) || levelFromScore(riskScore);

  const decision =
    firstDefined(raw, [
      "decision",
      "final_decision",
    ]) || decisionFromScore(riskScore);

  const shapFactors = normalizeShapFactors(
    firstDefined(raw, [
      "reasons",
      "shap",
      "shap_values",
      "shap_factors",
    ], null)
  );

  const anomalySignals = normalizeSignals(
    firstDefined(raw, [
      "anomaly_signals",
      "anomaly?.signals",
      "signals",
    ], null)
  );

  const entityBreakdown =
    firstDefined(raw, [
      "entity_breakdown",
      "entity.breakdown",
    ], {}) || {};

  const geminiRaw = firstDefined(
    raw,
    [
      "gemini_explanation",
      "gemini",
      "explanation.gemini",
    ],
    null
  );

  let gemini;

  if (geminiRaw && typeof geminiRaw === "object") {
    gemini = {
      available: true,
      summary:
        geminiRaw.summary ||
        geminiRaw.text ||
        null,
      keyFactors:
        geminiRaw.key_factors ||
        geminiRaw.keyFactors ||
        [],
      evidence: geminiRaw.evidence || [],
      recommendedAction:
        geminiRaw.analyst_action ||
        geminiRaw.recommended_action ||
        geminiRaw.recommendedAction ||
        null,
    };
  } else if (typeof geminiRaw === "string") {
    gemini = {
      available: true,
      summary: geminiRaw,
      keyFactors: [],
      evidence: [],
      recommendedAction: null,
    };
  } else {
    gemini = {
      available: false,
      error: "Gemini explanation unavailable.",
    };
  }

  return {
    id:
      firstDefined(raw, [
        "transaction_id",
        "id",
      ]) || generateTxnId(),

    timestamp:
      firstDefined(raw, ["timestamp"]) ||
      input?.timestamp ||
      new Date().toISOString(),

    source: meta.mode || "live",

    input,

    scores: {
      fraudProbability,
      anomalyScore,
      entityRisk,
      riskScore,
    },

    riskLevel,
    decision,

    ml: {
      shapFactors,
      modelConfidence:
        firstDefined(raw, [
          "model_confidence",
          "ml.confidence",
        ], null),
    },

    anomaly: {
      score: anomalyScore,
      level:
        firstDefined(raw, [
          "anomaly_level",
          "anomaly.level",
        ]) || levelFromScore(anomalyScore * 100),

      amountAnomaly: toFraction(
        firstDefined(raw, [
          "anomaly_components.amount",
          "anomaly.amount_anomaly",
          "amount_anomaly",
        ], null),
        null
      ),

      entityAnomaly: toFraction(
        firstDefined(raw, [
          "anomaly_components.entity",
          "anomaly.entity_anomaly",
          "entity_anomaly",
        ], null),
        null
      ),

      missingness: toFraction(
        firstDefined(raw, [
          "anomaly_components.missingness",
          "anomaly.missingness",
          "missingness_score",
        ], null),
        null
      ),

      signals: anomalySignals,
    },

    entity: {
      cardRisk: toFraction(
        entityBreakdown.card,
        entityRisk
      ),

      deviceRisk: toFraction(
        entityBreakdown.device,
        null
      ),

      addressRisk: toFraction(
        entityBreakdown.address,
        null
      ),

      relationshipRisk: toFraction(
        entityBreakdown.relationship,
        null
      ),

      networkRisk: toFraction(
        entityBreakdown.network,
        null
      ),

      notes: [],
    },

    riskComposition: buildRiskComposition(
      fraudProbability,
      anomalyScore,
      entityRisk
    ),

    gemini,

    raw,
  };
}

/*
 * Converts the simple frontend form into the EXACT fields
 * expected by the existing Flask /predict endpoint.
 */
export function buildPredictPayload(form) {
  const amount = toNumber(form?.amount, 0);
  const card1 = toNumber(form?.cardId, null);

  const card2 = toNumber(
    form?.advanced?.card2,
    null
  );

  const addr1 = toNumber(
    form?.billingAddress?.state,
    null
  );

  const addr2 = toNumber(
    form?.advanced?.addr2,
    null
  );

  const d7 = toNumber(
    form?.advanced?.d7,
    null
  );

  const d12 = toNumber(
    form?.advanced?.d12,
    null
  );

  const d13 = toNumber(
    form?.advanced?.d13,
    null
  );

  const d14 = toNumber(
    form?.advanced?.d14,
    null
  );

  /*
   * TransactionDT must be the numeric value expected by the
   * trained model. A form.transactionDT can be supplied directly
   * by the UI/demo data. Otherwise use the existing demo-compatible
   * value until timestamp conversion is explicitly defined.
   */
  const transactionDT = toNumber(
    form?.transactionDT,
    12192900
  );

  return {
    TransactionAmt: amount,
    TransactionDT: transactionDT,
    card1,
    card2,
    addr1,
    addr2,
    D7: d7,
    D12: d12,
    D13: d13,
    D14: d14,
    DeviceInfo:
      form?.deviceInfo?.trim() || null,
    ProductCD: form?.productCategory || null,
    card4: form?.cardNetwork || null,
    card6: form?.cardType || null,
    DeviceType: form?.deviceType || null,
  };
}

function withTimeout(promise, ms) {
  let timer;

  const timeout = new Promise((_, reject) => {
    timer = setTimeout(
      () => reject(new Error("TIMEOUT")),
      ms
    );
  });

  return Promise.race([
    promise,
    timeout,
  ]).finally(() => {
    clearTimeout(timer);
  });
}

export async function predictTransaction(form) {
  const payload = buildPredictPayload(form);

  try {
    const controller = new AbortController();

    const response = await withTimeout(
      fetch(PREDICT_ENDPOINT, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
        signal: controller.signal,
      }),
      DEFAULT_TIMEOUT_MS
    ).catch((error) => {
      controller.abort();
      throw error;
    });

    if (!response.ok) {
      const errorText = await response.text().catch(
        () => ""
      );

      throw new Error(
        `API ${response.status}: ${
          errorText || "Prediction failed."
        }`
      );
    }

    const json = await response.json();

    const result = normalizeApiResponse(
      json,
      form,
      { mode: "live" }
    );

    return {
      mode: "live",
      result,
      error: null,
    };
  } catch (error) {
    console.error(
      "TRACE API request failed:",
      error
    );

    const reason =
      error?.message === "TIMEOUT"
        ? "TRACE API timed out."
        : error?.message ||
          "TRACE API request failed.";

    /*
     * Keep demo fallback only for connectivity failures.
     * A real HTTP 4xx/5xx should remain visible instead of
     * silently becoming fake demo data.
     */
    if (
      error?.message?.includes("API 4") ||
      error?.message?.includes("API 5")
    ) {
      throw error;
    }

    return {
      mode: "demo",
      result: buildDemoFallback(form, reason),
      error: reason,
    };
  }
}

function buildDemoFallback(form, reason) {
  const usedDefaultDemo =
    !form || !form.amount;

  const base = usedDefaultDemo
    ? DEMO_RESULT
    : mutateDemoForInput(form);

  return {
    ...base,
    id: generateTxnId(),
    timestamp:
      form?.timestamp ||
      new Date().toISOString(),
    source: "demo",
    input: form || DEMO_RESULT.input,
    demoReason: reason,
  };
}

function mutateDemoForInput(form) {
  const amount =
    Number(form?.amount) || 0;

  const amountFactor = Math.min(
    1,
    amount / 4000
  );

  const deviceKnown = [
    "mobile",
    "desktop",
    "tablet",
  ].includes(
    String(form?.deviceType || "").toLowerCase()
  );

  const fraudProbability = Math.min(
    0.98,
    0.05 +
      amountFactor * 0.55 +
      (deviceKnown ? 0 : 0.2)
  );

  const anomalyScore = Math.min(
    0.95,
    0.1 + amountFactor * 0.45
  );

  const entityRisk = Math.min(
    0.95,
    0.15 + amountFactor * 0.35
  );

  const riskScore = computeRiskScore(
    fraudProbability,
    anomalyScore,
    entityRisk
  );

  const riskLevel =
    levelFromScore(riskScore);

  const decision =
    decisionFromScore(riskScore);

  return {
    ...DEMO_RESULT,

    scores: {
      fraudProbability,
      anomalyScore,
      entityRisk,
      riskScore,
    },

    riskLevel,
    decision,

    riskComposition:
      buildRiskComposition(
        fraudProbability,
        anomalyScore,
        entityRisk
      ),

    anomaly: {
      ...DEMO_RESULT.anomaly,
      score: anomalyScore,
      level: riskLevel,
    },

    entity: {
      ...DEMO_RESULT.entity,
      cardRisk: entityRisk,
    },
  };
}
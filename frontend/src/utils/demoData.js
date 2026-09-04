import { levelFromScore, decisionFromScore } from "./risk";
import { generateTxnId } from "./format";

// ============================================================
// TRACE RISK WEIGHTS
// ============================================================

export const RISK_WEIGHTS = {
  fraud: 0.55,
  anomaly: 0.2,
  entity: 0.25,
};


// ============================================================
// RISK CALCULATION
// ============================================================

export function computeRiskScore(
  fraudProbability,
  anomalyScore,
  entityRisk
) {
  const score =
    fraudProbability * 100 * RISK_WEIGHTS.fraud +
    anomalyScore * 100 * RISK_WEIGHTS.anomaly +
    entityRisk * 100 * RISK_WEIGHTS.entity;

  return Math.round(score * 100) / 100;
}


export function buildRiskComposition(
  fraudProbability,
  anomalyScore,
  entityRisk
) {
  return {
    weights: {
      fraud: 55,
      anomaly: 20,
      entity: 25,
    },

    contributions: {
      fraud:
        Math.round(
          fraudProbability * 100 * 0.55 * 100
        ) / 100,

      anomaly:
        Math.round(
          anomalyScore * 100 * 0.2 * 100
        ) / 100,

      entity:
        Math.round(
          entityRisk * 100 * 0.25 * 100
        ) / 100,
    },
  };
}


// ============================================================
// COMMON EMPTY INPUT STRUCTURE
// ============================================================

export const EMPTY_DEMO_INPUT = {
  amount: 52.811,

  transactionDT: 12192900,

  timestamp: new Date().toISOString(),

  cardId: 9300,

  productCategory: "C",
  cardNetwork: "visa",
  cardType: "credit",

  deviceType: "",
  deviceInfo: "",

  billingAddress: {
    line1: "",
    city: "",
    state: "",
    zip: "",
    country: null,
  },

  advanced: {
    card2: 103,
    addr2: null,
    d7: null,
    d12: null,
    d13: null,
    d14: null,
  },
};


// ============================================================
// ALLOW DEMO
// ============================================================

/*
 * Existing tested TRACE transaction.
 *
 * Expected:
 * Fraud Probability : ~7.99%
 * Anomaly Score     : 23%
 * Entity Risk       : 31.33%
 * Risk Score        : 16.83
 * Risk Level        : LOW
 * Decision          : ALLOW
 */

export const DEMO_INPUT = {
  ...EMPTY_DEMO_INPUT,
};


const DEMO_SHAP_LOW = [
  {
    feature: "addr1_transaction_count",
    direction: "decreases",
    impact: 0.93,
    description:
      "Billing-region activity lowers the fraud signal.",
  },

  {
    feature: "ProductCD_C",
    direction: "increases",
    impact: 0.55,
    description:
      "This product category increases the fraud signal.",
  },

  {
    feature: "card1_unique_DeviceInfo_count",
    direction: "increases",
    impact: 0.29,
    description:
      "The card-device relationship contributes some additional risk.",
  },

  {
    feature: "TransactionAmt",
    direction: "decreases",
    impact: 0.24,
    description:
      "The transaction amount lowers the fraud signal.",
  },
];


const DEMO_ANOMALY_LOW = {
  score: 0.23,
  level: "LOW",

  amountAnomaly: 0.0716,
  entityAnomaly: 0.2869,
  missingness: 0.3382,

  signals: [
    {
      name: "address_pattern",
      label: "Address Pattern",
      detail:
        "Address availability pattern is unusual.",
      severity: "low",
    },

    {
      name: "device_relationship",
      label: "Card-Device Pattern",
      detail:
        "Card-device activity shows an unusual relationship.",
      severity: "low",
    },

    {
      name: "billing_activity",
      label: "Billing Activity",
      detail:
        "Billing/address activity is unusual.",
      severity: "low",
    },
  ],
};


const DEMO_ENTITY_LOW = {
  cardRisk: 0.0831,
  deviceRisk: 0.4,
  addressRisk: 0.35,
  relationshipRisk: 0.4,
  networkRisk: 0.4,

  notes: [
    "Card activity is relatively low risk.",
    "Device relationship contributes moderate risk.",
    "Billing/address activity remains low risk.",
  ],
};


const DEMO_GEMINI_LOW = {
  available: true,

  summary:
    "TRACE classified this transaction as low operational risk. The model probability is low and the combined anomaly and entity signals do not push the transaction into review or block territory.",

  keyFactors: [
    "Low fraud probability",
    "No strong anomaly signal",
    "Overall entity risk remains low",
  ],

  evidence: [
    "Fraud probability: 7.99%",
    "Anomaly score: 23%",
    "Entity risk: 31.33%",
  ],

  recommendedAction:
    "No analyst action required. The transaction can proceed under the ALLOW decision.",
};


// ============================================================
// VERIFIED REAL BLOCK DEMO
// ============================================================

/*
 * REAL VALIDATION TRANSACTION
 *
 * TransactionID : 3464297
 * Amount        : 44.266
 * TransactionDT : 12352706
 * card1         : 9026
 * card2         : 545
 * addr1         : missing
 * addr2         : missing
 * D7            : 0
 * D12           : 0
 * D13           : missing
 * D14           : 0
 * DeviceInfo    : Moto E (4) Build/NMA26.42-69
 * ProductCD     : C
 * card4         : visa
 * card6         : credit
 * DeviceType    : desktop
 *
 * Verified TRACE result:
 * Fraud Probability : 88.41%
 * Anomaly Score     : 49.73%
 * Entity Risk       : 62.74%
 * Risk Score        : 74.26
 * Risk Level        : HIGH
 * Decision          : BLOCK
 *
 * This is a real fraud transaction from the chronological
 * validation set, not an artificially generated transaction.
 */

export const VERIFIED_BLOCK_INPUT = {
  amount: 44.266,

  // Exact TransactionDT from validation.
  transactionDT: 12352706,

  timestamp: new Date().toISOString(),

  // Exact card1.
  cardId: 9026,

  productCategory: "C",
  cardNetwork: "visa",
  cardType: "credit",

  // Exact identity fields.
  deviceType: "desktop",
  deviceInfo: "Moto E (4) Build/NMA26.42-69",

  billingAddress: {
    line1: "",
    city: "",
    state: "",
    zip: "",
    country: null,
  },

  advanced: {
    card2: 545,
    addr2: null,

    d7: 0,
    d12: 0,
    d13: null,
    d14: 0,
  },
};


// ============================================================
// RESULT BUILDER
// ============================================================

function buildResult({
  id,
  timestamp,
  source = "demo",
  input,
  fraudProbability,
  anomalyScore,
  entityRisk,
  riskScoreOverride,
  shapFactors,
  anomaly,
  entity,
  gemini,
}) {
  const riskScore =
    riskScoreOverride !== undefined
      ? riskScoreOverride
      : computeRiskScore(
          fraudProbability,
          anomalyScore,
          entityRisk
        );

  const riskLevel = levelFromScore(riskScore);

  const decision = decisionFromScore(riskScore);

  return {
    id,
    timestamp,
    source,
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
    },

    anomaly,
    entity,

    riskComposition:
      buildRiskComposition(
        fraudProbability,
        anomalyScore,
        entityRisk
      ),

    gemini,
  };
}


// ============================================================
// ALLOW RESULT
// ============================================================

export const DEMO_RESULT = buildResult({
  id: "TXN-DEMO0001",

  timestamp: new Date(
    Date.now() - 6 * 60 * 1000
  ).toISOString(),

  input: DEMO_INPUT,

  fraudProbability: 0.07997,
  anomalyScore: 0.23,
  entityRisk: 0.3133,

  riskScoreOverride: 16.83,

  shapFactors: DEMO_SHAP_LOW,
  anomaly: DEMO_ANOMALY_LOW,
  entity: DEMO_ENTITY_LOW,
  gemini: DEMO_GEMINI_LOW,
});


// ============================================================
// VERIFIED BLOCK RESULT
//
// Used only as fallback demo data if backend is unavailable.
// Normally Analyze sends VERIFIED_BLOCK_INPUT to the backend.
// ============================================================

const BLOCK_SHAP_FACTORS = [
  {
    feature: "TransactionAmt",
    direction: "increases",
    impact: 0.92,
    description:
      "The transaction amount contributes strongly to the fraud signal.",
  },

  {
    feature: "card1_unique_DeviceInfo_count",
    direction: "increases",
    impact: 0.78,
    description:
      "The observed card-device relationship contributes significant risk.",
  },

  {
    feature: "DeviceType",
    direction: "increases",
    impact: 0.61,
    description:
      "The device profile contributes to the elevated fraud signal.",
  },

  {
    feature: "ProductCD_C",
    direction: "increases",
    impact: 0.54,
    description:
      "The product category contributes additional fraud risk.",
  },
];


const BLOCK_ANOMALY = {
  score: 0.4973,
  level: "MEDIUM",

  amountAnomaly: 0.0,
  entityAnomaly: 0.0,
  missingness: 0.0,

  signals: [
    {
      name: "transaction_pattern",
      label: "Transaction Pattern",
      detail:
        "The transaction shows an elevated anomaly score.",
      severity: "medium",
    },

    {
      name: "entity_pattern",
      label: "Entity Pattern",
      detail:
        "Entity behavior contributes additional anomaly risk.",
      severity: "medium",
    },
  ],
};


const BLOCK_ENTITY = {
  cardRisk: 0.0,
  deviceRisk: 0.0,
  addressRisk: 0.0,
  relationshipRisk: 0.0,
  networkRisk: 0.0,

  notes: [
    "Card activity contributes to elevated entity risk.",
    "Device relationship contributes additional risk.",
    "Combined entity signals increase the overall score.",
  ],
};


const BLOCK_GEMINI = {
  available: true,

  summary:
    "TRACE identified a high-risk transaction. The fraud model probability is high and the combined anomaly and entity signals push the transaction above the blocking threshold.",

  keyFactors: [
    "High fraud probability",
    "Elevated anomaly score",
    "Elevated entity risk",
  ],

  evidence: [
    "Fraud probability: 88.41%",
    "Anomaly score: 49.73%",
    "Entity risk: 62.74%",
  ],

  recommendedAction:
    "Block the transaction and route it for investigation.",
};


export const VERIFIED_BLOCK_RESULT =
  buildResult({
    id: "TXN-3464297",

    timestamp: new Date().toISOString(),

    source: "validation",

    input: VERIFIED_BLOCK_INPUT,

    fraudProbability: 0.8840982173974141,

    anomalyScore: 0.4973,

    entityRisk: 0.6274,

    riskScoreOverride: 74.26,

    shapFactors: BLOCK_SHAP_FACTORS,

    anomaly: BLOCK_ANOMALY,

    entity: BLOCK_ENTITY,

    gemini: BLOCK_GEMINI,
  });


// ============================================================
// PRESENTATION HISTORY
// ============================================================

const DEMO_HISTORY = [
  {
    amount: 52.811,
    cardId: 9300,
    productCategory: "C",
    cardNetwork: "visa",
    cardType: "credit",
    deviceType: "",
    deviceInfo: "",

    fraud: 0.07997,
    anomaly: 0.23,
    entity: 0.3133,
    score: 16.83,

    decision: "ALLOW",
  },

  {
    amount: 1284,
    cardId: 55810,
    productCategory: "H",
    cardNetwork: "amex",
    cardType: "credit",
    deviceType: "desktop",
    deviceInfo: "Windows 11 / Chrome",

    fraud: 0.61,
    anomaly: 0.48,
    entity: 0.52,

    decision: "REVIEW",
  },

  {
    amount: 42.15,
    cardId: 20981,
    productCategory: "R",
    cardNetwork: "mastercard",
    cardType: "debit",
    deviceType: "mobile",
    deviceInfo: "Android Device",

    fraud: 0.06,
    anomaly: 0.11,
    entity: 0.09,

    decision: "ALLOW",
  },

  {
    amount: 3499.99,
    cardId: 88213,
    productCategory: "C",
    cardNetwork: "visa",
    cardType: "credit",
    deviceType: "mobile",
    deviceInfo: "Unrecognized Device",

    fraud: 0.95,
    anomaly: 0.9,
    entity: 0.88,

    decision: "BLOCK",
  },

  {
    amount: 19.99,
    cardId: 10294,
    productCategory: "S",
    cardNetwork: "visa",
    cardType: "debit",
    deviceType: "mobile",
    deviceInfo: "iOS Device",

    fraud: 0.05,
    anomaly: 0.08,
    entity: 0.07,

    decision: "ALLOW",
  },

  {
    amount: 5899,
    cardId: 99881,
    productCategory: "C",
    cardNetwork: "visa",
    cardType: "credit",
    deviceType: "desktop",
    deviceInfo: "Unrecognized Device",

    fraud: 0.88,
    anomaly: 0.71,
    entity: 0.69,

    decision: "BLOCK",
  },
];


// ============================================================
// BUILD PRESENTATION RECORDS
// ============================================================

export const DEMO_HISTORY_RECORDS =
  DEMO_HISTORY.map((item, index) => {
    const riskScore =
      computeRiskScore(
        item.fraud,
        item.anomaly,
        item.entity
      );

    const level =
      levelFromScore(riskScore);

    const decision =
      decisionFromScore(riskScore);

    return buildResult({
      id:
        `TXN-DEMO${String(index + 1).padStart(4, "0")}`,

      timestamp: new Date(
        Date.now() -
          (index + 1) *
            15 *
            60 *
            1000
      ).toISOString(),

      input: {
        amount: item.amount,

        transactionDT: 12192900,

        timestamp: new Date().toISOString(),

        cardId: item.cardId,

        productCategory:
          item.productCategory,

        cardNetwork:
          item.cardNetwork,

        cardType:
          item.cardType,

        deviceType:
          item.deviceType,

        deviceInfo:
          item.deviceInfo,

        billingAddress: {
          line1: "",
          city: "",
          state: "",
          zip: "",
          country: null,
        },

        advanced: {
          card2: null,
          addr2: null,
          d7: null,
          d12: null,
          d13: null,
          d14: null,
        },
      },

      fraudProbability:
        item.fraud,

      anomalyScore:
        item.anomaly,

      entityRisk:
        item.entity,

      riskScoreOverride:
        item.score !== undefined
          ? item.score
          : undefined,

      shapFactors:
        DEMO_SHAP_LOW,

      anomaly: {
        ...DEMO_ANOMALY_LOW,

        score:
          item.anomaly,

        level,
      },

      entity: {
        ...DEMO_ENTITY_LOW,

        cardRisk:
          item.entity,
      },

      gemini: {
        ...DEMO_GEMINI_LOW,

        summary:
          decision === "BLOCK"
            ? "This transaction shows a high-risk profile and would be blocked by the TRACE policy."
            : decision === "REVIEW"
              ? "This transaction shows moderate risk and would be routed for review."
              : DEMO_GEMINI_LOW.summary,
      },
    });
  });


// ============================================================
// ALL DEMO RECORDS
// ============================================================

export const ALL_DEMO_RECORDS = [
  DEMO_RESULT,
  VERIFIED_BLOCK_RESULT,
  ...DEMO_HISTORY_RECORDS,
];


// ============================================================
// HELPER
// ============================================================

export function createDemoRecordId() {
  return generateTxnId();
}
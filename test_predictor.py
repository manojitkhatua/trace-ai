import sys
from pathlib import Path

import pandas as pd

# ------------------------------------------------------------
# Project path
# ------------------------------------------------------------

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# ------------------------------------------------------------
# TRACE components
# ------------------------------------------------------------

from models.predictor import FraudPredictor
from backend.risk_engine import RiskEngine
from backend.decision_engine import DecisionEngine


# ------------------------------------------------------------
# Initialize
# ------------------------------------------------------------

predictor = FraudPredictor(
    ROOT / "models" / "lightgbm_final.pkl",
    ROOT / "models" / "lightgbm_config.json",
    ROOT / "models" / "preprocessing",
)

risk_engine = RiskEngine()
decision_engine = DecisionEngine()


# ------------------------------------------------------------
# Test transaction
# ------------------------------------------------------------

test_data = {
    "TransactionAmt": 10000,
    "TransactionDT": 12192900,
    "card1": 88213,
    "card2": None,
    "addr1": 999,
    "addr2": None,
    "D7": None,
    "D12": None,
    "D13": None,
    "D14": None,
    "DeviceInfo": "Unrecognized Device",
    "ProductCD": "C",
    "card4": "visa",
    "card6": "credit",
    "DeviceType": "mobile",
}


# ------------------------------------------------------------
# Prediction
# ------------------------------------------------------------

transaction = pd.DataFrame([test_data])

print("\nRunning TRACE prediction...\n")

result = predictor.predict(transaction)

print("=== MODEL OUTPUT ===")
print("Fraud Probability :", result["fraud_probability"])
print("Anomaly Score     :", result["anomaly_score"])
print("Entity Risk       :", result["entity_risk"])


# ------------------------------------------------------------
# Risk Engine
# ------------------------------------------------------------

risk = risk_engine.calculate(
    result["fraud_probability"],
    result["anomaly_score"],
    result["entity_risk"],
)

print("\n=== RISK ENGINE ===")
print("Risk Score        :", risk["risk_score"])
print("Risk Level        :", risk["risk_level"])
print("Risk Components   :", risk["risk_components"])


# ------------------------------------------------------------
# Decision Engine
# ------------------------------------------------------------

decision = decision_engine.decide(
    risk["risk_score"]
)

print("\n=== DECISION ===")
print("Decision          :", decision["decision"])
print("Risk Level        :", decision["risk_level"])
print("Risk Score        :", decision["risk_score"])


# ------------------------------------------------------------
# Final
# ------------------------------------------------------------

print("\n==============================")
print("TRACE FINAL RESULT")
print("==============================")
print(f"Fraud Probability : {result['fraud_probability']:.4f}")
print(f"Anomaly Score     : {result['anomaly_score']:.4f}")
print(f"Entity Risk       : {result['entity_risk']:.4f}")
print(f"Risk Score        : {risk['risk_score']:.2f}")
print(f"Risk Level        : {decision['risk_level']}")
print(f"Decision          : {decision['decision']}")
print("==============================\n")
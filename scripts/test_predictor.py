from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from models.predictor import FraudPredictor
from backend.risk_engine import RiskEngine
from backend.decision_engine import DecisionEngine


# ------------------------------------------------------------
# TRACE model setup
# ------------------------------------------------------------

predictor = FraudPredictor(
    ROOT / "models" / "lightgbm_final.pkl",
    ROOT / "models" / "lightgbm_config.json",
    ROOT / "models" / "preprocessing",
)

risk_engine = RiskEngine()
decision_engine = DecisionEngine()


# ------------------------------------------------------------
# Base transaction
# Only use values accepted by the current backend.
# ------------------------------------------------------------

BASE = {
    "TransactionDT": 12192900,
    "card1": 9300,
    "card2": 103,
    "addr1": 315,
    "addr2": None,
    "D7": None,
    "D12": None,
    "D13": None,
    "D14": None,
    "DeviceInfo": None,
    "ProductCD": "C",
    "card4": "visa",
    "card6": "credit",
    "DeviceType": None,
}


# ------------------------------------------------------------
# Controlled test grid
# ------------------------------------------------------------

amounts = [20, 50, 100, 250, 500, 1000, 2000, 3500, 5000, 7500, 10000]
products = ["C", "H", "R", "S", "W"]
devices = [
    (None, None),
    ("mobile", "Android Device"),
    ("desktop", "Windows 10"),
    ("mobile", "Unrecognized Device"),
]

cases = []

for amount in amounts:
    for product in products:
        for device_type, device_info in devices:
            tx = BASE.copy()
            tx["TransactionAmt"] = amount
            tx["ProductCD"] = product
            tx["DeviceType"] = device_type
            tx["DeviceInfo"] = device_info
            cases.append(tx)


# ------------------------------------------------------------
# Run predictions
# ------------------------------------------------------------

results = []

print(f"Testing {len(cases)} transactions...\n")

for i, tx in enumerate(cases, start=1):
    try:
        df = pd.DataFrame([tx])
        prediction = predictor.predict(df)

        risk = risk_engine.calculate(
            prediction["fraud_probability"],
            prediction["anomaly_score"],
            prediction["entity_risk"],
        )

        decision = decision_engine.decide(risk["risk_score"])

        results.append({
            "case": i,
            "amount": tx["TransactionAmt"],
            "product": tx["ProductCD"],
            "device_type": tx["DeviceType"],
            "device_info": tx["DeviceInfo"],
            "card1": tx["card1"],
            "card2": tx["card2"],
            "addr1": tx["addr1"],
            "fraud_probability": prediction["fraud_probability"],
            "anomaly_score": prediction["anomaly_score"],
            "entity_risk": prediction["entity_risk"],
            "risk_score": risk["risk_score"],
            "risk_level": decision["risk_level"],
            "decision": decision["decision"],
        })

        if i % 25 == 0:
            print(f"Processed {i}/{len(cases)}")

    except Exception as exc:
        print(f"Case {i} failed: {exc}")


# ------------------------------------------------------------
# Sort by highest TRACE risk
# ------------------------------------------------------------

results_df = pd.DataFrame(results)

if results_df.empty:
    raise RuntimeError("No predictions were produced.")

results_df = results_df.sort_values(
    "risk_score",
    ascending=False
).reset_index(drop=True)


# ------------------------------------------------------------
# Display top cases
# ------------------------------------------------------------

print("\n" + "=" * 100)
print("TOP 15 HIGHEST-RISK TRACE CASES")
print("=" * 100)

columns = [
    "case",
    "amount",
    "product",
    "device_type",
    "device_info",
    "fraud_probability",
    "anomaly_score",
    "entity_risk",
    "risk_score",
    "risk_level",
    "decision",
]

for _, row in results_df.head(15).iterrows():
    print(
        f"\nCase {int(row['case'])}"
        f"\nAmount:             {row['amount']}"
        f"\nProductCD:          {row['product']}"
        f"\nDeviceType:         {row['device_type']}"
        f"\nDeviceInfo:         {row['device_info']}"
        f"\nFraud Probability:  {row['fraud_probability']:.4f}"
        f"\nAnomaly Score:      {row['anomaly_score']:.4f}"
        f"\nEntity Risk:        {row['entity_risk']:.4f}"
        f"\nTRACE Risk Score:   {row['risk_score']:.2f}"
        f"\nRisk Level:         {row['risk_level']}"
        f"\nDecision:           {row['decision']}"
    )


# ------------------------------------------------------------
# Show whether all three states were found
# ------------------------------------------------------------

print("\n" + "=" * 100)
print("STATE SUMMARY")
print("=" * 100)

for decision in ["ALLOW", "REVIEW", "BLOCK"]:
    subset = results_df[results_df["decision"] == decision]

    if subset.empty:
        print(f"{decision}: NOT FOUND")
    else:
        best = subset.iloc[0]
        print(
            f"{decision}: FOUND | "
            f"Risk={best['risk_score']:.2f} | "
            f"Amount={best['amount']} | "
            f"Product={best['product']} | "
            f"Device={best['device_type']} / {best['device_info']}"
        )


# ------------------------------------------------------------
# Save results
# ------------------------------------------------------------

output = ROOT / "scripts" / "trace_test_results.csv"
results_df.to_csv(output, index=False)

print(f"\nFull results saved to:\n{output}")

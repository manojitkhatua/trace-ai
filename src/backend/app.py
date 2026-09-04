from pathlib import Path
import sys

import pandas as pd
from flask import Flask, jsonify, request

# ------------------------------------------------------------
# Project path
# ------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

# ------------------------------------------------------------
# TRACE components
# ------------------------------------------------------------

from models.predictor import FraudPredictor
from backend.risk_engine import RiskEngine
from backend.decision_engine import DecisionEngine
from backend.audit_logger import AuditLogger
from backend.gemini_service import GeminiService


# ------------------------------------------------------------
# Initialize components
# ------------------------------------------------------------

predictor = FraudPredictor(
    ROOT / "models" / "lightgbm_final.pkl",
    ROOT / "models" / "lightgbm_config.json",
    ROOT / "models" / "preprocessing",
)

risk_engine = RiskEngine()
decision_engine = DecisionEngine()
audit_logger = AuditLogger()
gemini_service = GeminiService()

app = Flask(__name__)


# ------------------------------------------------------------
# Health check
# ------------------------------------------------------------

@app.get("/")
def home():
    return jsonify({
        "status": "ok",
        "service": "TRACE Fraud Detection API",
    })


# ------------------------------------------------------------
# Fraud prediction
# ------------------------------------------------------------

@app.post("/predict")
def predict():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "error": "Request body must contain JSON."
            }), 400

        transaction = pd.DataFrame([data])

        # 1. ML + SHAP + anomaly + entity intelligence
        result = predictor.predict(transaction)

        # 2. Unified risk score
        result.update(
            risk_engine.calculate(
                result["fraud_probability"],
                result["anomaly_score"],
                result["entity_risk"],
            )
        )

        # 3. Operational decision
        result.update(
            decision_engine.decide(
                result["risk_score"]
            )
        )

        # 4. Gemini explanation
        evidence = {
            "fraud_probability": result["fraud_probability"],
            "anomaly_score": result["anomaly_score"],
            "entity_risk": result["entity_risk"],
            "risk_score": result["risk_score"],
            "risk_level": result["risk_level"],
            "decision": result["decision"],
            "reasons": result["reasons"],
            "anomaly_signals": result["anomaly_signals"],
            "entity_breakdown": result["entity_breakdown"],
        }

        try:
            result["gemini_explanation"] = (
                gemini_service.explain(evidence)
            )
        except Exception:
            result["gemini_explanation"] = (
                "AI explanation unavailable. "
                "TRACE decision remains valid."
            )

        # 5. Audit trail
        audit_logger.log(data, result)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# ------------------------------------------------------------
# Run
# ------------------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
from pathlib import Path
import sys

import os
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
import re

# ============================================================
# Project path
# ============================================================

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# ============================================================
# TRACE components
# ============================================================

from models.predictor import FraudPredictor
from backend.risk_engine import RiskEngine
from backend.decision_engine import DecisionEngine
from backend.audit_logger import AuditLogger
from backend.gemini_service import GeminiService

# ============================================================
# Initialize TRACE
# ============================================================

predictor = FraudPredictor(
    ROOT / "models" / "lightgbm_final.pkl",
    ROOT / "models" / "lightgbm_config.json",
    ROOT / "models" / "preprocessing",
)

risk_engine = RiskEngine()
decision_engine = DecisionEngine()
audit_logger = AuditLogger()
gemini_service = GeminiService()

# ============================================================
# Flask application
# ============================================================

app = Flask(__name__)

# Allow the React/Vite frontend to communicate with Flask
CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                re.compile(r"^https://.*\.vercel\.app$"),
            ]
        }
    },
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)
# ============================================================
# Health check
# ============================================================

@app.get("/")
def home():
    return jsonify({
        "status": "ok",
        "service": "TRACE Fraud Detection API",
    }), 200


# ============================================================
# Prediction endpoint
# ============================================================

@app.post("/predict")
def predict():
    try:
        print("STEP 1: /predict received", flush=True)

        data = request.get_json(silent=True)

        if not isinstance(data, dict) or not data:
            return jsonify({
                "error": "Request body must contain valid JSON."
            }), 400

        transaction = pd.DataFrame([data])

        print("STEP 2: starting predictor", flush=True)

        result = predictor.predict(transaction)

        print(
            f"STEP 3: predictor finished | fraud={result.get('fraud_probability')}",
            flush=True
        )

        risk_result = risk_engine.calculate(
            result["fraud_probability"],
            result["anomaly_score"],
            result["entity_risk"],
        )

        result.update(risk_result)

        print(
            f"STEP 4: risk engine finished | risk={result.get('risk_score')}",
            flush=True
        )

        decision_result = decision_engine.decide(
            result["risk_score"]
        )

        result.update(decision_result)

        print(
            f"STEP 5: decision finished | decision={result.get('decision')}",
            flush=True
        )

        evidence = {
            "fraud_probability": result["fraud_probability"],
            "anomaly_score": result["anomaly_score"],
            "entity_risk": result["entity_risk"],
            "risk_score": result["risk_score"],
            "risk_level": result["risk_level"],
            "decision": result["decision"],
            "reasons": result.get("reasons", []),
            "anomaly_signals": result.get("anomaly_signals", []),
            "entity_breakdown": result.get("entity_breakdown", {}),
        }

        print("STEP 6: starting Gemini", flush=True)

        try:
            result["gemini_explanation"] = gemini_service.explain(
                evidence
            )
            print("STEP 7: Gemini finished", flush=True)

        except Exception as gemini_error:
            print(
                f"STEP 7: Gemini failed: {gemini_error}",
                flush=True
            )

            result["gemini_explanation"] = (
                "AI explanation unavailable. "
                "TRACE decision remains valid."
            )

        print("STEP 8: audit logging", flush=True)

        try:
            audit_logger.log(data, result)
        except Exception as audit_error:
            result["audit_warning"] = str(audit_error)

        print("STEP 9: returning response", flush=True)

        return jsonify(result), 200

    except Exception as e:
        print(f"TRACE ERROR: {e}", flush=True)

        return jsonify({
            "error": str(e)
        }), 500

# ============================================================
# Run server
# ============================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
    )
from pathlib import Path
import sys

import pandas as pd
from flask import Flask, jsonify, request
import traceback

# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


# ============================================================
# IMPORTS
# ============================================================

from models.predictor import FraudPredictor
from backend.risk_engine import RiskEngine
from backend.decision_engine import DecisionEngine


# ============================================================
# MODEL CONFIGURATION
# ============================================================

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "lightgbm_final.pkl"
)

CONFIG_PATH = (
    PROJECT_ROOT
    / "models"
    / "lightgbm_config.json"
)

PREPROCESSING_PATH = (
    PROJECT_ROOT
    / "models"
    / "preprocessing"
)


# ============================================================
# LOAD TRACE COMPONENTS
# ============================================================

predictor = FraudPredictor(
    model_path=MODEL_PATH,
    config_path=CONFIG_PATH,
    preprocessing_path=PREPROCESSING_PATH,
)

risk_engine = RiskEngine(
    fraud_weight=0.55,
    anomaly_weight=0.20,
    entity_weight=0.25,
)

decision_engine = DecisionEngine(
    review_threshold=40.0,
    block_threshold=70.0,
)


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def home():
    return jsonify({
        "status": "ok",
        "service": "TRACE Fraud Detection API",
    })


# ============================================================
# PREDICT
# ============================================================

@app.post("/predict")
def predict():

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "Request body must contain JSON."
            }), 400

        transaction = pd.DataFrame([data])

        # ----------------------------------------------------
        # 1. ML + SHAP + ANOMALY
        # ----------------------------------------------------

        model_result = predictor.predict(
            transaction
        )

        fraud_probability = model_result[
            "fraud_probability"
        ]

        anomaly_score = model_result[
            "anomaly_score"
        ]

        anomaly_level = model_result[
            "anomaly_level"
        ]

        anomaly_signals = model_result[
            "anomaly_signals"
        ]

        anomaly_components = model_result[
            "anomaly_components"
        ]

        # ----------------------------------------------------
        # 2. ENTITY RISK
        #
        # Entity risk is calculated inside the predictor
        # in the next integration step.
        # For now, fail clearly rather than silently inventing it.
        # ----------------------------------------------------

        entity_risk = model_result.get(
            "entity_risk"
        )

        entity_level = model_result.get(
            "entity_level"
        )

        entity_breakdown = model_result.get(
            "entity_breakdown"
        )

        if entity_risk is None:
            raise RuntimeError(
                "Entity Risk Engine is not yet integrated "
                "into FraudPredictor."
            )

        # ----------------------------------------------------
        # 3. UNIFIED RISK
        # ----------------------------------------------------

        risk_result = risk_engine.calculate(
            fraud_probability=fraud_probability,
            anomaly_score=anomaly_score,
            entity_risk=entity_risk,
        )

        risk_score = risk_result[
            "risk_score"
        ]

        risk_level = risk_result[
            "risk_level"
        ]

        # ----------------------------------------------------
        # 4. DECISION
        # ----------------------------------------------------

        decision_result = decision_engine.decide(
            risk_score
        )

        # ----------------------------------------------------
        # 5. FINAL RESPONSE
        # ----------------------------------------------------

        return jsonify({
            "fraud_probability": fraud_probability,
            "prediction": model_result["prediction"],
            "threshold": model_result["threshold"],

            "anomaly_score": anomaly_score,
            "anomaly_level": anomaly_level,
            "anomaly_signals": anomaly_signals,
            "anomaly_components": anomaly_components,

            "entity_risk": entity_risk,
            "entity_level": entity_level,
            "entity_breakdown": entity_breakdown,

            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_components": risk_result[
                "risk_components"
            ],
            "risk_weights": risk_result[
                "risk_weights"
            ],

            "decision": decision_result[
                "decision"
            ],

            "reasons": model_result[
                "reasons"
            ],
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
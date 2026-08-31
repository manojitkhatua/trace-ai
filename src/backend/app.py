from pathlib import Path
import sys

import pandas as pd
from flask import Flask, request, jsonify


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


# --------------------------------------------------
# Imports
# --------------------------------------------------

from models.predictor import FraudPredictor
from backend.decision_engine import DecisionEngine


# --------------------------------------------------
# Model paths
# --------------------------------------------------

MODEL_PATH = PROJECT_ROOT / "models" / "lightgbm_final.pkl"
CONFIG_PATH = PROJECT_ROOT / "models" / "lightgbm_config.json"
PREPROCESSING_PATH = PROJECT_ROOT / "models" / "preprocessing"


# --------------------------------------------------
# Initialize ML predictor
# --------------------------------------------------

predictor = FraudPredictor(
    MODEL_PATH,
    CONFIG_PATH,
    PREPROCESSING_PATH
)


# --------------------------------------------------
# Initialize decision engine
# --------------------------------------------------

decision_engine = DecisionEngine(
    review_threshold=0.20,
    block_threshold=0.70
)


# --------------------------------------------------
# Flask application
# --------------------------------------------------

app = Flask(__name__)


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "service": "TRACE Fraud Detection API"
    })


# --------------------------------------------------
# Prediction endpoint
# --------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "Request body is empty."
            }), 400

        transaction = pd.DataFrame([data])

        # ML prediction + SHAP explanation
        result = predictor.predict(transaction)

        # Operational decision
        decision = decision_engine.decide(
            result["fraud_probability"]
        )

        # Combine results
        result.update(decision)

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# --------------------------------------------------
# Run application
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
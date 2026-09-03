from __future__ import annotations

from typing import Any, Dict

import numpy as np


class RiskEngine:
    """
    Combines independent TRACE risk signals into one operational risk score.

    IMPORTANT:
    This is an operational score, not a calibrated probability.
    LightGBM fraud_probability remains the actual ML model output.
    """

    def __init__(
        self,
        fraud_weight: float = 0.55,
        anomaly_weight: float = 0.20,
        entity_weight: float = 0.25,
    ):
        weights = {
            "fraud": fraud_weight,
            "anomaly": anomaly_weight,
            "entity": entity_weight,
        }

        total = sum(weights.values())

        if total <= 0:
            raise ValueError("Risk weights must sum to a positive value.")

        # Normalize weights automatically.
        self.weights = {
            key: value / total
            for key, value in weights.items()
        }

    @staticmethod
    def _clip(value: float) -> float:
        return float(np.clip(value, 0.0, 1.0))

    def calculate(
        self,
        fraud_probability: float,
        anomaly_score: float,
        entity_risk: float,
    ) -> Dict[str, Any]:

        fraud_probability = self._clip(
            float(fraud_probability)
        )

        anomaly_score = self._clip(
            float(anomaly_score)
        )

        entity_risk = self._clip(
            float(entity_risk)
        )

        # Weighted operational risk.
        combined_risk = (
            self.weights["fraud"] * fraud_probability
            + self.weights["anomaly"] * anomaly_score
            + self.weights["entity"] * entity_risk
        )

        combined_risk = self._clip(combined_risk)

        risk_score = round(
            combined_risk * 100,
            2
        )

        if risk_score >= 70:
            risk_level = "HIGH"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_components": {
                "fraud_probability": round(
                    fraud_probability,
                    4
                ),
                "anomaly_score": round(
                    anomaly_score,
                    4
                ),
                "entity_risk": round(
                    entity_risk,
                    4
                ),
            },
            "risk_weights": {
                key: round(value, 4)
                for key, value in self.weights.items()
            },
        }
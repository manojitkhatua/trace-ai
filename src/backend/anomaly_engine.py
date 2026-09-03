from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd


class AnomalyEngine:
    """
    Behavioral anomaly scorer for TRACE.

    This is intentionally separate from the supervised fraud model.
    It scores how unusual a transaction's behavioral features are
    relative to statistics learned from the training split.

    Expected config format:
    {
        "features": {
            "log_transaction_amount": {
                "type": "continuous",
                "q01": ...,
                "q25": ...,
                "median": ...,
                "q75": ...,
                "q99": ...
            },
            "card1_transaction_count": {...},
            ...
        },
        "weights": {
            "amount": 0.30,
            "entity": 0.55,
            "missingness": 0.15
        }
    }
    """

    DEFAULT_FEATURE_GROUPS = {
        "amount": [
            "log_transaction_amount",
            "TransactionAmt",
        ],
        "entity": [
            "card1_transaction_count",
            "card2_transaction_count",
            "addr1_transaction_count",
            "card1_DeviceInfo_transaction_count",
            "card1_unique_DeviceInfo_count",
            "DeviceInfo_unique_card1_count",
        ],
        "missingness": [
            "addr1_missing",
            "addr2_missing",
            "D7_missing",
            "D12_missing",
            "D13_missing",
            "D14_missing",
            "DeviceInfo_missing",
        ],
    }

    def __init__(
        self,
        config_path: Optional[str | Path] = None,
        weights: Optional[Dict[str, float]] = None,
    ) -> None:
        project_root = Path(__file__).resolve().parents[2]

        if config_path is None:
            config_path = project_root / "models" / "anomaly_config.json"

        self.config_path = Path(config_path)

        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Anomaly configuration not found: {self.config_path}. "
                "Create anomaly_config.json from the training split before "
                "using the AnomalyEngine."
            )

        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        configured_weights = self.config.get("weights", {})
        self.weights = weights or {
            "amount": float(configured_weights.get("amount", 0.30)),
            "entity": float(configured_weights.get("entity", 0.55)),
            "missingness": float(configured_weights.get("missingness", 0.15)),
        }

        total = sum(self.weights.values())
        if total <= 0:
            raise ValueError("Anomaly weights must sum to a positive value.")

        # Normalize so configuration remains flexible.
        self.weights = {k: v / total for k, v in self.weights.items()}

    @staticmethod
    def _clip01(value: float) -> float:
        return float(np.clip(value, 0.0, 1.0))

    @staticmethod
    def _continuous_score(value: float, stats: Dict[str, Any]) -> float:
        """
        Convert distance from the training median into [0, 1].

        IQR is used instead of standard deviation because transaction
        distributions are typically skewed and heavy-tailed.
        """
        if value is None or pd.isna(value):
            return 1.0

        median = float(stats.get("median", 0.0))
        q25 = float(stats.get("q25", median))
        q75 = float(stats.get("q75", median))
        q01 = float(stats.get("q01", q25))
        q99 = float(stats.get("q99", q75))

        iqr = max(q75 - q25, 1e-6)
        robust_z = abs(float(value) - median) / iqr

        # Saturating transformation: normal-ish values stay low,
        # extreme values approach 1.
        score = 1.0 - np.exp(-robust_z / 3.0)

        # Extra tail emphasis when outside the empirical 1%-99% range.
        if float(value) < q01 or float(value) > q99:
            score = max(score, 0.80)

        return AnomalyEngine._clip01(score)

    @staticmethod
    def _binary_score(value: Any, stats: Dict[str, Any]) -> float:
        """
        Score how rare the observed 0/1 state is in training data.

        Config should contain:
            "frequency_1": fraction of training rows where value == 1
        """
        if value is None or pd.isna(value):
            return 1.0

        frequency_1 = float(stats.get("frequency_1", 0.5))
        frequency_1 = float(np.clip(frequency_1, 0.0, 1.0))

        observed = 1 if int(value) == 1 else 0
        state_frequency = frequency_1 if observed else (1.0 - frequency_1)

        # Rare states get high anomaly scores.
        return AnomalyEngine._clip01(1.0 - state_frequency)

    def _feature_score(self, feature_name: str, value: Any) -> Optional[float]:
        stats = self.config.get("features", {}).get(feature_name)
        if stats is None:
            return None

        feature_type = stats.get("type", "continuous")

        if feature_type == "binary":
            return self._binary_score(value, stats)

        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            return None

        return self._continuous_score(numeric_value, stats)

    def score(self, features: Dict[str, Any] | pd.Series | pd.DataFrame) -> Dict[str, Any]:
        """
        Score one engineered transaction.

        `features` may be:
        - a dictionary
        - a pandas Series
        - a one-row DataFrame

        Returns:
            anomaly_score: 0-1
            anomaly_level: LOW / MEDIUM / HIGH
            signals: human-readable anomaly signals
            components: detailed component scores
        """
        if isinstance(features, pd.DataFrame):
            if len(features) != 1:
                raise ValueError("AnomalyEngine.score expects exactly one row.")
            row = features.iloc[0].to_dict()
        elif isinstance(features, pd.Series):
            row = features.to_dict()
        elif isinstance(features, dict):
            row = features
        else:
            raise TypeError(
                "features must be a dict, pandas Series, or one-row DataFrame."
            )

        group_scores: Dict[str, list[float]] = {
            "amount": [],
            "entity": [],
            "missingness": [],
        }

        signal_candidates = []

        for group, feature_names in self.DEFAULT_FEATURE_GROUPS.items():
            for feature_name in feature_names:
                if feature_name not in row:
                    continue

                score = self._feature_score(feature_name, row[feature_name])
                if score is None:
                    continue

                group_scores[group].append(score)

                if score >= 0.70:
                    signal_candidates.append(
                        {
                            "feature": feature_name,
                            "score": round(score, 4),
                            "group": group,
                            "value": row[feature_name],
                        }
                    )

        component_scores = {
            group: (
                float(np.mean(values)) if values else 0.0
            )
            for group, values in group_scores.items()
        }

        active_weights = {
            group: self.weights[group]
            for group, values in group_scores.items()
            if values
        }

        if not active_weights:
            raise ValueError(
                "No supported anomaly features were found in the input."
            )

        weight_total = sum(active_weights.values())

        anomaly_score = sum(
            component_scores[group] * weight
            for group, weight in active_weights.items()
        ) / weight_total

        anomaly_score = round(self._clip01(anomaly_score), 4)

        if anomaly_score >= 0.70:
            anomaly_level = "HIGH"
        elif anomaly_score >= 0.40:
            anomaly_level = "MEDIUM"
        else:
            anomaly_level = "LOW"

        signal_candidates.sort(key=lambda item: item["score"], reverse=True)

        signals = [
            self._humanize_signal(item["feature"], item["group"])
            for item in signal_candidates[:5]
        ]

        return {
            "anomaly_score": anomaly_score,
            "anomaly_level": anomaly_level,
            "signals": signals,
            "components": {
                key: round(value, 4)
                for key, value in component_scores.items()
            },
        }

    @staticmethod
    def _humanize_signal(feature: str, group: str) -> str:
        names = {
            "log_transaction_amount": "Transaction amount is unusually high or low",
            "TransactionAmt": "Transaction amount is unusual",
            "card1_transaction_count": "Card transaction frequency is unusual",
            "card2_transaction_count": "Secondary card activity is unusual",
            "addr1_transaction_count": "Billing/address activity is unusual",
            "card1_DeviceInfo_transaction_count": "Card-device activity is unusual",
            "card1_unique_DeviceInfo_count": "Card is associated with an unusual number of devices",
            "DeviceInfo_unique_card1_count": "Device is associated with an unusual number of cards",
            "addr1_missing": "Address availability pattern is unusual",
            "addr2_missing": "Secondary address availability pattern is unusual",
            "D7_missing": "D7 availability pattern is unusual",
            "D12_missing": "D12 availability pattern is unusual",
            "D13_missing": "D13 availability pattern is unusual",
            "D14_missing": "D14 availability pattern is unusual",
            "DeviceInfo_missing": "Device information availability pattern is unusual",
        }

        return names.get(
            feature,
            f"Unusual {group} behavior detected ({feature})",
        )

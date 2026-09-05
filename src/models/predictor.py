import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.anomaly_engine import AnomalyEngine
from backend.entity_risk_engine import EntityRiskEngine


class FraudPredictor:
    def __init__(
        self,
        model_path,
        config_path,
        preprocessing_path,
        anomaly_config_path=None,
    ):
        preprocessing_path = Path(preprocessing_path)
        root = Path(__file__).resolve().parents[2]

        # --------------------------------------------------
        # Load model
        # --------------------------------------------------
        self.model = joblib.load(model_path)

        # IMPORTANT:
        # SHAP explainer is created lazily only when requested.
        # This keeps the live prediction path lightweight.
        self.explainer = None

        # --------------------------------------------------
        # Load model configuration
        # --------------------------------------------------
        self.config = json.loads(
            Path(config_path).read_text()
        )

        self.threshold = float(
            self.config["threshold"]
        )

        # --------------------------------------------------
        # Load preprocessing artifacts
        # --------------------------------------------------
        self.entity_maps = joblib.load(
            preprocessing_path / "entity_maps.pkl"
        )

        self.pair_map = joblib.load(
            preprocessing_path / "pair_map.pkl"
        )

        self.card_device_map = joblib.load(
            preprocessing_path / "card_device_map.pkl"
        )

        self.device_card_map = joblib.load(
            preprocessing_path / "device_card_map.pkl"
        )

        self.encoder = joblib.load(
            preprocessing_path / "onehot_encoder.pkl"
        )

        self.feature_config = joblib.load(
            preprocessing_path / "feature_config.pkl"
        )

        self.temporal_config = joblib.load(
            preprocessing_path / "temporal_config.pkl"
        )

        # --------------------------------------------------
        # Feature configuration
        # --------------------------------------------------
        self.numeric_features = list(
            self.feature_config["numeric_features"]
        )

        self.categorical_features = list(
            self.feature_config["categorical_features"]
        )

        self.encoded_feature_names = list(
            self.feature_config["encoded_feature_names"]
        )

        self.expected_features = (
            self.numeric_features
            + self.encoded_feature_names
        )

        # --------------------------------------------------
        # Anomaly engine
        # --------------------------------------------------
        self.anomaly_engine = AnomalyEngine(
            anomaly_config_path
            or root / "models" / "anomaly_config.json"
        )

        # --------------------------------------------------
        # Entity risk engine
        # --------------------------------------------------
        self.entity_risk_engine = EntityRiskEngine(
            self.entity_maps,
            self.pair_map,
            self.card_device_map,
            self.device_card_map,
        )

    # ======================================================
    # Input validation
    # ======================================================

    def _validate_input(self, df):
        required = {
            "TransactionAmt",
            "TransactionDT",
            "card1",
            "card2",
            "addr1",
            "addr2",
            "D7",
            "D12",
            "D13",
            "D14",
            "DeviceInfo",
            "ProductCD",
            "card4",
            "card6",
            "DeviceType",
        }

        if not isinstance(df, pd.DataFrame) or len(df) != 1:
            raise ValueError(
                "Predictor expects one transaction DataFrame."
            )

        missing = sorted(
            required - set(df.columns)
        )

        if missing:
            raise ValueError(
                f"Missing columns: {missing}"
            )

    # ======================================================
    # Feature creation
    # ======================================================

    def _create_features(self, df):
        self._validate_input(df)

        df = df.copy()

        # Transaction amount
        df["log_transaction_amount"] = np.log1p(
            df["TransactionAmt"]
        )

        # Missingness indicators
        missing_cols = [
            "addr1",
            "addr2",
            "D7",
            "D12",
            "D13",
            "D14",
            "DeviceInfo",
        ]

        for col in missing_cols:
            df[f"{col}_missing"] = (
                df[col]
                .isna()
                .astype("int8")
            )

        # Temporal feature
        df["time_since_previous_transaction"] = (
            df["TransactionDT"]
            - self.temporal_config[
                "previous_transaction_dt"
            ]
        )

        df["has_previous_transaction"] = 1

        # Entity counts
        for col, mapping in self.entity_maps.items():
            df[f"{col}_transaction_count"] = (
                df[col]
                .map(mapping)
                .fillna(0)
                .astype("int32")
            )

        # card1 + DeviceInfo relationship
        pair_index = pd.MultiIndex.from_frame(
            df[["card1", "DeviceInfo"]]
        )

        df["card1_DeviceInfo_transaction_count"] = (
            pair_index
            .map(self.pair_map)
            .fillna(0)
            .astype("int32")
        )

        # Card → device diversity
        df["card1_unique_DeviceInfo_count"] = (
            df["card1"]
            .map(self.card_device_map)
            .fillna(0)
            .astype("int32")
        )

        # Device → card diversity
        df["DeviceInfo_unique_card1_count"] = (
            df["DeviceInfo"]
            .map(self.device_card_map)
            .fillna(0)
            .astype("int32")
        )

        # Categorical missing values
        df[self.categorical_features] = (
            df[self.categorical_features]
            .fillna("MISSING")
        )

        # One-hot encoding
        categorical = pd.DataFrame(
            self.encoder.transform(
                df[self.categorical_features]
            ),
            columns=self.encoded_feature_names,
            index=df.index,
        )

        # Final feature matrix
        X = pd.concat(
            [
                df[self.numeric_features],
                categorical,
            ],
            axis=1,
        )

        # Exact training-time feature order
        if list(X.columns) != self.expected_features:
            raise ValueError(
                "Feature order does not match training."
            )

        return X

    # ======================================================
    # Optional SHAP explanation
    # ======================================================

    def _get_explainer(self):
        """
        Create SHAP explainer only when explanation
        is explicitly requested.
        """
        if self.explainer is None:
            self.explainer = shap.TreeExplainer(
                self.model
            )

        return self.explainer

    def _shap_reasons(self, X, top_n=5):
        explainer = self._get_explainer()

        shap_values = explainer.shap_values(X)

        if isinstance(shap_values, list):
            values = shap_values[1][0]
        else:
            values = shap_values[0]

        values = np.asarray(values).reshape(-1)

        if len(values) != X.shape[1]:
            raise ValueError(
                f"SHAP/model feature mismatch: "
                f"SHAP returned {len(values)} values, "
                f"but X has {X.shape[1]} features."
            )

        explanation = pd.DataFrame(
            {
                "feature": X.columns.tolist(),
                "value": X.iloc[0].tolist(),
                "shap_value": values,
            }
        )

        explanation["direction"] = np.where(
            explanation["shap_value"] > 0,
            "fraud",
            "legitimate",
        )

        explanation["abs_shap"] = (
            explanation["shap_value"].abs()
        )

        return (
            explanation
            .sort_values(
                "abs_shap",
                ascending=False,
            )
            .head(top_n)
            .to_dict(orient="records")
        )

    # ======================================================
    # Prediction
    # ======================================================

    def predict(
        self,
        transaction,
        include_shap=False,
    ):
        """
        Run TRACE prediction.

        include_shap=False by default so the production
        request stays fast and reliable.

        SHAP can still be requested explicitly when needed.
        """

        X = self._create_features(transaction)

        print(
            "PREDICTOR DEBUG",
            flush=True,
        )

        print(
            "X shape:",
            X.shape,
            flush=True,
        )

        print(
            "X columns:",
            len(X.columns),
            flush=True,
        )

        # --------------------------------------------------
        # 1. Fraud probability
        # --------------------------------------------------
        probability = float(
            self.model.predict_proba(X)[0, 1]
        )

        print(
            "MODEL PREDICTION COMPLETE",
            flush=True,
        )

        # --------------------------------------------------
        # 2. Anomaly score
        # --------------------------------------------------
        anomaly = self.anomaly_engine.score(X)

        print(
            "ANOMALY COMPLETE",
            flush=True,
        )

        # --------------------------------------------------
        # 3. Entity risk
        # --------------------------------------------------
        entity = self.entity_risk_engine.calculate(
            transaction
        )

        print(
            "ENTITY RISK COMPLETE",
            flush=True,
        )

        # --------------------------------------------------
        # 4. Optional SHAP
        # --------------------------------------------------
        reasons = []

        if include_shap:
            print(
                "SHAP STARTING",
                flush=True,
            )

            reasons = self._shap_reasons(X)

            print(
                "SHAP COMPLETE",
                flush=True,
            )

        # --------------------------------------------------
        # 5. Return result
        # --------------------------------------------------
        return {
            "fraud_probability": probability,
            "prediction": int(
                probability >= self.threshold
            ),
            "threshold": self.threshold,

            # Empty during normal live prediction.
            # SHAP can be enabled explicitly.
            "reasons": reasons,

            "anomaly_score": anomaly[
                "anomaly_score"
            ],
            "anomaly_level": anomaly[
                "anomaly_level"
            ],
            "anomaly_signals": anomaly[
                "signals"
            ],
            "anomaly_components": anomaly[
                "components"
            ],

            "entity_risk": entity[
                "entity_risk"
            ],
            "entity_level": entity[
                "entity_level"
            ],
            "entity_breakdown": {
                key: entity[key]
                for key in (
                    "card_risk",
                    "device_risk",
                    "address_risk",
                    "relationship_risk",
                    "network_risk",
                )
            },
        }
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap


class FraudPredictor:
    """Load the final LightGBM model and reproduce training-time preprocessing."""

    def __init__(self, model_path, config_path, preprocessing_path):
        model_path = Path(model_path)
        config_path = Path(config_path)
        preprocessing_path = Path(preprocessing_path)

        self.model = joblib.load(model_path)
        self.explainer = shap.TreeExplainer(self.model)

        with config_path.open("r", encoding="utf-8") as f:
            self.config = json.load(f)

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

        self.threshold = float(self.config["threshold"])
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
            self.numeric_features + self.encoded_feature_names
        )

    def _validate_input(self, df: pd.DataFrame) -> None:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("transaction must be a pandas DataFrame.")

        if len(df) != 1:
            raise ValueError("Predictor expects exactly one transaction at a time.")

        required_columns = {
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

        missing_columns = sorted(required_columns - set(df.columns))
        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}")

    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        self._validate_input(df)
        df = df.copy()

        # Same simple numeric feature used during training.
        df["log_transaction_amount"] = np.log1p(
            df["TransactionAmt"]
        )

        # Same missingness indicators used during training.
        for column in [
            "addr1",
            "addr2",
            "D7",
            "D12",
            "D13",
            "D14",
            "DeviceInfo",
        ]:
            df[f"{column}_missing"] = (
                df[column].isna().astype("int8")
            )

        # Reproduce validation-time temporal logic:
        # first new transaction is measured from the last training transaction.
        previous_time = self.temporal_config[
            "previous_transaction_dt"
        ]
        df["time_since_previous_transaction"] = (
            df["TransactionDT"] - previous_time
        )
        df["has_previous_transaction"] = 1

        # Entity frequency features from training-derived mappings.
        for column, mapping in self.entity_maps.items():
            df[f"{column}_transaction_count"] = (
                df[column]
                .map(mapping)
                .fillna(0)
                .astype("int32")
            )

        # card1 + DeviceInfo pair frequency.
        pair_index = pd.MultiIndex.from_frame(
            df[["card1", "DeviceInfo"]]
        )
        df["card1_DeviceInfo_transaction_count"] = (
            pair_index
            .map(self.pair_map)
            .fillna(0)
            .astype("int32")
        )

        # card1 -> unique DeviceInfo count.
        df["card1_unique_DeviceInfo_count"] = (
            df["card1"]
            .map(self.card_device_map)
            .fillna(0)
            .astype("int32")
        )

        # DeviceInfo -> unique card1 count.
        df["DeviceInfo_unique_card1_count"] = (
            df["DeviceInfo"]
            .map(self.device_card_map)
            .fillna(0)
            .astype("int32")
        )

        # Match training categorical preprocessing.
        for column in self.categorical_features:
            df[column] = df[column].fillna("MISSING")

        X_num = df[self.numeric_features].copy()

        X_cat = self.encoder.transform(
            df[self.categorical_features]
        )
        X_cat = pd.DataFrame(
            X_cat,
            columns=self.encoded_feature_names,
            index=df.index,
        )

        X = pd.concat([X_num, X_cat], axis=1)

        # Exact feature count and order check.
        if len(X.columns) != len(self.expected_features):
            raise ValueError(
                f"Feature count mismatch: generated {len(X.columns)}, "
                f"expected {len(self.expected_features)}."
            )

        if list(X.columns) != self.expected_features:
            raise ValueError("Feature order does not match training.")

        return X

    def predict_proba(self, transaction: pd.DataFrame) -> float:
        X = self._create_features(transaction)
        return float(self.model.predict_proba(X)[:, 1][0])
    def explain_prediction(self, transaction, top_n=5):
        X = self._create_features(transaction)

        shap_values = self.explainer.shap_values(X)

        if isinstance(shap_values, list):
            values = shap_values[1][0]
        else:
            values = shap_values[0]

        feature_names = X.columns.tolist()
        feature_values = X.iloc[0].values

        explanation = pd.DataFrame({
            "feature": feature_names,
            "value": feature_values,
            "shap_value": values
        })

        explanation["direction"] = np.where(
            explanation["shap_value"] > 0,
            "fraud",
            "legitimate"
        )

        explanation["abs_shap"] = explanation["shap_value"].abs()

        explanation = (
            explanation
            .sort_values("abs_shap", ascending=False)
            .head(top_n)
        )

        return {
            "fraud_probability": float(
                self.model.predict_proba(X)[0, 1]
            ),
            "reasons": explanation.to_dict(orient="records")
        }
    def predict(self, transaction):
        probability = self.predict_proba(transaction)

        explanation = self.explain_prediction(
            transaction,
            top_n=5
        )

        return {
            "fraud_probability": probability,
            "prediction": int(probability >= self.threshold),
            "threshold": self.threshold,
            "reasons": explanation["reasons"]
        }
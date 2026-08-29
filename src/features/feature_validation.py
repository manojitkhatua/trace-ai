import numpy as np
import pandas as pd


class FeatureValidator:

    def validate(self, df: pd.DataFrame, features: list[str], target: str = "isFraud"):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame.")
        if not features:
            raise ValueError("features cannot be empty.")

        missing_features = [col for col in features if col not in df.columns]
        if missing_features:
            raise ValueError(f"Missing features: {missing_features}")

        if target in features:
            raise ValueError(f"Target column '{target}' cannot be a feature.")

        if df[features].isna().any().any():
            missing_counts = df[features].isna().sum()
            raise ValueError(
                f"Engineered features contain missing values:\n"
                f"{missing_counts[missing_counts > 0]}"
            )

        numeric_features = df[features].select_dtypes(include="number")

        if np.isinf(numeric_features).any().any():
            raise ValueError("Engineered features contain infinite values.")

        duplicate_features = df[features].columns[
            df[features].columns.duplicated()
        ].tolist()

        if duplicate_features:
            raise ValueError(
                f"Duplicate feature columns found: {duplicate_features}"
            )

        if len(df) == 0:
            raise ValueError("Feature dataset is empty.")

        return True
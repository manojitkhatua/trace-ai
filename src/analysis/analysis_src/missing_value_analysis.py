from abc import ABC, abstractmethod

import pandas as pd


# =========================================================
# ABSTRACT BASE CLASS
# =========================================================

class MissingValueAnalysisStrategy(ABC):
    """
    Abstract base class for missing-value analysis strategies.

    Every concrete strategy must implement the analyze()
    method.
    """

    @abstractmethod
    def analyze(self, df: pd.DataFrame):
        """
        Perform a specific missing-value analysis.

        Parameters:
        df : pd.DataFrame
            DataFrame to analyze.

        Returns:
        pd.DataFrame
            Result of the analysis.
        """
        pass


# =========================================================
# MISSING PERCENTAGE STRATEGY
# =========================================================

class MissingPercentageStrategy(
    MissingValueAnalysisStrategy
):
    """
    Calculates missing-value counts and percentages
    for all columns.
    """

    def analyze(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate missing-value statistics.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to analyze.

        Returns
        -------
        pd.DataFrame
            Missing count and missing percentage
            for each column containing missing values.
        """

        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                "df must be a pandas DataFrame."
            )

        if df.empty:
            raise ValueError(
                "Cannot analyze an empty DataFrame."
            )

        total_rows = len(df)

        missing_count = df.isna().sum()

        result = pd.DataFrame(
            {
                "missing_count": missing_count,
                "missing_percentage": (
                    missing_count
                    / total_rows
                    * 100
                ),
            }
        )

        # Keep only columns that actually contain
        # missing values.
        result = result[
            result["missing_count"] > 0
        ]

        # Sort by amount of missing data.
        result = result.sort_values(
            by="missing_percentage",
            ascending=False,
        )

        print("\nMissing Value Analysis:")
        print(result)

        return result


# =========================================================
# MISSINGNESS VS FRAUD STRATEGY
# =========================================================

class MissingnessVsFraudStrategy(
    MissingValueAnalysisStrategy
):
    """
    Analyzes whether missingness in a feature is
    associated with the fraud target.

    A minimum missing-observation threshold is used
    to prevent extremely small groups from producing
    misleading fraud rates.
    """

    def __init__(
        self,
        min_missing_count: int = 1000
    ):
        """
        Initialize the strategy.

        Parameters
        ----------
        min_missing_count : int, default=1000
            Minimum number of missing observations
            required for a feature to be included.
        """

        if min_missing_count <= 0:
            raise ValueError(
                "min_missing_count must be greater than 0."
            )

        self.min_missing_count = min_missing_count

    def analyze(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compare fraud rates between missing and
        non-missing observations.

        Parameters
        ----------
        df : pd.DataFrame
            Training DataFrame containing isFraud.

        Returns
        -------
        pd.DataFrame
            Missing-count, fraud-count, fraud-rate,
            and fraud-rate difference statistics.
        """

        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                "df must be a pandas DataFrame."
            )

        if df.empty:
            raise ValueError(
                "Cannot analyze an empty DataFrame."
            )

        if "isFraud" not in df.columns:
            raise ValueError(
                "Column 'isFraud' is required."
            )

        # Validate the target.
        if df["isFraud"].isna().any():
            raise ValueError(
                "isFraud contains missing values."
            )

        unique_target_values = set(
            df["isFraud"].unique()
        )

        if not unique_target_values.issubset({0, 1}):
            raise ValueError(
                "isFraud must contain only 0 and 1."
            )

        results = []

        for column in df.columns:

            # Never analyze the target against itself.
            if column == "isFraud":
                continue

            missing_mask = df[column].isna()

            missing_count = int(
                missing_mask.sum()
            )

            # Ignore extremely small missing groups.
            if missing_count < self.min_missing_count:
                continue

            present_mask = ~missing_mask

            present_count = int(
                present_mask.sum()
            )

            missing_fraud_count = int(
                df.loc[
                    missing_mask,
                    "isFraud"
                ].sum()
            )

            present_fraud_count = int(
                df.loc[
                    present_mask,
                    "isFraud"
                ].sum()
            )

            missing_fraud_rate = (
                missing_fraud_count
                / missing_count
            )

            present_fraud_rate = (
                present_fraud_count
                / present_count
                if present_count > 0
                else 0.0
            )

            fraud_rate_difference = (
                missing_fraud_rate
                - present_fraud_rate
            )

            results.append(
                {
                    "feature": column,
                    "missing_count": missing_count,
                    "missing_fraud_count": (
                        missing_fraud_count
                    ),
                    "missing_fraud_rate": (
                        missing_fraud_rate
                    ),
                    "present_count": present_count,
                    "present_fraud_count": (
                        present_fraud_count
                    ),
                    "present_fraud_rate": (
                        present_fraud_rate
                    ),
                    "fraud_rate_difference": (
                        fraud_rate_difference
                    ),
                    "absolute_difference": abs(
                        fraud_rate_difference
                    ),
                }
            )

        result = pd.DataFrame(results)

        if result.empty:

            print(
                "\nNo features met the minimum "
                "missing-observation threshold."
            )

            return result

        # Rank by the magnitude of the fraud-rate
        # difference only after applying the
        # minimum-sample-size filter.
        result = result.sort_values(
            by="absolute_difference",
            ascending=False,
        ).reset_index(drop=True)

        print(
            "\nMissingness vs Fraud Analysis:"
        )

        print(
            f"Minimum missing observations: "
            f"{self.min_missing_count}"
        )

        print(result)

        return result


# =========================================================
# CONTEXT CLASS
# =========================================================

class MissingValueAnalyzer:
    """
    Context class that executes a selected
    missing-value analysis strategy.
    """

    def __init__(
        self,
        strategy: MissingValueAnalysisStrategy
    ):
        """
        Initialize the analyzer with a strategy.
        """

        self.set_strategy(strategy)

    def set_strategy(
        self,
        strategy: MissingValueAnalysisStrategy
    ):
        """
        Set a new missing-value analysis strategy.
        """

        if not isinstance(
            strategy,
            MissingValueAnalysisStrategy
        ):
            raise TypeError(
                "strategy must inherit from "
                "MissingValueAnalysisStrategy."
            )

        self._strategy = strategy

    def execute_analysis(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Execute the current analysis strategy.
        """

        if not isinstance(
            df,
            pd.DataFrame
        ):
            raise TypeError(
                "df must be a pandas DataFrame."
            )

        return self._strategy.analyze(df)


# =========================================================
# MAIN
# =========================================================

def main():
    """
    Main entry point for the module.
    """

    print("=" * 60)
    print("TRACE MISSING VALUE ANALYSIS")
    print("=" * 60)

    print("\nAvailable strategies:")

    print(
        "1. MissingPercentageStrategy"
    )

    print(
        "2. MissingnessVsFraudStrategy"
    )

    print(
        "\nMissingnessVsFraudStrategy uses "
        "a minimum observation threshold."
    )


# =========================================================
# MODULE ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()
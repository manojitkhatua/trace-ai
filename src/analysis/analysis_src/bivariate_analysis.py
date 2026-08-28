from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import pandas as pd


# =========================================================
# ABSTRACT BASE CLASS
# =========================================================

class BivariateAnalysisStrategy(ABC):
    """
    Abstract base class for bivariate analysis strategies.
    """

    @abstractmethod
    def analyze(self, df: pd.DataFrame):
        """
        Perform a specific bivariate analysis.
        """
        pass


# =========================================================
# NUMERICAL FEATURE VS FRAUD
# =========================================================

class NumericalVsFraudStrategy(
    BivariateAnalysisStrategy
):
    """
    Analyze the relationship between a numerical
    feature and the fraud target.
    """

    def __init__(self, column: str):
        self.column = column

    def analyze(self, df: pd.DataFrame):

        required_columns = {
            self.column,
            "isFraud"
        }

        missing_columns = (
            required_columns - set(df.columns)
        )

        if missing_columns:
            raise ValueError(
                f"Missing required columns: "
                f"{missing_columns}"
            )

        if not pd.api.types.is_numeric_dtype(
            df[self.column]
        ):
            raise TypeError(
                f"'{self.column}' must be numerical."
            )

        grouped_statistics = (
            df.groupby("isFraud")[self.column]
            .describe()
        )

        print(
            f"\n{self.column} by Fraud Status:"
        )

        print(grouped_statistics)

        plt.figure(figsize=(8, 5))

        df.boxplot(
            column=self.column,
            by="isFraud"
        )

        plt.title(
            f"{self.column} by Fraud Status"
        )

        plt.suptitle("")

        plt.xlabel("Fraud Status")
        plt.ylabel(self.column)

        plt.tight_layout()
        plt.show()

        return grouped_statistics


# =========================================================
# CATEGORICAL FEATURE VS FRAUD
# =========================================================

class CategoricalVsFraudStrategy(
    BivariateAnalysisStrategy
):
    """
    Analyze fraud rate across categories.
    """

    def __init__(self, column: str):
        self.column = column

    def analyze(self, df: pd.DataFrame):

        required_columns = {
            self.column,
            "isFraud"
        }

        missing_columns = (
            required_columns - set(df.columns)
        )

        if missing_columns:
            raise ValueError(
                f"Missing required columns: "
                f"{missing_columns}"
            )

        fraud_rate = (
            df.groupby(self.column, dropna=False)["isFraud"]
            .agg(
                transaction_count="count",
                fraud_count="sum",
                fraud_rate="mean"
            )
            .sort_values(
                "fraud_rate",
                ascending=False
            )
        )

        print(
            f"\nFraud Rate by {self.column}:"
        )

        print(fraud_rate)

        plt.figure(figsize=(9, 5))

        fraud_rate["fraud_rate"].plot(
            kind="bar"
        )

        plt.title(
            f"Fraud Rate by {self.column}"
        )

        plt.xlabel(self.column)
        plt.ylabel("Fraud Rate")

        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.show()

        return fraud_rate


# =========================================================
# TRANSACTION TIME VS FRAUD
# =========================================================

class TemporalVsFraudStrategy(
    BivariateAnalysisStrategy
):
    """
    Analyze fraud rate across ordered transaction-time bins.
    """

    def __init__(self, bins: int = 20):
        if bins <= 0:
            raise ValueError(
                "bins must be greater than zero."
            )

        self.bins = bins

    def analyze(self, df: pd.DataFrame):

        required_columns = {
            "TransactionDT",
            "isFraud"
        }

        missing_columns = (
            required_columns - set(df.columns)
        )

        if missing_columns:
            raise ValueError(
                f"Missing required columns: "
                f"{missing_columns}"
            )

        working_df = df[
            ["TransactionDT", "isFraud"]
        ].dropna()

        working_df = working_df.copy()

        working_df["time_bin"] = pd.cut(
            working_df["TransactionDT"],
            bins=self.bins,
            include_lowest=True
        )

        fraud_rate = (
            working_df
            .groupby(
                "time_bin",
                observed=True
            )["isFraud"]
            .mean()
        )

        print(
            "\nFraud Rate Across Transaction Time:"
        )

        print(fraud_rate)

        plt.figure(figsize=(10, 5))

        fraud_rate.plot()

        plt.title(
            "Fraud Rate Across Transaction Time"
        )

        plt.xlabel("Transaction Time Bin")
        plt.ylabel("Fraud Rate")

        plt.tight_layout()
        plt.show()

        return fraud_rate


# =========================================================
# CONTEXT CLASS
# =========================================================

class BivariateAnalyzer:
    """
    Context class for executing a selected
    bivariate analysis strategy.
    """

    def __init__(
        self,
        strategy: BivariateAnalysisStrategy
    ):

        if not isinstance(
            strategy,
            BivariateAnalysisStrategy
        ):
            raise TypeError(
                "strategy must inherit from "
                "BivariateAnalysisStrategy."
            )

        self._strategy = strategy

    def set_strategy(
        self,
        strategy: BivariateAnalysisStrategy
    ):

        if not isinstance(
            strategy,
            BivariateAnalysisStrategy
        ):
            raise TypeError(
                "strategy must inherit from "
                "BivariateAnalysisStrategy."
            )

        self._strategy = strategy

    def execute_analysis(
        self,
        df: pd.DataFrame
    ):

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

    print("=" * 60)
    print("TRACE BIVARIATE ANALYSIS")
    print("=" * 60)

    print("\nAvailable strategies:")
    print("1. NumericalVsFraudStrategy")
    print("2. CategoricalVsFraudStrategy")
    print("3. TemporalVsFraudStrategy")


if __name__ == "__main__":
    main()  
from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import pandas as pd


# =========================================================
# ABSTRACT BASE CLASS
# =========================================================

class UnivariateAnalysisStrategy(ABC):
    """
    Abstract base class for univariate analysis strategies.
    """

    @abstractmethod
    def analyze(self, df: pd.DataFrame):
        """
        Perform a specific univariate analysis.
        """
        pass


# =========================================================
# FRAUD DISTRIBUTION
# =========================================================

class FraudDistributionStrategy(
    UnivariateAnalysisStrategy
):
    """
    Analyze the distribution of the fraud target.
    """

    def analyze(self, df: pd.DataFrame):

        if "isFraud" not in df.columns:
            raise ValueError(
                "Column 'isFraud' was not found."
            )

        fraud_counts = (
            df["isFraud"]
            .value_counts()
            .sort_index()
        )

        print("\nFraud Distribution:")
        print(fraud_counts)

        print("\nFraud Distribution (%):")
        print(
            df["isFraud"]
            .value_counts(normalize=True)
            .sort_index()
            .mul(100)
        )

        ax = fraud_counts.plot(
            kind="bar",
            figsize=(7, 5),
            title="Fraud Distribution"
        )

        ax.set_xlabel("isFraud")
        ax.set_ylabel("Transaction Count")

        plt.tight_layout()
        plt.show()

        return fraud_counts


# =========================================================
# NUMERICAL DISTRIBUTION
# =========================================================

class NumericalDistributionStrategy(
    UnivariateAnalysisStrategy
):
    """
    Analyze the distribution of a numerical column.
    """

    def __init__(self, column: str):
        self.column = column

    def analyze(self, df: pd.DataFrame):

        if self.column not in df.columns:
            raise ValueError(
                f"Column '{self.column}' was not found."
            )

        if not pd.api.types.is_numeric_dtype(
            df[self.column]
        ):
            raise TypeError(
                f"Column '{self.column}' is not numerical."
            )

        series = df[self.column].dropna()

        print(
            f"\nSummary for {self.column}:"
        )

        print(series.describe())

        plt.figure(figsize=(8, 5))

        plt.hist(
            series,
            bins=50
        )

        plt.title(
            f"Distribution of {self.column}"
        )

        plt.xlabel(self.column)
        plt.ylabel("Frequency")

        plt.tight_layout()
        plt.show()

        return series.describe()


# =========================================================
# CATEGORICAL DISTRIBUTION
# =========================================================

class CategoricalDistributionStrategy(
    UnivariateAnalysisStrategy
):
    """
    Analyze the distribution of a categorical column.
    """

    def __init__(
        self,
        column: str,
        top_n: int = 10
    ):
        self.column = column
        self.top_n = top_n

    def analyze(self, df: pd.DataFrame):

        if self.column not in df.columns:
            raise ValueError(
                f"Column '{self.column}' was not found."
            )

        value_counts = (
            df[self.column]
            .value_counts(dropna=False)
            .head(self.top_n)
        )

        print(
            f"\nTop values for {self.column}:"
        )

        print(value_counts)

        plt.figure(figsize=(9, 5))

        value_counts.plot(
            kind="bar"
        )

        plt.title(
            f"Top {self.top_n} Values - {self.column}"
        )

        plt.xlabel(self.column)
        plt.ylabel("Frequency")

        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.show()

        return value_counts


# =========================================================
# ANALYZER CONTEXT
# =========================================================

class UnivariateAnalyzer:
    """
    Context class that executes a selected
    univariate analysis strategy.
    """

    def __init__(
        self,
        strategy: UnivariateAnalysisStrategy
    ):

        if not isinstance(
            strategy,
            UnivariateAnalysisStrategy
        ):
            raise TypeError(
                "strategy must inherit from "
                "UnivariateAnalysisStrategy."
            )

        self._strategy = strategy

    def set_strategy(
        self,
        strategy: UnivariateAnalysisStrategy
    ):

        if not isinstance(
            strategy,
            UnivariateAnalysisStrategy
        ):
            raise TypeError(
                "strategy must inherit from "
                "UnivariateAnalysisStrategy."
            )

        self._strategy = strategy

    def execute_analysis(
        self,
        df: pd.DataFrame
    ):

        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                "df must be a pandas DataFrame."
            )

        return self._strategy.analyze(df)


# =========================================================
# MAIN
# =========================================================

def main():

    print("=" * 60)
    print("TRACE UNIVARIATE ANALYSIS")
    print("=" * 60)

    print(
        "Available strategies:"
    )

    print(
        "1. FraudDistributionStrategy"
    )

    print(
        "2. NumericalDistributionStrategy"
    )

    print(
        "3. CategoricalDistributionStrategy"
    )


if __name__ == "__main__":
    main()
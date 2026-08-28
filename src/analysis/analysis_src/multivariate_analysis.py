from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import pandas as pd


class MultivariateAnalysisStrategy(ABC):

    @abstractmethod
    def analyze(self, df: pd.DataFrame):
        """Perform a multivariate analysis."""
        pass


class CorrelationAnalysisStrategy(MultivariateAnalysisStrategy):

    def __init__(self, columns: list[str]):
        if not columns:
            raise ValueError("columns cannot be empty.")
        self.columns = columns

    def analyze(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame.")

        missing_columns = [col for col in self.columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}")

        numeric_df = df[self.columns].select_dtypes(include="number")

        if numeric_df.empty:
            raise ValueError("No numerical columns available.")

        correlation = numeric_df.corr()

        plt.figure(figsize=(10, 7))
        plt.imshow(correlation, aspect="auto")
        plt.colorbar()
        plt.xticks(range(len(correlation.columns)), correlation.columns, rotation=90)
        plt.yticks(range(len(correlation.columns)), correlation.columns)
        plt.title("Multivariate Feature Correlation")
        plt.tight_layout()
        plt.show()

        return correlation


class TargetGroupComparisonStrategy(MultivariateAnalysisStrategy):

    def __init__(self, columns: list[str]):
        if not columns:
            raise ValueError("columns cannot be empty.")
        self.columns = columns

    def analyze(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame.")
        if "isFraud" not in df.columns:
            raise ValueError("Column 'isFraud' is required.")

        missing_columns = [col for col in self.columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}")

        numeric_columns = (
            df[self.columns]
            .select_dtypes(include="number")
            .columns
        )

        if len(numeric_columns) == 0:
            raise ValueError("No numerical columns available.")

        result = (
            df.groupby("isFraud")[numeric_columns]
            .mean()
            .transpose()
            .rename(columns={0: "legitimate_mean", 1: "fraud_mean"})
        )

        return result


class MultivariateAnalyzer:

    def __init__(self, strategy: MultivariateAnalysisStrategy):
        if not isinstance(strategy, MultivariateAnalysisStrategy):
            raise TypeError(
                "strategy must inherit from MultivariateAnalysisStrategy."
            )
        self._strategy = strategy

    def set_strategy(self, strategy: MultivariateAnalysisStrategy):
        if not isinstance(strategy, MultivariateAnalysisStrategy):
            raise TypeError(
                "strategy must inherit from MultivariateAnalysisStrategy."
            )
        self._strategy = strategy

    def execute_analysis(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame.")
        return self._strategy.analyze(df)


def main():
    print("=" * 60)
    print("TRACE MULTIVARIATE ANALYSIS")
    print("=" * 60)
    print("\nAvailable strategies:")
    print("1. CorrelationAnalysisStrategy")
    print("2. TargetGroupComparisonStrategy")


if __name__ == "__main__":
    main()
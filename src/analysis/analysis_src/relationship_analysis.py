from abc import ABC, abstractmethod

import pandas as pd


class RelationshipAnalysisStrategy(ABC):

    @abstractmethod
    def analyze(self, df: pd.DataFrame):
        """Perform a specific relationship analysis."""
        pass


class EntityPairFrequencyStrategy(RelationshipAnalysisStrategy):

    def __init__(self, first_entity: str, second_entity: str, top_n: int = 20):
        if not first_entity or not second_entity:
            raise ValueError("Entity names cannot be empty.")
        if first_entity == second_entity:
            raise ValueError("Entities must be different.")
        if top_n <= 0:
            raise ValueError("top_n must be greater than zero.")

        self.first_entity = first_entity
        self.second_entity = second_entity
        self.top_n = top_n

    def analyze(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame.")

        required_columns = {self.first_entity, self.second_entity}
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        relationship = (
            df[[self.first_entity, self.second_entity]]
            .dropna()
            .groupby([self.first_entity, self.second_entity])
            .size()
            .reset_index(name="transaction_count")
            .sort_values("transaction_count", ascending=False)
            .head(self.top_n)
            .reset_index(drop=True)
        )

        return relationship


class EntityPairFraudRateStrategy(RelationshipAnalysisStrategy):

    def __init__(self, first_entity: str, second_entity: str, min_transactions: int = 20, top_n: int = 20):
        if not first_entity or not second_entity:
            raise ValueError("Entity names cannot be empty.")
        if first_entity == second_entity:
            raise ValueError("Entities must be different.")
        if min_transactions <= 0:
            raise ValueError("min_transactions must be greater than zero.")
        if top_n <= 0:
            raise ValueError("top_n must be greater than zero.")

        self.first_entity = first_entity
        self.second_entity = second_entity
        self.min_transactions = min_transactions
        self.top_n = top_n

    def analyze(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame.")

        required_columns = {self.first_entity, self.second_entity, "isFraud"}
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        grouped = (
            df[[self.first_entity, self.second_entity, "isFraud"]]
            .dropna()
            .groupby([self.first_entity, self.second_entity])["isFraud"]
            .agg(transaction_count="count", fraud_count="sum", fraud_rate="mean")
            .reset_index()
        )

        grouped = grouped[grouped["transaction_count"] >= self.min_transactions]

        if grouped.empty:
            return grouped

        return (
            grouped.sort_values("fraud_rate", ascending=False)
            .head(self.top_n)
            .reset_index(drop=True)
        )


class RelationshipAnalyzer:

    def __init__(self, strategy: RelationshipAnalysisStrategy):
        if not isinstance(strategy, RelationshipAnalysisStrategy):
            raise TypeError("strategy must inherit from RelationshipAnalysisStrategy.")
        self._strategy = strategy

    def set_strategy(self, strategy: RelationshipAnalysisStrategy):
        if not isinstance(strategy, RelationshipAnalysisStrategy):
            raise TypeError("strategy must inherit from RelationshipAnalysisStrategy.")
        self._strategy = strategy

    def execute_analysis(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame.")
        return self._strategy.analyze(df)


def main():
    print("=" * 60)
    print("TRACE RELATIONSHIP ANALYSIS")
    print("=" * 60)
    print("\nAvailable strategies:")
    print("1. EntityPairFrequencyStrategy")
    print("2. EntityPairFraudRateStrategy")


if __name__ == "__main__":
    main()
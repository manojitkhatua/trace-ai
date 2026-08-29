from abc import ABC, abstractmethod

import pandas as pd


# Abstract Base Class for Entity Analysis Strategies
class EntityAnalysisStrategy(ABC):

    @abstractmethod
    def analyze(self, df: pd.DataFrame):
        """Perform a specific entity analysis."""
        pass


# Concrete Strategy for Entity Cardinality Analysis
class EntityCardinalityStrategy(EntityAnalysisStrategy):

    def __init__(self, entity_columns: list[str]):
        if not entity_columns:
            raise ValueError("entity_columns cannot be empty.")
        self.entity_columns = entity_columns

    def analyze(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame.")

        missing_columns = [
            col for col in self.entity_columns
            if col not in df.columns
        ]

        if missing_columns:
            raise ValueError(f"Missing entity columns: {missing_columns}")

        results = []

        for column in self.entity_columns:
            series = df[column].dropna()
            value_counts = series.value_counts()

            results.append({
                "entity": column,
                "unique_entities": series.nunique(),
                "non_missing_transactions": len(series),
                "shared_transaction_count": int(
                    value_counts[value_counts > 1].sum()
                ),
                "max_transactions_per_entity": int(
                    value_counts.max()
                ) if not value_counts.empty else 0
            })

        result = pd.DataFrame(results)

        return result.sort_values(
            "max_transactions_per_entity",
            ascending=False
        ).reset_index(drop=True)


# Concrete Strategy for Shared Entity Analysis
class SharedEntityStrategy(EntityAnalysisStrategy):

    def __init__(
        self,
        entity_columns: list[str],
        min_transactions: int = 2,
        top_n: int = 20
    ):
        if not entity_columns:
            raise ValueError("entity_columns cannot be empty.")
        if min_transactions < 2:
            raise ValueError("min_transactions must be at least 2.")
        if top_n <= 0:
            raise ValueError("top_n must be greater than zero.")

        self.entity_columns = entity_columns
        self.min_transactions = min_transactions
        self.top_n = top_n

    def analyze(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame.")

        missing_columns = [
            col for col in self.entity_columns
            if col not in df.columns
        ]

        if missing_columns:
            raise ValueError(f"Missing entity columns: {missing_columns}")

        results = []

        for column in self.entity_columns:
            counts = df[column].dropna().value_counts()

            shared_entities = counts[
                counts >= self.min_transactions
            ].head(self.top_n)

            for value, count in shared_entities.items():
                results.append({
                    "entity": column,
                    "entity_value": value,
                    "transaction_count": int(count)
                })

        result = pd.DataFrame(results)

        if result.empty:
            return result

        return result.sort_values(
            "transaction_count",
            ascending=False
        ).reset_index(drop=True)


# Concrete Strategy for Entity Fraud Rate Analysis
class EntityFraudRateStrategy(EntityAnalysisStrategy):

    def __init__(
        self,
        entity_columns: list[str],
        min_transactions: int = 20,
        top_n: int = 20
    ):
        if not entity_columns:
            raise ValueError("entity_columns cannot be empty.")
        if min_transactions <= 0:
            raise ValueError(
                "min_transactions must be greater than zero."
            )
        if top_n <= 0:
            raise ValueError("top_n must be greater than zero.")

        self.entity_columns = entity_columns
        self.min_transactions = min_transactions
        self.top_n = top_n

    def analyze(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame.")

        required_columns = set(self.entity_columns) | {"isFraud"}
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}"
            )

        results = []

        for column in self.entity_columns:
            grouped = (
                df[[column, "isFraud"]]
                .dropna(subset=[column])
                .groupby(column)["isFraud"]
                .agg(
                    transaction_count="count",
                    fraud_count="sum",
                    fraud_rate="mean"
                )
            )

            grouped = grouped[
                grouped["transaction_count"] >= self.min_transactions
            ]

            if grouped.empty:
                continue

            grouped = (
                    grouped.sort_values("fraud_rate", ascending=False)
                        .head(self.top_n)
                        .reset_index()
                        .rename(columns={column: "entity_value"})
                )

            grouped.insert(0, "entity", column)
            results.append(grouped)
        if not results:
            return pd.DataFrame()

        return pd.concat(results, ignore_index=True)


class DeviceCardConnectivityStrategy(EntityAnalysisStrategy):

    def __init__(self, min_cards: int = 2, top_n: int = 20):
        if min_cards <= 0:
            raise ValueError("min_cards must be greater than zero.")
        if top_n <= 0:
            raise ValueError("top_n must be greater than zero.")

        self.min_cards = min_cards
        self.top_n = top_n

    def analyze(self, df: pd.DataFrame):
        required_columns = {"DeviceInfo", "card1"}

        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}")

        working_df = df[["DeviceInfo", "card1"]].dropna().copy()

        result = (
            working_df.groupby("DeviceInfo")
            .agg(
                unique_card1_count=("card1", "nunique"),
                transaction_count=("card1", "count")
            )
            .query("unique_card1_count >= @self.min_cards")
            .sort_values(
                ["unique_card1_count", "transaction_count"],
                ascending=False
            )
            .head(self.top_n)
            .reset_index()
        )

        return result

# Context Class for Entity Analysis
class EntityAnalyzer:

    def __init__(self, strategy: EntityAnalysisStrategy):
        if not isinstance(strategy, EntityAnalysisStrategy):
            raise TypeError(
                "strategy must inherit from EntityAnalysisStrategy."
            )
        self._strategy = strategy

    def set_strategy(self, strategy: EntityAnalysisStrategy):
        if not isinstance(strategy, EntityAnalysisStrategy):
            raise TypeError(
                "strategy must inherit from EntityAnalysisStrategy."
            )
        self._strategy = strategy

    def execute_analysis(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame.")
        return self._strategy.analyze(df)


# Main Method
def main():
    print("=" * 60)
    print("TRACE ENTITY / RELATIONSHIP ANALYSIS")
    print("=" * 60)
    print("\nAvailable strategies:")
    print("1. EntityCardinalityStrategy")
    print("2. SharedEntityStrategy")
    print("3. EntityFraudRateStrategy")
    print("4. DeviceCardConnectivityStrategy")


if __name__ == "__main__":
    main()
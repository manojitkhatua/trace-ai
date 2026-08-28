from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import pandas as pd


# =========================================================
# ABSTRACT BASE CLASS
# =========================================================

class TemporalAnalysisStrategy(ABC):
    """
    Abstract base class for temporal analysis strategies.
    """

    @abstractmethod
    def analyze(self, df: pd.DataFrame):
        """
        Perform a temporal analysis.
        """
        pass


# =========================================================
# FRAUD RATE BY TIME BIN
# =========================================================

class FraudRateByTimeBinStrategy(
    TemporalAnalysisStrategy
):
    """
    Calculates fraud rate across ordered TransactionDT bins.
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
            "isFraud",
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
        ].dropna().copy()

        working_df["time_bin"] = pd.cut(
            working_df["TransactionDT"],
            bins=self.bins,
            include_lowest=True,
        )

        result = (
            working_df
            .groupby(
                "time_bin",
                observed=True,
            )["isFraud"]
            .agg(
                transaction_count="count",
                fraud_count="sum",
                fraud_rate="mean",
            )
        )

        print("\nFraud Rate by Time Bin:")
        print(result)

        plt.figure(figsize=(10, 5))

        result["fraud_rate"].plot(
            marker="o"
        )

        plt.title(
            "Fraud Rate Across Transaction Time"
        )

        plt.xlabel("Transaction Time Bin")
        plt.ylabel("Fraud Rate")

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        return result


# =========================================================
# TRANSACTION VOLUME BY TIME BIN
# =========================================================

class TransactionVolumeByTimeBinStrategy(
    TemporalAnalysisStrategy
):
    """
    Measures transaction volume across time bins.
    """

    def __init__(self, bins: int = 20):
        if bins <= 0:
            raise ValueError(
                "bins must be greater than zero."
            )

        self.bins = bins

    def analyze(self, df: pd.DataFrame):

        if "TransactionDT" not in df.columns:
            raise ValueError(
                "Column 'TransactionDT' is required."
            )

        working_df = df[
            ["TransactionDT"]
        ].dropna().copy()

        working_df["time_bin"] = pd.cut(
            working_df["TransactionDT"],
            bins=self.bins,
            include_lowest=True,
        )

        result = (
            working_df["time_bin"]
            .value_counts()
            .sort_index()
            .rename("transaction_count")
            .to_frame()
        )

        print("\nTransaction Volume by Time Bin:")
        print(result)

        plt.figure(figsize=(10, 5))

        result["transaction_count"].plot(
            marker="o"
        )

        plt.title(
            "Transaction Volume Across Time"
        )

        plt.xlabel("Transaction Time Bin")
        plt.ylabel("Transaction Count")

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        return result


# =========================================================
# FRAUD COUNT BY TIME BIN
# =========================================================

class FraudCountByTimeBinStrategy(
    TemporalAnalysisStrategy
):
    """
    Measures the number of fraudulent transactions
    across time bins.
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
            "isFraud",
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
        ].dropna().copy()

        working_df["time_bin"] = pd.cut(
            working_df["TransactionDT"],
            bins=self.bins,
            include_lowest=True,
        )

        result = (
            working_df
            .groupby(
                "time_bin",
                observed=True,
            )["isFraud"]
            .sum()
            .rename("fraud_count")
            .to_frame()
        )

        print("\nFraud Count by Time Bin:")
        print(result)

        plt.figure(figsize=(10, 5))

        result["fraud_count"].plot(
            kind="bar"
        )

        plt.title(
            "Fraud Count Across Transaction Time"
        )

        plt.xlabel("Transaction Time Bin")
        plt.ylabel("Fraud Count")

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        return result


# =========================================================
# TRANSACTION VELOCITY STRATEGY
# =========================================================

class TransactionVelocityStrategy(
    TemporalAnalysisStrategy
):
    """
    Analyze short-term transaction activity using
    a past-looking time window.

    For each transaction, the strategy calculates
    how many previous transactions occurred within
    the specified time window.

    Important:
    Future transactions are never included.
    """

    def __init__(
        self,
        window_seconds: int = 300
    ):
        """
        Parameters
        ----------
        window_seconds : int, default=300
            Size of the look-back window in seconds.

            300 seconds = 5 minutes.
        """

        if window_seconds <= 0:
            raise ValueError(
                "window_seconds must be greater than zero."
            )

        self.window_seconds = window_seconds

    def analyze(self, df: pd.DataFrame):

        required_columns = {
            "TransactionDT",
            "isFraud",
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
            [
                "TransactionDT",
                "isFraud",
            ]
        ].copy()

        working_df = working_df.dropna(
            subset=["TransactionDT"]
        )

        # Preserve original row identity.
        working_df["_original_index"] = (
            working_df.index
        )

        # Sort chronologically.
        working_df = working_df.sort_values(
            "TransactionDT"
        )

        transaction_times = (
            working_df["TransactionDT"]
            .to_numpy()
        )

        velocity = []

        left_pointer = 0

        for right_pointer in range(
            len(transaction_times)
        ):

            current_time = (
                transaction_times[right_pointer]
            )

            window_start = (
                current_time
                - self.window_seconds
            )

            while (
                left_pointer < right_pointer
                and transaction_times[left_pointer]
                <= window_start
            ):
                left_pointer += 1

            previous_transaction_count = (
                right_pointer - left_pointer
            )

            velocity.append(
                previous_transaction_count
            )

        working_df["transaction_velocity"] = (
            velocity
        )

        result = (
            working_df[
                [
                    "_original_index",
                    "transaction_velocity",
                    "isFraud",
                ]
            ]
        )

        # Compare velocity between legitimate
        # and fraudulent transactions.
        velocity_summary = (
            result.groupby("isFraud")
            ["transaction_velocity"]
            .describe()
        )

        print(
            "\nTransaction Velocity Summary:"
        )

        print(velocity_summary)

        plt.figure(figsize=(8, 5))

        result.boxplot(
            column="transaction_velocity",
            by="isFraud",
        )

        plt.title(
            f"Transaction Velocity "
            f"({self.window_seconds}-Second Window)"
        )

        plt.suptitle("")

        plt.xlabel("Fraud Status")
        plt.ylabel("Previous Transactions in Window")

        plt.tight_layout()
        plt.show()

        return result
    
# =========================================================
# INTER-TRANSACTION TIME STRATEGY
# =========================================================

class InterTransactionTimeStrategy(
    TemporalAnalysisStrategy
):
    """
    Analyze the time difference between consecutive
    transactions in chronological order.

    The analysis is performed globally across the
    transaction stream.

    For transaction i:

        delta_t = TransactionDT[i] - TransactionDT[i-1]

    The first transaction has no previous transaction
    and is therefore excluded from the result.
    """

    def analyze(self, df: pd.DataFrame):

        required_columns = {
            "TransactionDT",
            "isFraud",
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
            [
                "TransactionDT",
                "isFraud",
            ]
        ].dropna(
            subset=["TransactionDT"]
        ).copy()

        if working_df.empty:
            raise ValueError(
                "No valid TransactionDT values "
                "were found."
            )

        # Preserve the original row index.
        working_df["_original_index"] = (
            working_df.index
        )

        # Sort chronologically.
        working_df = working_df.sort_values(
            "TransactionDT"
        ).reset_index(drop=True)

        # Calculate the time difference between
        # consecutive transactions.
        working_df["inter_transaction_time"] = (
            working_df["TransactionDT"].diff()
        )

        # The first transaction has no previous
        # transaction and therefore no valid delta.
        working_df = working_df.dropna(
            subset=["inter_transaction_time"]
        )

        # Basic safety check.
        if (
            working_df["inter_transaction_time"] < 0
        ).any():
            raise ValueError(
                "Negative inter-transaction time "
                "detected after chronological sorting."
            )

        result = working_df[
            [
                "_original_index",
                "inter_transaction_time",
                "isFraud",
            ]
        ].copy()

        # -------------------------------------------------
        # Summary by fraud status
        # -------------------------------------------------

        summary = (
            result
            .groupby("isFraud")
            ["inter_transaction_time"]
            .describe()
        )

        print(
            "\nInter-Transaction Time Summary:"
        )

        print(summary)

        # -------------------------------------------------
        # Distribution plot
        # -------------------------------------------------

        plt.figure(figsize=(8, 5))

        result.boxplot(
            column="inter_transaction_time",
            by="isFraud",
        )

        plt.title(
            "Inter-Transaction Time by Fraud Status"
        )

        plt.suptitle("")

        plt.xlabel("Fraud Status")
        plt.ylabel(
            "Time Since Previous Transaction"
        )

        plt.tight_layout()
        plt.show()

        return result


# =========================================================
# CONTEXT CLASS
# =========================================================

class TemporalAnalyzer:
    """
    Context class for executing a selected temporal
    analysis strategy.
    """

    def __init__(
        self,
        strategy: TemporalAnalysisStrategy,
    ):

        if not isinstance(
            strategy,
            TemporalAnalysisStrategy,
        ):
            raise TypeError(
                "strategy must inherit from "
                "TemporalAnalysisStrategy."
            )

        self._strategy = strategy

    def set_strategy(
        self,
        strategy: TemporalAnalysisStrategy,
    ):

        if not isinstance(
            strategy,
            TemporalAnalysisStrategy,
        ):
            raise TypeError(
                "strategy must inherit from "
                "TemporalAnalysisStrategy."
            )

        self._strategy = strategy

    def execute_analysis(
        self,
        df: pd.DataFrame,
    ):

        if not isinstance(
            df,
            pd.DataFrame,
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
    print("TRACE TEMPORAL ANALYSIS")
    print("=" * 60)

    print("1. FraudRateByTimeBinStrategy")
    print("2. TransactionVolumeByTimeBinStrategy")
    print("3. FraudCountByTimeBinStrategy")
    print("4. TransactionVelocityStrategy")
    print("5. InterTransactionTimeStrategy")


if __name__ == "__main__":
    main()
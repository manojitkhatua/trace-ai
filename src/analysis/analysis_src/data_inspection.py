from abc import ABC, abstractmethod

import pandas as pd


# =========================================================
# DATA INSPECTION STRATEGY
# =========================================================

class DataInspectionStrategy(ABC):
    """
    Abstract base class for data inspection strategies.

    Each concrete strategy must implement the inspect()
    method and perform one specific type of inspection.
    """

    @abstractmethod
    def inspect(self, df: pd.DataFrame) -> None:
        """
        Perform a specific inspection on the DataFrame.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to inspect.

        Raises
        ------
        TypeError
            If the supplied object is not a DataFrame.
        """
        pass


# =========================================================
# VIEW OF DATA STRATEGY
# =========================================================

class ViewOfDataStrategy(DataInspectionStrategy):
    """
    Strategy for displaying the basic structure of a dataset.
    """

    def inspect(self, df: pd.DataFrame) -> None:

        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                "Expected df to be a pandas DataFrame."
            )

        print("\nFirst five rows of data:")
        print(df.head())

        print("\nShape of the data:")
        print(df.shape)

        print("\nColumn names:")
        print(df.columns.tolist())


# =========================================================
# DATA TYPES INSPECTION STRATEGY
# =========================================================

class DataTypesInspectionStrategy(DataInspectionStrategy):
    """
    Strategy for inspecting data types and non-null values.
    """

    def inspect(self, df: pd.DataFrame) -> None:

        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                "Expected df to be a pandas DataFrame."
            )

        print("\nData types and non-null information:")
        df.info()


# =========================================================
# SUMMARY STATISTICS STRATEGY
# =========================================================

class SummaryStatisticalInspectionStrategy(
    DataInspectionStrategy
):
    """
    Strategy for inspecting numerical and categorical
    summary statistics.
    """

    def inspect(self, df: pd.DataFrame) -> None:

        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                "Expected df to be a pandas DataFrame."
            )

        print("\nNumerical summary statistics:")

        numerical_columns = df.select_dtypes(
            include="number"
        )

        if numerical_columns.empty:

            print(
                "No numerical columns available."
            )

        else:

            print(
                numerical_columns.describe()
            )

        print("\nCategorical summary statistics:")

        categorical_columns = df.select_dtypes(
            include=["object", "category"]
        )

        if categorical_columns.empty:

            print(
                "No categorical columns available."
            )

        else:

            print(
                categorical_columns.describe()
            )


# =========================================================
# DATA INSPECTOR
# =========================================================

class DataInspector:
    """
    Context class responsible for executing a selected
    data inspection strategy.
    """

    def __init__(
        self,
        strategy: DataInspectionStrategy
    ) -> None:

        if not isinstance(
            strategy,
            DataInspectionStrategy
        ):
            raise TypeError(
                "strategy must inherit from "
                "DataInspectionStrategy."
            )

        self._strategy = strategy

    def set_strategy(
        self,
        strategy: DataInspectionStrategy
    ) -> None:
        """
        Change the currently selected inspection strategy.
        """

        if not isinstance(
            strategy,
            DataInspectionStrategy
        ):
            raise TypeError(
                "strategy must inherit from "
                "DataInspectionStrategy."
            )

        self._strategy = strategy

    def execute_inspection(
        self,
        df: pd.DataFrame
    ) -> None:
        """
        Execute the currently selected strategy.
        """

        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                "Expected df to be a pandas DataFrame."
            )

        self._strategy.inspect(df)


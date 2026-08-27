from pathlib import Path

import pandas as pd


class DataValidation:
    """
    Validates the structure and basic integrity
    of the TRACE datasets.

    This class does not clean or transform data.
    """

    REQUIRED_FILES = {
        "train_transaction": "train_transaction.csv",
        "train_identity": "train_identity.csv",
        "test_transaction": "test_transaction.csv",
        "test_identity": "test_identity.csv",
    }

    REQUIRED_COLUMNS = {
        "train_transaction": [
            "TransactionID",
            "isFraud",
            "TransactionDT",
            "TransactionAmt",
        ],
        "train_identity": [
            "TransactionID",
        ],
        "test_transaction": [
            "TransactionID",
            "TransactionDT",
            "TransactionAmt",
        ],
        "test_identity": [
            "TransactionID",
        ],
    }

    def __init__(self):
        # trace-ai/src/data_validation.py
        # parent.parent -> trace-ai

        self.project_root = (
            Path(__file__).resolve().parents[2]
        )
        self.data_directory = (
            self.project_root
            / "data"
            / "processed"
            / "extracted_data"
        )

    # -----------------------------------------------------
    # Load extracted datasets
    # -----------------------------------------------------

    def load_datasets(self):
        """
        Load the already extracted CSV files.
        """

        if not self.data_directory.exists():
            raise FileNotFoundError(
                "Extracted dataset directory does not exist: "
                f"{self.data_directory}"
            )

        datasets = {}

        for dataset_name, file_name in (
            self.REQUIRED_FILES.items()
        ):

            file_path = (
                self.data_directory
                / file_name
            )

            if not file_path.exists():
                raise FileNotFoundError(
                    f"Required file not found: {file_path}"
                )

            print(f"Reading: {file_name}")

            datasets[dataset_name] = pd.read_csv(
                file_path
            )

        return datasets

    # -----------------------------------------------------
    # Validate required files/datasets
    # -----------------------------------------------------

    def validate_datasets(self, datasets):

        for dataset_name in self.REQUIRED_FILES:

            if dataset_name not in datasets:
                raise ValueError(
                    f"Missing dataset: {dataset_name}"
                )

        print("✓ Required datasets found")

    # -----------------------------------------------------
    # Validate required columns
    # -----------------------------------------------------

    def validate_columns(self, datasets):

        for dataset_name, required_columns in (
            self.REQUIRED_COLUMNS.items()
        ):

            dataframe = datasets[dataset_name]

            missing_columns = [
                column
                for column in required_columns
                if column not in dataframe.columns
            ]

            if missing_columns:
                raise ValueError(
                    f"{dataset_name} is missing columns: "
                    f"{missing_columns}"
                )

        print("✓ Required columns found")

    # -----------------------------------------------------
    # Validate TransactionID
    # -----------------------------------------------------

    def validate_transaction_id(self, datasets):

        for dataset_name, dataframe in (
            datasets.items()
        ):

            if dataframe["TransactionID"].isna().any():

                raise ValueError(
                    f"{dataset_name} contains "
                    "missing TransactionID values"
                )

            if dataframe["TransactionID"].duplicated().any():

                raise ValueError(
                    f"{dataset_name} contains "
                    "duplicate TransactionID values"
                )

        print("✓ TransactionID validation passed")

    # -----------------------------------------------------
    # Validate fraud target
    # -----------------------------------------------------

    def validate_target(self, datasets):

        train_transaction = datasets[
            "train_transaction"
        ]

        target = train_transaction["isFraud"]

        if target.isna().any():
            raise ValueError(
                "isFraud contains missing values"
            )

        unique_values = set(target.unique())

        if not unique_values.issubset({0, 1}):

            raise ValueError(
                "isFraud must contain only 0 and 1"
            )

        print("✓ isFraud validation passed")

    # -----------------------------------------------------
    # Run all validations
    # -----------------------------------------------------

    def validate(self, datasets):

        print("\n")
        print("=" * 60)
        print("TRACE DATA VALIDATION")
        print("=" * 60)

        self.validate_datasets(datasets)
        self.validate_columns(datasets)
        self.validate_transaction_id(datasets)
        self.validate_target(datasets)

        print("=" * 60)
        print("TRACE DATA VALIDATION PASSED")
        print("=" * 60)


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    validator = DataValidation()

    datasets = validator.load_datasets()

    validator.validate(datasets)
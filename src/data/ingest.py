import os
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd


# =========================================================
# ABSTRACT DATA INGESTOR
# =========================================================

class DataIngestor(ABC):

    @abstractmethod
    def ingest(self, file_path: str):
        """
        Ingest data from the given file.
        """
        pass


# =========================================================
# ZIP DATA INGESTOR
# =========================================================

class ZipDataIngestor(DataIngestor):

    # Files that TRACE needs from the IEEE-CIS dataset
    REQUIRED_FILES = [
        "train_transaction.csv",
        "train_identity.csv",
        "test_transaction.csv",
        "test_identity.csv",
    ]

    def ingest(self, file_path: str):
        """
        Extract the ZIP only when necessary and load
        the already-extracted CSV files.
        """

        zip_path = Path(file_path)

        # -------------------------------------------------
        # 1. Validate ZIP file
        # -------------------------------------------------

        if zip_path.suffix.lower() != ".zip":
            raise ValueError(
                "The provided file is not a ZIP file."
            )

        if not zip_path.exists():
            raise FileNotFoundError(
                f"ZIP file not found: {zip_path}"
            )

        # -------------------------------------------------
        # 2. Find project root
        #
        # Current file:
        # trace-ai/src/ingest.py
        #
        # parent       -> src
        # parent.parent -> trace-ai
        # -------------------------------------------------

        project_root = (
            Path(__file__).resolve().parent.parent
        )

        # -------------------------------------------------
        # 3. Define extracted-data directory
        # -------------------------------------------------

        extracted_data_dir = (
            project_root
            / "data"
            / "processed"
            / "extracted_data"
        )

        extracted_data_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # -------------------------------------------------
        # 4. Check whether data is already extracted
        # -------------------------------------------------

        dataset_already_extracted = all(
            (
                extracted_data_dir / file_name
            ).exists()
            for file_name in self.REQUIRED_FILES
        )

        # -------------------------------------------------
        # 5. Extract only when required
        # -------------------------------------------------

        if not dataset_already_extracted:

            print("\nTRACE DATA INGESTION")
            print("=" * 60)

            print(
                "Extracted dataset not found."
            )

            print(
                f"Extracting ZIP:\n{zip_path}"
            )

            with zipfile.ZipFile(
                zip_path,
                "r"
            ) as zip_ref:

                zip_ref.extractall(
                    extracted_data_dir
                )

            print(
                "ZIP extraction completed."
            )

        else:

            print("\nTRACE DATA INGESTION")
            print("=" * 60)

            print(
                "Extracted dataset already exists."
            )

            print(
                "Skipping ZIP extraction."
            )

        # -------------------------------------------------
        # 6. Load extracted CSV files
        # -------------------------------------------------

        datasets = {}

        for file_name in self.REQUIRED_FILES:

            csv_path = (
                extracted_data_dir
                / file_name
            )

            # Safety check
            if not csv_path.exists():
                raise FileNotFoundError(
                    f"Required dataset file not found: "
                    f"{csv_path}"
                )

            print(
                f"Loading: {file_name}"
            )

            dataset_name = file_name.replace(
                ".csv",
                ""
            )

            datasets[dataset_name] = pd.read_csv(
                csv_path
            )

        # -------------------------------------------------
        # 7. Return datasets
        # -------------------------------------------------

        print("=" * 60)
        print(
            "TRACE DATA INGESTION COMPLETE"
        )
        print("=" * 60)

        return datasets


# =========================================================
# DATA INGESTOR FACTORY
# =========================================================

class DataIngestorFactory:

    @staticmethod
    def get_data_ingestor(
        file_extension: str
    ) -> DataIngestor:
        """
        Return the correct data ingestor based
        on the file extension.
        """

        if file_extension.lower() == ".zip":
            return ZipDataIngestor()

        raise ValueError(
            f"No ingestor available for "
            f"extension: {file_extension}"
        )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    # -----------------------------------------------------
    # 1. Project root
    # -----------------------------------------------------

    project_root = Path(__file__).resolve().parents[2]

    file_path = (
        project_root
        / "data"
        / "raw"
        / "ieee-fraud-detection.zip"
    )

    # -----------------------------------------------------
    # 2. ZIP file location
    # -----------------------------------------------------

    file_path = (
        project_root
        / "data"
        / "raw"
        / "ieee-fraud-detection.zip"
    )

    # -----------------------------------------------------
    # 3. Get file extension
    # -----------------------------------------------------

    file_extension = os.path.splitext(
        file_path
    )[1]

    # -----------------------------------------------------
    # 4. Create appropriate ingestor
    # -----------------------------------------------------

    data_ingestor = (
        DataIngestorFactory.get_data_ingestor(
            file_extension
        )
    )

    # -----------------------------------------------------
    # 5. Ingest data
    # -----------------------------------------------------

    datasets = data_ingestor.ingest(
        str(file_path)
    )

    # -----------------------------------------------------
    # 6. Display loaded datasets
    # -----------------------------------------------------

    print("\nDATASETS AVAILABLE TO TRACE")
    print("=" * 60)

    for name, dataframe in datasets.items():

        print(
            f"{name:<20}"
            f"Rows: {dataframe.shape[0]:<10}"
            f"Columns: {dataframe.shape[1]}"
        )
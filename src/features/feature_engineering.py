import numpy as np
import pandas as pd


class FeatureEngineer:

    def __init__(self):
        self.feature_names = []

    def create_transaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame.")

        required_columns = {"TransactionAmt", "TransactionDT"}
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}")

        result = df.copy()

        result["log_transaction_amount"] = np.log1p(
            result["TransactionAmt"]
        )

        self.feature_names = ["log_transaction_amount"]

        return result

    def create_missingness_features(self, df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame.")
        if not columns:
            raise ValueError("columns cannot be empty.")

        missing_columns = [col for col in columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}")

        result = df.copy()

        for column in columns:
            result[f"{column}_missing"] = result[column].isna().astype("int8")

        self.feature_names.extend(
            f"{column}_missing" for column in columns
        )

        return result  
    
    def create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame.")

        required_columns = {"TransactionDT"}
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}")

        result = df.copy()
        result["_original_index"] = result.index

        result = result.sort_values("TransactionDT").reset_index(drop=True)

        result["time_since_previous_transaction"] = (
            result["TransactionDT"].diff()
        )

        result["time_since_previous_transaction"] = (
            result["time_since_previous_transaction"].fillna(0)
        )

        result["has_previous_transaction"] = (
            result["TransactionDT"].diff().notna().astype("int8")
        )

        self.feature_names.extend([
            "time_since_previous_transaction",
            "has_previous_transaction"
        ])

        result = result.sort_values("_original_index").drop(
            columns="_original_index"
        )

        return result
    
    def create_entity_features(self, df: pd.DataFrame, entity_columns: list[str]) -> pd.DataFrame:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame.")
        if not entity_columns:
            raise ValueError("entity_columns cannot be empty.")

        missing_columns = [col for col in entity_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}")

        result = df.copy()

        for column in entity_columns:
            counts = result[column].value_counts(dropna=False)
            result[f"{column}_transaction_count"] = result[column].map(counts).fillna(0).astype("int32")

        self.feature_names.extend(
            f"{column}_transaction_count" for column in entity_columns
        )

        return result
    
    def create_relationship_features(self,df: pd.DataFrame,first_entity: str,second_entity: str) -> pd.DataFrame:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame.")

        required_columns = {first_entity, second_entity}
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}")

        result = df.copy()

        pair_counts = (
            result.groupby([first_entity, second_entity], dropna=False)
            .size()
        )

        result[f"{first_entity}_{second_entity}_transaction_count"] = (
            result.set_index([first_entity, second_entity]).index.map(pair_counts)
            .astype("int32")
        )

        feature_name = f"{first_entity}_{second_entity}_transaction_count"
        self.feature_names.append(feature_name)

        return result
    
    def create_relationship_features(self,df: pd.DataFrame,first_entity: str,second_entity: str) -> pd.DataFrame:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame.")

        required_columns = {first_entity, second_entity}
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}")

        result = df.copy()

        pair_counts = result.groupby(
            [first_entity, second_entity],
            dropna=False
        ).size()

        pair_index = pd.MultiIndex.from_frame(
            result[[first_entity, second_entity]]
        )

        feature_name = f"{first_entity}_{second_entity}_transaction_count"

        result[feature_name] = pair_index.map(pair_counts).astype("int32")

        self.feature_names.append(feature_name)

        return result
    
    def create_entity_relationship_count(self,df: pd.DataFrame,entity: str,related_entity: str) -> pd.DataFrame:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame.")

        required_columns = {entity, related_entity}
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}")

        result = df.copy()

        relationship_counts = (
            result.groupby(entity)[related_entity]
            .nunique()
        )

        feature_name = f"{entity}_unique_{related_entity}_count"

        result[feature_name] = (
            result[entity]
            .map(relationship_counts)
            .fillna(0)
            .astype("int32")
        )

        self.feature_names.append(feature_name)

        return result

def main():
    print("=" * 60)
    print("TRACE FEATURE ENGINEERING")
    print("=" * 60)


if __name__ == "__main__":
    main()
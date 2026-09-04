from __future__ import annotations

import sys
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

SRC = ROOT / "src"
DATA_DIR = ROOT / "data" / "processed" / "extracted_data"
MODEL_DIR = ROOT / "models"
PREPROCESSING_DIR = MODEL_DIR / "preprocessing"

TRANSACTION_PATH = DATA_DIR / "train_transaction.csv"
IDENTITY_PATH = DATA_DIR / "train_identity.csv"

OUTPUT_PATH = ROOT / "scripts" / "real_trace_cases.csv"


# ============================================================
# IMPORT TRACE COMPONENTS
# ============================================================

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from models.predictor import FraudPredictor
from backend.anomaly_engine import AnomalyEngine
from backend.entity_risk_engine import EntityRiskEngine
from backend.risk_engine import RiskEngine
from backend.decision_engine import DecisionEngine


# ============================================================
# RAW INPUT COLUMNS
# ============================================================

RAW_COLUMNS = [
    "TransactionAmt",
    "TransactionDT",
    "card1",
    "card2",
    "addr1",
    "addr2",
    "D7",
    "D12",
    "D13",
    "D14",
    "DeviceInfo",
    "ProductCD",
    "card4",
    "card6",
    "DeviceType",
]


IDENTITY_COLUMNS = [
    "TransactionID",
    "DeviceInfo",
    "DeviceType",
]


# ============================================================
# LOAD DATA
# ============================================================

def load_validation_data() -> pd.DataFrame:

    print("=" * 80)
    print("LOADING REAL VALIDATION DATA")
    print("=" * 80)

    if not TRANSACTION_PATH.exists():
        raise FileNotFoundError(
            f"Missing:\n{TRANSACTION_PATH}"
        )

    if not IDENTITY_PATH.exists():
        raise FileNotFoundError(
            f"Missing:\n{IDENTITY_PATH}"
        )

    # --------------------------------------------------------
    # Transaction table
    # --------------------------------------------------------

    transaction_columns = [
        c
        for c in RAW_COLUMNS + ["TransactionID", "isFraud"]
        if c not in {"DeviceInfo", "DeviceType"}
    ]

    print("\nLoading train_transaction.csv...")

    transaction_df = pd.read_csv(
        TRANSACTION_PATH,
        usecols=transaction_columns,
    )

    print(
        f"Transaction rows: {len(transaction_df):,}"
    )

    # --------------------------------------------------------
    # Identity table
    # --------------------------------------------------------

    print("\nLoading train_identity.csv...")

    identity_df = pd.read_csv(
        IDENTITY_PATH,
        usecols=IDENTITY_COLUMNS,
    )

    print(
        f"Identity rows: {len(identity_df):,}"
    )

    # --------------------------------------------------------
    # Merge
    # --------------------------------------------------------

    df = transaction_df.merge(
        identity_df,
        on="TransactionID",
        how="left",
    )

    print(
        f"\nMerged dataset: {df.shape}"
    )

    # --------------------------------------------------------
    # Chronological 80/20 split
    # --------------------------------------------------------

    print("\nSorting chronologically...")

    df = (
        df.sort_values("TransactionDT")
        .reset_index(drop=True)
    )

    split_index = int(len(df) * 0.80)

    validation = df.iloc[split_index:].copy()

    print(
        f"Validation rows: {len(validation):,}"
    )

    fraud_rows = validation[
        validation["isFraud"] == 1
    ].copy()

    print(
        f"Real validation fraud rows: "
        f"{len(fraud_rows):,}"
    )

    return fraud_rows


# ============================================================
# LOAD MODEL + PREPROCESSING
# ============================================================

def load_model_components():

    print("\n")
    print("=" * 80)
    print("LOADING MODEL")
    print("=" * 80)

    model = joblib.load(
        MODEL_DIR / "lightgbm_final.pkl"
    )

    with open(
        MODEL_DIR / "lightgbm_config.json",
        "r",
        encoding="utf-8",
    ) as f:
        model_config = json.load(f)

    entity_maps = joblib.load(
        PREPROCESSING_DIR / "entity_maps.pkl"
    )

    pair_map = joblib.load(
        PREPROCESSING_DIR / "pair_map.pkl"
    )

    card_device_map = joblib.load(
        PREPROCESSING_DIR / "card_device_map.pkl"
    )

    device_card_map = joblib.load(
        PREPROCESSING_DIR / "device_card_map.pkl"
    )

    encoder = joblib.load(
        PREPROCESSING_DIR / "onehot_encoder.pkl"
    )

    feature_config = joblib.load(
        PREPROCESSING_DIR / "feature_config.pkl"
    )

    temporal_config = joblib.load(
        PREPROCESSING_DIR / "temporal_config.pkl"
    )

    numeric_features = list(
        feature_config["numeric_features"]
    )

    categorical_features = list(
        feature_config["categorical_features"]
    )

    encoded_feature_names = list(
        feature_config["encoded_feature_names"]
    )

    expected_features = (
        numeric_features
        + encoded_feature_names
    )

    print("Model and preprocessing loaded.")

    return {
        "model": model,
        "model_config": model_config,
        "entity_maps": entity_maps,
        "pair_map": pair_map,
        "card_device_map": card_device_map,
        "device_card_map": device_card_map,
        "encoder": encoder,
        "feature_config": feature_config,
        "temporal_config": temporal_config,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "encoded_feature_names": encoded_feature_names,
        "expected_features": expected_features,
    }


# ============================================================
# FAST BATCH FEATURE CREATION
#
# This reproduces the predictor's training-time preprocessing,
# but works on many rows at once.
# ============================================================

def create_batch_features(
    df: pd.DataFrame,
    components: dict,
) -> pd.DataFrame:

    data = df.copy()

    numeric_features = components[
        "numeric_features"
    ]

    categorical_features = components[
        "categorical_features"
    ]

    encoded_feature_names = components[
        "encoded_feature_names"
    ]

    expected_features = components[
        "expected_features"
    ]

    entity_maps = components[
        "entity_maps"
    ]

    pair_map = components[
        "pair_map"
    ]

    card_device_map = components[
        "card_device_map"
    ]

    device_card_map = components[
        "device_card_map"
    ]

    encoder = components[
        "encoder"
    ]

    temporal_config = components[
        "temporal_config"
    ]

    # --------------------------------------------------------
    # Amount
    # --------------------------------------------------------

    data["log_transaction_amount"] = np.log1p(
        data["TransactionAmt"]
    )

    # --------------------------------------------------------
    # Missingness
    # --------------------------------------------------------

    missing_columns = [
        "addr1",
        "addr2",
        "D7",
        "D12",
        "D13",
        "D14",
        "DeviceInfo",
    ]

    for column in missing_columns:

        data[f"{column}_missing"] = (
            data[column]
            .isna()
            .astype("int8")
        )

    # --------------------------------------------------------
    # Temporal
    # --------------------------------------------------------

    previous_time = temporal_config[
        "previous_transaction_dt"
    ]

    data["time_since_previous_transaction"] = (
        data["TransactionDT"]
        - previous_time
    )

    data["has_previous_transaction"] = 1

    # --------------------------------------------------------
    # Entity frequency
    # --------------------------------------------------------

    for column, mapping in entity_maps.items():

        data[
            f"{column}_transaction_count"
        ] = (
            data[column]
            .map(mapping)
            .fillna(0)
            .astype("int32")
        )

    # --------------------------------------------------------
    # card1 + DeviceInfo pair frequency
    # --------------------------------------------------------

    pair_index = pd.MultiIndex.from_frame(
        data[
            ["card1", "DeviceInfo"]
        ]
    )

    data[
        "card1_DeviceInfo_transaction_count"
    ] = (
        pair_index
        .map(pair_map)
        .fillna(0)
        .astype("int32")
    )

    # --------------------------------------------------------
    # card1 -> unique DeviceInfo
    # --------------------------------------------------------

    data[
        "card1_unique_DeviceInfo_count"
    ] = (
        data["card1"]
        .map(card_device_map)
        .fillna(0)
        .astype("int32")
    )

    # --------------------------------------------------------
    # DeviceInfo -> unique card1
    # --------------------------------------------------------

    data[
        "DeviceInfo_unique_card1_count"
    ] = (
        data["DeviceInfo"]
        .map(device_card_map)
        .fillna(0)
        .astype("int32")
    )

    # --------------------------------------------------------
    # Categorical preprocessing
    # --------------------------------------------------------

    for column in categorical_features:

        data[column] = data[column].fillna(
            "MISSING"
        )

    # --------------------------------------------------------
    # Numeric
    # --------------------------------------------------------

    X_num = data[
        numeric_features
    ].copy()

    # --------------------------------------------------------
    # One-hot
    # --------------------------------------------------------

    X_cat = encoder.transform(
        data[categorical_features]
    )

    X_cat = pd.DataFrame(
        X_cat,
        columns=encoded_feature_names,
        index=data.index,
    )

    # --------------------------------------------------------
    # Combine
    # --------------------------------------------------------

    X = pd.concat(
        [X_num, X_cat],
        axis=1,
    )

    # --------------------------------------------------------
    # Safety checks
    # --------------------------------------------------------

    if len(X.columns) != len(
        expected_features
    ):
        raise ValueError(
            f"Feature count mismatch. "
            f"Generated {len(X.columns)}, "
            f"expected {len(expected_features)}."
        )

    if list(X.columns) != expected_features:
        raise ValueError(
            "Feature order does not match "
            "the trained model."
        )

    return X


# ============================================================
# FAST RANKING
# ============================================================

def rank_real_fraud_cases(
    fraud_df: pd.DataFrame,
    components: dict,
    top_n: int = 25,
) -> pd.DataFrame:

    print("\n")
    print("=" * 80)
    print("FAST FRAUD CANDIDATE SEARCH")
    print("=" * 80)

    print(
        f"Preparing {len(fraud_df):,} "
        f"real fraud rows..."
    )

    # Create all model features at once.
    X = create_batch_features(
        fraud_df,
        components,
    )

    print(
        f"Feature matrix: {X.shape}"
    )

    # Direct LightGBM prediction.
    probabilities = components[
        "model"
    ].predict_proba(X)[:, 1]

    ranked = fraud_df.copy()

    ranked[
        "fast_fraud_probability"
    ] = probabilities

    ranked = ranked.sort_values(
        "fast_fraud_probability",
        ascending=False,
    )

    candidates = ranked.head(top_n).copy()

    print(
        f"\nSelected top {len(candidates)} "
        f"real fraud candidates."
    )

    print(
        "\nHighest model probabilities:"
    )

    print(
        candidates[
            [
                "TransactionID",
                "TransactionAmt",
                "ProductCD",
                "card4",
                "card6",
                "DeviceType",
                "fast_fraud_probability",
            ]
        ].to_string(index=False)
    )

    return candidates


# ============================================================
# FULL TRACE SCORING
# ============================================================

def score_trace_candidates(
    candidates: pd.DataFrame,
):

    print("\n")
    print("=" * 80)
    print("FULL TRACE SCORING")
    print("=" * 80)

    # Existing TRACE predictor.
    predictor = FraudPredictor(
        MODEL_DIR / "lightgbm_final.pkl",
        MODEL_DIR / "lightgbm_config.json",
        PREPROCESSING_DIR,
    )

    anomaly_engine = AnomalyEngine(
        config_path=MODEL_DIR / "anomaly_config.json"
    )

    # Correct EntityRiskEngine initialization.
    entity_engine = EntityRiskEngine(
        entity_maps=joblib.load(
            PREPROCESSING_DIR / "entity_maps.pkl"
        ),
        pair_map=joblib.load(
            PREPROCESSING_DIR / "pair_map.pkl"
        ),
        card_device_map=joblib.load(
            PREPROCESSING_DIR / "card_device_map.pkl"
        ),
        device_card_map=joblib.load(
            PREPROCESSING_DIR / "device_card_map.pkl"
        ),
    )

    risk_engine = RiskEngine()
    decision_engine = DecisionEngine()

    results = []

    total = len(candidates)

    # Only ~25 rows reach this loop.
    for position, (_, row) in enumerate(
        candidates.iterrows(),
        start=1,
    ):

        print(
            f"\n[{position}/{total}] "
            f"TransactionID={row['TransactionID']}"
        )

        raw = {}

        for column in RAW_COLUMNS:

            value = row[column]

            if pd.isna(value):
                raw[column] = None
            else:
                raw[column] = value

        transaction = pd.DataFrame(
            [raw]
        )

        try:

            # ------------------------------------------------
            # 1. Existing ML predictor
            # ------------------------------------------------

            ml = predictor.predict(
                transaction
            )

            fraud_probability = float(
                ml["fraud_probability"]
            )

            # ------------------------------------------------
            # 2. Existing anomaly engine
            # ------------------------------------------------

            engineered = (
                predictor._create_features(
                    transaction
                )
            )

            anomaly_input = (
                engineered.iloc[0].to_dict()
            )

            anomaly = anomaly_engine.score(
                anomaly_input
            )

            anomaly_score = float(
                anomaly["anomaly_score"]
            )

            # ------------------------------------------------
            # 3. Existing entity engine
            # ------------------------------------------------

            entity = entity_engine.calculate(
                transaction
            )

            entity_risk = float(
                entity["entity_risk"]
            )

            # ------------------------------------------------
            # 4. Existing TRACE RiskEngine
            # ------------------------------------------------

            risk = risk_engine.calculate(
                fraud_probability,
                anomaly_score,
                entity_risk,
            )

            risk_score = float(
                risk["risk_score"]
            )

            # ------------------------------------------------
            # 5. Existing DecisionEngine
            # ------------------------------------------------

            decision = decision_engine.decide(
                risk_score
            )

            results.append(
                {
                    "TransactionID": int(
                        row["TransactionID"]
                    ),

                    "TransactionAmt": float(
                        row["TransactionAmt"]
                    ),

                    "ProductCD": row["ProductCD"],
                    "card4": row["card4"],
                    "card6": row["card6"],
                    "DeviceType": row["DeviceType"],

                    "isFraud": 1,

                    "fraud_probability":
                        fraud_probability,

                    "anomaly_score":
                        anomaly_score,

                    "entity_risk":
                        entity_risk,

                    "risk_score":
                        risk_score,

                    "risk_level":
                        decision["risk_level"],

                    "decision":
                        decision["decision"],
                }
            )

            print(
                f"  Fraud       : "
                f"{fraud_probability:.4f}"
            )

            print(
                f"  Anomaly     : "
                f"{anomaly_score:.4f}"
            )

            print(
                f"  Entity      : "
                f"{entity_risk:.4f}"
            )

            print(
                f"  Risk Score  : "
                f"{risk_score:.2f}"
            )

            print(
                f"  Decision    : "
                f"{decision['decision']}"
            )

        except Exception as exc:

            print(
                f"  ERROR: "
                f"{type(exc).__name__}: {exc}"
            )

    if not results:

        raise RuntimeError(
            "No candidate was successfully scored."
        )

    results_df = pd.DataFrame(
        results
    )

    results_df = results_df.sort_values(
        "risk_score",
        ascending=False,
    ).reset_index(drop=True)

    return results_df


# ============================================================
# DISPLAY FINAL RESULT
# ============================================================

def show_results(
    results: pd.DataFrame,
):

    print("\n")
    print("=" * 100)
    print("FINAL TRACE RESULTS")
    print("=" * 100)

    display_columns = [
        "TransactionID",
        "TransactionAmt",
        "fraud_probability",
        "anomaly_score",
        "entity_risk",
        "risk_score",
        "risk_level",
        "decision",
    ]

    print(
        results[
            display_columns
        ].to_string(index=False)
    )

    # --------------------------------------------------------
    # Decision counts
    # --------------------------------------------------------

    print("\n")
    print("=" * 100)
    print("DECISION SUMMARY")
    print("=" * 100)

    decision_counts = (
        results["decision"]
        .astype(str)
        .str.upper()
        .value_counts()
    )

    print(
        f"BLOCK  : "
        f"{decision_counts.get('BLOCK', 0)}"
    )

    print(
        f"REVIEW : "
        f"{decision_counts.get('REVIEW', 0)}"
    )

    print(
        f"ALLOW  : "
        f"{decision_counts.get('ALLOW', 0)}"
    )

    # --------------------------------------------------------
    # Highest risk case
    # --------------------------------------------------------

    best = results.iloc[0]

    print("\n")
    print("=" * 100)
    print("HIGHEST-RISK REAL FRAUD CASE")
    print("=" * 100)

    for column in display_columns:

        print(
            f"{column:22s}: "
            f"{best[column]}"
        )

    # --------------------------------------------------------
    # Genuine BLOCK case
    # --------------------------------------------------------

    blocks = results[
        results["decision"]
        .astype(str)
        .str.upper()
        == "BLOCK"
    ]

    print("\n")

    if len(blocks) > 0:

        block = blocks.iloc[0]

        print("=" * 100)
        print("GENUINE BLOCK CASE FOUND")
        print("=" * 100)

        print(
            f"TransactionID : "
            f"{block['TransactionID']}"
        )

        print(
            f"Amount        : "
            f"{block['TransactionAmt']}"
        )

        print(
            f"Fraud Prob.   : "
            f"{block['fraud_probability']:.4f}"
        )

        print(
            f"Anomaly       : "
            f"{block['anomaly_score']:.4f}"
        )

        print(
            f"Entity Risk   : "
            f"{block['entity_risk']:.4f}"
        )

        print(
            f"Risk Score    : "
            f"{block['risk_score']:.2f}"
        )

        print(
            f"Decision      : "
            f"{block['decision']}"
        )

    else:

        print("=" * 100)
        print("NO BLOCK CASE FOUND AMONG TOP CANDIDATES")
        print("=" * 100)

        print(
            "The highest-risk genuine fraud case "
            "is shown above."
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 100)
    print("TRACE — REAL FRAUD VALIDATION SEARCH")
    print("=" * 100)

    # --------------------------------------------------------
    # 1. Load genuine validation fraud rows
    # --------------------------------------------------------

    fraud_df = load_validation_data()

    # --------------------------------------------------------
    # 2. Load model + preprocessing
    # --------------------------------------------------------

    components = load_model_components()

    # --------------------------------------------------------
    # 3. Fast ranking
    #
    # Thousands of rows are scored directly by LightGBM.
    # No row-by-row TRACE loop here.
    # --------------------------------------------------------

    candidates = rank_real_fraud_cases(
        fraud_df,
        components,
        top_n=25,
    )

    # --------------------------------------------------------
    # 4. Full TRACE pipeline on only 25 candidates
    # --------------------------------------------------------

    results = score_trace_candidates(
        candidates
    )

    # --------------------------------------------------------
    # 5. Save results
    # --------------------------------------------------------

    results.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    # --------------------------------------------------------
    # 6. Display
    # --------------------------------------------------------

    show_results(
        results
    )

    print("\n")
    print("=" * 100)
    print("SAVED RESULT")
    print("=" * 100)
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
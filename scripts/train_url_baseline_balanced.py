from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import joblib
import pandas as pd

from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    average_precision_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)

from backend.features.live_url_features import (
    FEATURE_NAMES,
    extract_url_features,
)

SPLIT_DIR = ROOT / "data/processed/research_splits_balanced"
METADATA_PATH = SPLIT_DIR / "split_metadata.json"

MODEL_DIR = ROOT / "models/research_balanced"
REPORT_DIR = ROOT / "reports/research_balanced"


def build_features(df):
    rows = []

    for url in df["url"]:
        try:
            rows.append(extract_url_features(str(url)))
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"Could not extract features for URL {url!r}: {exc}"
            ) from exc

    features = pd.DataFrame(rows, columns=FEATURE_NAMES)

    if list(features.columns) != FEATURE_NAMES:
        raise ValueError("Extracted feature order does not match FEATURE_NAMES.")

    return features


def calculate_metrics(y_true, probabilities, predictions):
    return {
        "accuracy": float(accuracy_score(y_true, predictions)),
        "precision_phishing": float(
            precision_score(y_true, predictions, pos_label=1, zero_division=0)
        ),
        "recall_phishing": float(
            recall_score(y_true, predictions, pos_label=1, zero_division=0)
        ),
        "f1_phishing": float(
            f1_score(y_true, predictions, pos_label=1, zero_division=0)
        ),
        "pr_auc_average_precision": float(
            average_precision_score(y_true, probabilities)
        ),
        "roc_auc": float(roc_auc_score(y_true, probabilities)),
        "confusion_matrix": confusion_matrix(
            y_true, predictions, labels=[0, 1]
        ).tolist(),
    }


def validate_partitions(parts):
    required = {"sample_id", "url", "label", "domain_group"}

    for name, df in parts.items():
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"{name} is missing columns: {sorted(missing)}")

        if df[["sample_id", "url", "label", "domain_group"]].isna().any().any():
            raise ValueError(f"{name} has missing required values.")

        if not set(df["label"].unique()).issubset({0, 1}):
            raise ValueError(f"{name} has labels other than 0 and 1.")

        if df["label"].nunique() != 2:
            raise ValueError(f"{name} must contain both label classes.")

    for i, first_name in enumerate(parts):
        for second_name in list(parts)[i + 1:]:
            first = parts[first_name]
            second = parts[second_name]

            overlap = set(first["domain_group"]) & set(second["domain_group"])
            if overlap:
                raise ValueError(
                    f"Domain overlap between {first_name} and {second_name}: "
                    f"{len(overlap)} groups."
                )

    all_ids = pd.concat(
        [df["sample_id"] for df in parts.values()],
        ignore_index=True,
    )

    if all_ids.duplicated().any():
        raise ValueError("Duplicate sample IDs found across split files.")

    if METADATA_PATH.exists():
        metadata = json.loads(METADATA_PATH.read_text())
        expected = metadata.get("records")

        if expected is not None and len(all_ids) != expected:
            raise ValueError(
                f"Split record count {len(all_ids)} does not match "
                f"metadata record count {expected}."
            )


def main():
    for path in [
        SPLIT_DIR / "train.csv",
        SPLIT_DIR / "validation.csv",
        SPLIT_DIR / "test.csv",
        METADATA_PATH,
    ]:
        if not path.exists():
            raise FileNotFoundError(f"Required file not found: {path}")

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    split_metadata = json.loads(METADATA_PATH.read_text())

    parts = {
        name: pd.read_csv(SPLIT_DIR / f"{name}.csv")
        for name in ["train", "validation", "test"]
    }

    validate_partitions(parts)

    for name, df in parts.items():
        print(
            f"{name}: {len(df)} records, "
            f"{df['domain_group'].nunique()} groups, "
            f"phishing rate {df['label'].mean():.4f}"
        )

    X_train = build_features(parts["train"])
    X_val = build_features(parts["validation"])
    X_test = build_features(parts["test"])

    y_train = parts["train"]["label"].astype(int)
    y_val = parts["validation"]["label"].astype(int)
    y_test = parts["test"]["label"].astype(int)

    candidates = {
        "logistic_regression": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=42,
            )),
        ]),
        "random_forest": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("classifier", RandomForestClassifier(
                n_estimators=300,
                min_samples_leaf=2,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            )),
        ]),
    }

    validation_results = {}

    # Use validation data for model selection only.
    for name, model in candidates.items():
        model.fit(X_train, y_train)
        probabilities = model.predict_proba(X_val)[:, 1]
        predictions = (probabilities >= 0.5).astype(int)

        validation_results[name] = calculate_metrics(
            y_val, probabilities, predictions
        )

        print(f"\n{name} — VALIDATION")
        print(json.dumps(validation_results[name], indent=2))

    selected_name = max(
        validation_results,
        key=lambda name: validation_results[name]["f1_phishing"],
    )
    selected_model = candidates[selected_name]

    # Evaluate the selected model on the test set after selection.
    test_probabilities = selected_model.predict_proba(X_test)[:, 1]
    test_predictions = (test_probabilities >= 0.5).astype(int)

    test_metrics = calculate_metrics(
        y_test, test_probabilities, test_predictions
    )

    print(f"\nSelected model: {selected_name}")
    print("\nSelected model — TEST")
    print(json.dumps(test_metrics, indent=2))
    print("\nTest classification report:")
    print(classification_report(
        y_test,
        test_predictions,
        labels=[0, 1],
        target_names=["legitimate", "phishing"],
        zero_division=0,
    ))

    artifact = {
        "model": selected_model,
        "model_name": selected_name,
        "features": FEATURE_NAMES,
        "positive_label": 1,
        "label_mapping": {0: "legitimate", 1: "phishing"},
        "decision_threshold": 0.5,
        "split_seed": split_metadata["selected_seed"],
        "split_strategy": split_metadata["method"],
        "split_metadata_path": str(
            METADATA_PATH.relative_to(ROOT)
        ),
    }

    model_path = MODEL_DIR / "url_baseline.joblib"
    joblib.dump(artifact, model_path)

    report = {
        "experiment": "URL-only baseline using balanced group-disjoint splits",
        "selected_model": selected_name,
        "selection_metric": "validation_f1_phishing",
        "decision_threshold": 0.5,
        "validation_results": validation_results,
        "test_results": test_metrics,
        "train_records": len(parts["train"]),
        "validation_records": len(parts["validation"]),
        "test_records": len(parts["test"]),
        "train_domains": int(parts["train"]["domain_group"].nunique()),
        "validation_domains": int(parts["validation"]["domain_group"].nunique()),
        "test_domains": int(parts["test"]["domain_group"].nunique()),
        "split_seed": split_metadata["selected_seed"],
        "split_strategy": split_metadata["method"],
        "model_performance_used_for_split_selection": False,
        "feature_names": FEATURE_NAMES,
    }

    report_path = REPORT_DIR / "url_baseline_metrics.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")

    print(f"\nSaved model: {model_path}")
    print(f"Saved metrics: {report_path}")
    print("Original model and original experiment files were not modified.")


if __name__ == "__main__":
    main()

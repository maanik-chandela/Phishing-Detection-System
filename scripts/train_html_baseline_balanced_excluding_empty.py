from pathlib import Path
import json
import warnings

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.features.html_features import (
    extract_html_features,
    HTML_FEATURE_NAMES,
)

ROOT = Path(__file__).resolve().parents[1]
SPLIT_DIR = ROOT / "data/processed/research_splits_balanced"
OUT_DIR = ROOT / "models/research_balanced/html_live_excluding_empty"
REPORT_DIR = ROOT / "reports/research_balanced/html_live_excluding_empty"

SPLITS = ("train", "validation", "test")


def resolve_path(value):
    path = Path(str(value))
    return path if path.is_absolute() else ROOT / path


def load_and_extract(split_name):
    path = SPLIT_DIR / f"{split_name}.csv"
    df = pd.read_csv(path)

    required = {
        "sample_id", "url", "label", "html_path", "domain_group"
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{split_name}: missing columns {sorted(missing)}")

    df["label"] = pd.to_numeric(df["label"], errors="raise").astype(int)
    if not set(df["label"].unique()).issubset({0, 1}):
        raise ValueError(f"{split_name}: labels must be 0 or 1")

    records = []
    excluded = []

    for row in df.to_dict("records"):
        html_path = resolve_path(row["html_path"])

        try:
            if not html_path.is_file():
                raise ValueError("HTML file does not exist")

            html = html_path.read_text(encoding="utf-8", errors="replace")
            if not html.strip():
                raise ValueError("Empty HTML content")

            features = extract_html_features(html, str(row["url"]))

            if set(features) != set(HTML_FEATURE_NAMES):
                raise ValueError(
                    f"Feature names mismatch: {sorted(features)}"
                )

            records.append({
                "sample_id": str(row["sample_id"]),
                "label": int(row["label"]),
                "domain_group": str(row["domain_group"]),
                "features": features,
            })

        except Exception as exc:
            excluded.append({
                "sample_id": str(row["sample_id"]),
                "url": str(row["url"]),
                "html_path": str(row["html_path"]),
                "reason": str(exc),
            })

    if not records:
        raise RuntimeError(f"{split_name}: no usable HTML records")

    X = pd.DataFrame(
        [r["features"] for r in records],
        columns=HTML_FEATURE_NAMES,
    )
    y = pd.Series([r["label"] for r in records], dtype=int)
    groups = {r["domain_group"] for r in records}

    return {
        "X": X,
        "y": y,
        "groups": groups,
        "records": records,
        "original_rows": len(df),
        "excluded": excluded,
    }


def metrics(y_true, probabilities, threshold=0.5):
    predictions = (probabilities >= threshold).astype(int)
    return {
        "threshold": threshold,
        "accuracy": float(accuracy_score(y_true, predictions)),
        "precision_phishing": float(
            precision_score(y_true, predictions, zero_division=0)
        ),
        "recall_phishing": float(
            recall_score(y_true, predictions, zero_division=0)
        ),
        "f1_phishing": float(
            f1_score(y_true, predictions, zero_division=0)
        ),
        "average_precision": float(
            average_precision_score(y_true, probabilities)
        ),
        "roc_auc": float(roc_auc_score(y_true, probabilities)),
        "confusion_matrix": confusion_matrix(
            y_true, predictions, labels=[0, 1]
        ).tolist(),
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    data = {name: load_and_extract(name) for name in SPLITS}

    # Confirm that filtering has not introduced cross-split domain overlap.
    for i, left in enumerate(SPLITS):
        for right in SPLITS[i + 1:]:
            overlap = data[left]["groups"] & data[right]["groups"]
            if overlap:
                raise RuntimeError(
                    f"Domain leakage between {left} and {right}: "
                    f"{len(overlap)} overlapping groups"
                )

    print("DATA AUDIT")
    for name in SPLITS:
        item = data[name]
        y = item["y"]
        print(
            f"{name}: original={item['original_rows']}, "
            f"usable={len(y)}, excluded={len(item['excluded'])}, "
            f"domains={len(item['groups'])}, "
            f"phishing_rate={y.mean():.4f}"
        )

    X_train, y_train = data["train"]["X"], data["train"]["y"]
    X_val, y_val = data["validation"]["X"], data["validation"]["y"]
    X_test, y_test = data["test"]["X"], data["test"]["y"]

    candidates = {
        "logistic_regression": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=20261381,
            )),
        ]),
        "random_forest": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("classifier", RandomForestClassifier(
                n_estimators=400,
                class_weight="balanced",
                random_state=20261381,
                n_jobs=-1,
            )),
        ]),
    }

    validation_results = {}
    fitted_models = {}

    for name, model in candidates.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)
        val_prob = model.predict_proba(X_val)[:, 1]
        val_metrics = metrics(y_val, val_prob)
        validation_results[name] = val_metrics
        fitted_models[name] = model
        print(json.dumps(val_metrics, indent=2))

    selected_name = max(
        validation_results,
        key=lambda name: validation_results[name]["f1_phishing"],
    )
    selected_model = fitted_models[selected_name]

    # Test set is used only after selection using validation F1.
    test_prob = selected_model.predict_proba(X_test)[:, 1]
    test_metrics = metrics(y_test, test_prob)

    model_path = OUT_DIR / "selected_live_html_model.joblib"
    joblib.dump({
        "model": selected_model,
        "feature_names": HTML_FEATURE_NAMES,
        "selected_model": selected_name,
        "threshold": 0.5,
        "excluded_empty_html_policy": (
            "Rows with missing, unreadable, or empty HTML are excluded "
            "from this experiment; no missing record is labelled legitimate."
        ),
    }, model_path)

    exclusions = {
        name: data[name]["excluded"] for name in SPLITS
    }
    exclusion_path = REPORT_DIR / "excluded_records.json"
    exclusion_path.write_text(json.dumps(exclusions, indent=2))

    report = {
        "experiment": "live_html_five_features_excluding_unavailable_html",
        "features": HTML_FEATURE_NAMES,
        "split_policy": "Original domain-disjoint splits; unavailable HTML excluded per split",
        "original_rows": {
            name: data[name]["original_rows"] for name in SPLITS
        },
        "usable_rows": {
            name: len(data[name]["y"]) for name in SPLITS
        },
        "excluded_rows": {
            name: len(data[name]["excluded"]) for name in SPLITS
        },
        "domain_counts": {
            name: len(data[name]["groups"]) for name in SPLITS
        },
        "validation_metrics": validation_results,
        "selected_model": selected_name,
        "selection_rule": "Highest validation phishing-class F1 at threshold 0.5",
        "test_metrics": test_metrics,
        "model_path": str(model_path.relative_to(ROOT)),
        "excluded_records_path": str(exclusion_path.relative_to(ROOT)),
        "caveat": (
            "Results apply to this dataset and split only. This is a five-feature "
            "live HTML experiment, not the 23-feature workbook HTML experiment "
            "and not proof of real-world deployment performance."
        ),
    }

    report_path = REPORT_DIR / "experiment_summary.json"
    report_path.write_text(json.dumps(report, indent=2))

    print("\nSELECTED MODEL:", selected_name)
    print("\nFINAL TEST METRICS")
    print(json.dumps(test_metrics, indent=2))
    print(f"\nSaved model: {model_path}")
    print(f"Saved report: {report_path}")
    print(f"Saved exclusions: {exclusion_path}")


if __name__ == "__main__":
    main()

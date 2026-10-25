from pathlib import Path
from urllib.parse import urlsplit
from ipaddress import ip_address

import pandas as pd
import joblib

from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
)
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)

from backend.features.live_url_features import (
    extract_url_features,
    FEATURE_NAMES,
)


ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data/raw/All_Features_threshold90.xlsx"

MODEL_DIR = ROOT / "models"
REPORT_DIR = ROOT / "reports"

MODEL_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)


def get_domain_group(url):

    hostname = urlsplit(url).hostname or ""

    try:
        ip_address(hostname)
        return hostname
    except ValueError:
        pass

    import tldextract

    result = tldextract.extract(hostname)

    return result.top_domain_under_public_suffix or hostname


def main():

    print("Loading original dataset...")

    df = pd.read_excel(
        INPUT_FILE,
        usecols=["url", "label"]
    )

    df = df.dropna(subset=["url", "label"])

    df["url"] = df["url"].astype(str).str.strip()

    # Remove URLs with contradictory labels.
    conflicts = df.groupby("url")["label"].nunique()
    bad_urls = conflicts[conflicts > 1].index

    df = df[~df["url"].isin(bad_urls)]

    df = df.drop_duplicates(subset=["url"])

    records = []
    labels = []
    groups = []

    print("Extracting URL features...")

    for _, row in df.iterrows():

        try:
            features = extract_url_features(row["url"])
            group = get_domain_group(row["url"])

            records.append(features)
            labels.append(int(row["label"]))
            groups.append(group)

        except (ValueError, TypeError):
            continue

    X = pd.DataFrame(records)[FEATURE_NAMES]
    y = pd.Series(labels)
    groups = pd.Series(groups)

    if set(y.unique()) != {0, 1}:
        raise ValueError("Both classes must be present")

    print("Usable samples:", len(X))
    print("Features:", len(FEATURE_NAMES))

    # Separate test domains from development domains.
    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=0.20,
        random_state=42,
    )

    dev_idx, test_idx = next(
        splitter.split(X, y, groups)
    )

    X_dev = X.iloc[dev_idx]
    X_test = X.iloc[test_idx]

    y_dev = y.iloc[dev_idx]
    y_test = y.iloc[test_idx]

    groups_dev = groups.iloc[dev_idx]

    # Create a validation set from the development data.
    val_splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=0.20,
        random_state=43,
    )

    train_idx, val_idx = next(
        val_splitter.split(
            X_dev,
            y_dev,
            groups_dev,
        )
    )

    X_train = X_dev.iloc[train_idx]
    X_val = X_dev.iloc[val_idx]

    y_train = y_dev.iloc[train_idx]
    y_val = y_dev.iloc[val_idx]

    print("Training samples:", len(X_train))
    print("Validation samples:", len(X_val))
    print("Testing samples:", len(X_test))

    models = {
        "LogisticRegression": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=42,
            )),
        ]),

        "RandomForest": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("classifier", RandomForestClassifier(
                n_estimators=200,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            )),
        ]),

        "GradientBoosting": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("classifier", GradientBoostingClassifier(
                random_state=42,
            )),
        ]),
    }

    results = []
    fitted_models = {}

    for name, model in models.items():

        print(f"\nTraining {name}...")

        model.fit(X_train, y_train)

        predictions = model.predict(X_val)

        scores = {
            "model": name,
            "accuracy": accuracy_score(y_val, predictions),
            "precision": precision_score(
                y_val, predictions, zero_division=0
            ),
            "recall": recall_score(
                y_val, predictions, zero_division=0
            ),
            "f1": f1_score(
                y_val, predictions, zero_division=0
            ),
        }

        results.append(scores)
        fitted_models[name] = model

        print(scores)

    results_df = pd.DataFrame(results)

    results_df = results_df.sort_values(
        "f1",
        ascending=False
    )

    results_df.to_csv(
        REPORT_DIR / "model_comparison.csv",
        index=False
    )

    best_name = results_df.iloc[0]["model"]
    best_model = fitted_models[best_name]

    print("\nSelected model:", best_name)

    test_predictions = best_model.predict(X_test)

    print("\nHELD-OUT TEST RESULTS")

    print(
        classification_report(
            y_test,
            test_predictions,
            zero_division=0,
        )
    )

    print(
        confusion_matrix(
            y_test,
            test_predictions,
        )
    )

    joblib.dump(
        {
            "model": best_model,
            "features": FEATURE_NAMES,
            "model_name": best_name,
            "label_mapping": {
                0: "legitimate",
                1: "phishing",
            },
        },
        MODEL_DIR / "url_model.joblib"
    )

    print("\nSaved: models/url_model.joblib")


if __name__ == "__main__":
    main()
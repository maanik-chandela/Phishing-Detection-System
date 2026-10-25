from pathlib import Path

import pandas as pd
import joblib

from sklearn.model_selection import train_test_split

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
    confusion_matrix,
    classification_report,
)


ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT / "data/processed/training_data.csv"

MODEL_DIR = ROOT / "models"

RESULTS_DIR = ROOT / "data/processed"

MODEL_DIR.mkdir(exist_ok=True)

RESULTS_DIR.mkdir(exist_ok=True)


def main():

    print("Loading training data...")

    df = pd.read_csv(DATA_PATH)

    X = df.drop(
        columns=["url", "label"]
    )

    y = df["label"]

    feature_names = X.columns.tolist()

    print("Total samples:", len(df))

    print("Total features:", len(feature_names))

    # 70% training, 15% validation, 15% testing.
    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=42,
        stratify=y
    )

    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        random_state=42,
        stratify=y_temp
    )

    print("\nDataset split:")

    print("Training:", len(X_train))
    print("Validation:", len(X_val))
    print("Testing:", len(X_test))

    models = {

        "Logistic_Regression": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=42
            ))
        ]),

        "Random_Forest": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("classifier", RandomForestClassifier(
                n_estimators=200,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1
            ))
        ]),

        "Gradient_Boosting": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("classifier", GradientBoostingClassifier(
                random_state=42
            ))
        ]),
    }

    results = []

    trained_models = {}

    for name, model in models.items():

        print("\n" + "=" * 50)
        print("Training:", name)
        print("=" * 50)

        model.fit(X_train, y_train)

        predictions = model.predict(X_val)

        accuracy = accuracy_score(
            y_val,
            predictions
        )

        precision = precision_score(
            y_val,
            predictions,
            zero_division=0
        )

        recall = recall_score(
            y_val,
            predictions,
            zero_division=0
        )

        f1 = f1_score(
            y_val,
            predictions,
            zero_division=0
        )

        print("\nValidation results:")

        print("Accuracy:", round(accuracy, 4))
        print("Precision:", round(precision, 4))
        print("Recall:", round(recall, 4))
        print("F1 Score:", round(f1, 4))

        print("\nConfusion Matrix:")

        print(
            confusion_matrix(
                y_val,
                predictions
            )
        )

        print("\nClassification Report:")

        print(
            classification_report(
                y_val,
                predictions,
                zero_division=0
            )
        )

        results.append({
            "Model": name,
            "Accuracy": accuracy,
            "Precision": precision,
            "Recall": recall,
            "F1": f1
        })

        trained_models[name] = model

        joblib.dump(
            model,
            MODEL_DIR / f"{name}.joblib"
        )

    results_df = pd.DataFrame(results)

    results_df = results_df.sort_values(
        by="F1",
        ascending=False
    )

    print("\nFINAL VALIDATION COMPARISON")

    print(results_df)

    results_df.to_csv(
        RESULTS_DIR / "model_comparison.csv",
        index=False
    )

    best_name = results_df.iloc[0]["Model"]

    best_model = trained_models[best_name]

    print("\nSelected model:", best_name)

    # Evaluate the selected model on the held-out test set.
    test_predictions = best_model.predict(X_test)

    print("\nFINAL TEST RESULTS")

    print(
        classification_report(
            y_test,
            test_predictions,
            zero_division=0
        )
    )

    print("\nTest Confusion Matrix:")

    print(
        confusion_matrix(
            y_test,
            test_predictions
        )
    )

    joblib.dump(
        best_model,
        MODEL_DIR / "final_model.joblib"
    )

    joblib.dump(
        feature_names,
        MODEL_DIR / "feature_names.joblib"
    )

    print("\nTraining completed successfully!")

    print("Final model saved.")


if __name__ == "__main__":
    main()
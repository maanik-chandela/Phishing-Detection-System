import json
from pathlib import Path

import joblib
import pandas as pd

from backend.features.live_url_features import FEATURE_NAMES


ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models/research_balanced"
SPLIT_DIR = ROOT / "data/processed/research_splits_balanced"
REPORT_DIR = ROOT / "reports/research_balanced"


def test_url_baseline_artifact_alignment():
    model_path = MODEL_DIR / "url_baseline.joblib"
    assert model_path.exists()
    artifact = joblib.load(model_path)
    assert artifact["features"] == FEATURE_NAMES
    assert artifact["model_name"] in ("logistic_regression", "random_forest")
    assert artifact["decision_threshold"] == 0.5

    # check splits used are disjoint
    parts = {k: pd.read_csv(SPLIT_DIR / f"{k}.csv") for k in ["train", "validation", "test"]}
    for a, b in [("train", "validation"), ("train", "test"), ("validation", "test")]:
        ov = set(parts[a]["domain_group"]) & set(parts[b]["domain_group"])
        assert len(ov) == 0

    # check metrics exist and have required fields
    metrics_path = REPORT_DIR / "url_baseline_metrics.json"
    assert metrics_path.exists()
    m = json.loads(metrics_path.read_text())
    for k in ["test_results", "train_records", "validation_records", "test_records"]:
        assert k in m
    tr = m["test_results"]
    for k in ["accuracy", "precision_phishing", "recall_phishing", "f1_phishing", "pr_auc_average_precision", "roc_auc", "confusion_matrix"]:
        assert k in tr

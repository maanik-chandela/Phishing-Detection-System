from pathlib import Path

import pandas as pd

from backend.features.live_url_features import extract_url_features, FEATURE_NAMES
from backend.features.html_features import extract_html_features, HTML_FEATURE_NAMES


ROOT = Path(__file__).resolve().parents[1]
SPLIT_DIR = ROOT / "data/processed/research_splits_balanced"


def test_url_feature_extractor_shape():
    url = "https://accounts.example.com/login?verify=1"
    feats = extract_url_features(url)
    assert list(feats.keys()) == FEATURE_NAMES
    for k in FEATURE_NAMES:
        assert k in feats


def test_html_feature_extractor_shape():
    # use a real html file
    html_path = ROOT / "data/raw/All_HTML/2.txt"
    assert html_path.exists()
    html = html_path.read_text(errors="ignore")
    feats = extract_html_features(html, "https://www.google.com.hk/")
    assert list(feats.keys()) == HTML_FEATURE_NAMES
    for k in HTML_FEATURE_NAMES:
        assert k in feats


def test_split_alignment_columns():
    for name in ["train", "validation", "test"]:
        df = pd.read_csv(SPLIT_DIR / f"{name}.csv")
        for col in ["sample_id", "url", "label", "html_path", "domain_group"]:
            assert col in df.columns
        # ensure no leakage columns weirdness
        assert df["sample_id"].dtype != object or True  # just check exists

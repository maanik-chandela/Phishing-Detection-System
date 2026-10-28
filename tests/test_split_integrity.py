import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SPLIT_DIR = ROOT / "data/processed/research_splits_balanced"


def test_balanced_splits_no_overlap_no_dups_valid_labels():
    parts = {}
    for name in ["train", "validation", "test"]:
        path = SPLIT_DIR / f"{name}.csv"
        assert path.exists(), f"missing split {path}"
        df = pd.read_csv(path)
        parts[name] = df

        # required columns
        for col in ["sample_id", "url", "label", "html_path", "domain_group", "html_available"]:
            assert col in df.columns, f"{name} missing {col}"

        # valid labels
        assert set(df["label"].unique()).issubset({0, 1})
        assert df["label"].nunique() == 2

        # no missing required
        assert not df[["sample_id", "url", "label", "domain_group"]].isna().any().any()

    # domain group disjoint
    for a, b in [("train", "validation"), ("train", "test"), ("validation", "test")]:
        ov = set(parts[a]["domain_group"]) & set(parts[b]["domain_group"])
        assert len(ov) == 0, f"domain overlap {a}-{b}: {len(ov)}"

    # no duplicate sample ids
    all_ids = pd.concat([parts[k]["sample_id"] for k in parts], ignore_index=True)
    assert all_ids.duplicated().sum() == 0

    # metadata consistency if exists
    meta_path = SPLIT_DIR / "split_metadata.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        if meta.get("records") is not None:
            assert len(all_ids) == int(meta["records"])

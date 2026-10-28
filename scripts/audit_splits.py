#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SPLIT_DIR = ROOT / "data/processed/research_splits_balanced"
REPORT_DIR = ROOT / "reports/research_balanced"


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    parts = {}
    for name in ["train", "validation", "test"]:
        path = SPLIT_DIR / f"{name}.csv"
        if not path.exists():
            raise FileNotFoundError(path)
        parts[name] = pd.read_csv(path)

    # Check required columns
    required = {"sample_id", "url", "label", "html_path", "domain_group", "html_available"}
    for name, df in parts.items():
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"{name} missing columns: {sorted(missing)}")
        if not set(df["label"].unique()).issubset({0, 1}):
            raise ValueError(f"{name} has invalid labels")
        if df["label"].nunique() != 2:
            raise ValueError(f"{name} missing a class")

    # Domain group overlap
    overlaps = {}
    for a, b in [("train", "validation"), ("train", "test"), ("validation", "test")]:
        ov = set(parts[a]["domain_group"]) & set(parts[b]["domain_group"])
        if ov:
            raise ValueError(f"Domain overlap {a}-{b}: {len(ov)}")
        overlaps[f"{a}_vs_{b}"] = 0

    # Duplicate sample IDs
    all_ids = pd.concat([parts[k]["sample_id"] for k in parts], ignore_index=True)
    if all_ids.duplicated().any():
        raise ValueError("Duplicate sample IDs across splits")

    report = {
        "split_dir": str(SPLIT_DIR),
        "overlap": overlaps,
        "duplicate_sample_ids": int(all_ids.duplicated().sum()),
        "parts": {},
    }

    for name, df in parts.items():
        report["parts"][name] = {
            "rows": int(len(df)),
            "domains": int(df["domain_group"].nunique()),
            "label_counts": df["label"].value_counts().to_dict(),
            "phishing_rate": float(df["label"].mean()),
            "html_available_true": int((df["html_available"] == True).sum()) if df["html_available"].dtype == bool else int((df["html_available"].astype(str) == "True").sum()),
        }

    out = REPORT_DIR / "split_audit.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    print(f"\nSaved audit: {out}")


if __name__ == "__main__":
    main()

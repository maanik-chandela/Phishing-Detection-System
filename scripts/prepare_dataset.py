from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    ROOT / "data/raw/All_Features_threshold90.xlsx"
)

OUTPUT_FILE = (
    ROOT / "data/processed/training_data.csv"
)

FEATURES = [
    "url_length",
    "domain_length",
    "url_contains_ip",
    "uses_https",
    "no_of_dots",
    "no_of_hyphen",
    "no_of_at",
    "special_characters_count",
    "num_query_params",
    "no_of_slashes_inpath",
    "hostname_digit_ratio",
    "brand_subdomain",
    "brand_substring_domain",
    "brand_typo_dom",
    "brand_in_path_query",
    "no_of_forms",
    "Script_loaded_from_ext_domain",
    "form_action_external",
    "has_redirections",
    "has_punycode",
]


def main():

    print("Loading dataset...")

    df = pd.read_excel(INPUT_FILE)

    print("Original shape:", df.shape)

    required_columns = [
        "url",
        "label",
        *FEATURES,
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    df = df[required_columns].copy()

    df["url"] = df["url"].astype(str).str.strip()

    df = df[df["url"] != ""]

    # Remove URLs with contradictory labels.
    conflicts = (
        df.groupby("url")["label"]
        .nunique()
    )

    conflicting_urls = conflicts[
        conflicts > 1
    ].index

    df = df[
        ~df["url"].isin(conflicting_urls)
    ]

    # Remove repeated URL records.
    df = df.drop_duplicates(
        subset=["url"]
    )

    # Convert feature columns to numerical values.
    for feature in FEATURES:
        df[feature] = pd.to_numeric(
            df[feature],
            errors="coerce"
        )

    df = df.dropna(
        subset=FEATURES + ["label"]
    )

    df["label"] = df["label"].astype(int)

    if not set(df["label"].unique()).issubset({0, 1}):
        raise ValueError("Unexpected label values")

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nCleaned dataset:", df.shape)

    print("\nClass distribution:")
    print(df["label"].value_counts())

    print("\nSaved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
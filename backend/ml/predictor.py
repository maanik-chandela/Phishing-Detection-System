from pathlib import Path

import joblib
import pandas as pd

from backend.features.live_url_features import (
    extract_url_features,
)


ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = ROOT / "models/url_model.joblib"


class PhishingPredictor:

    def __init__(self):

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                "Model not found. Run Module 9 first."
            )

        artifact = joblib.load(MODEL_PATH)

        self.model = artifact["model"]
        self.features = artifact["features"]
        self.model_name = artifact["model_name"]

    def predict(self, url: str):

        extracted = extract_url_features(url)

        X = pd.DataFrame(
            [extracted],
            columns=self.features
        )

        prediction = int(self.model.predict(X)[0])

        probabilities = self.model.predict_proba(X)[0]

        phishing_index = list(
            self.model.classes_
        ).index(1)

        phishing_probability = float(
            probabilities[phishing_index]
        )

        return {
            "url": url,
            "prediction": prediction,
            "phishing_probability": phishing_probability,
            "features": extracted,
            "model_name": self.model_name,
        }
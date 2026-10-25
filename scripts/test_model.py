from pathlib import Path
import joblib
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
model = joblib.load(
    ROOT / "models/final_model.joblib"
)
feature_names = joblib.load(
    ROOT / "models/feature_names.joblib"
)
df = pd.read_csv(
    ROOT / "data/processed/training_data.csv"
)
sample = df.iloc[[0]]

X_sample = sample[feature_names]

prediction = model.predict(X_sample)[0]

probability = model.predict_proba(X_sample)[0]

classes = model.classes_

phishing_index = list(classes).index(1)

phishing_probability = probability[phishing_index]

risk_score = round(
    phishing_probability * 100
)

print("\nURL:", sample.iloc[0]["url"])

print("Actual Label:", sample.iloc[0]["label"])

print(
    "Prediction:",
    "Phishing" if prediction == 1 else "Legitimate"
)

print(
    "Phishing Probability:",
    round(phishing_probability, 4)
)

print("Risk Score:", risk_score)
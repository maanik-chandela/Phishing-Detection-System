from backend.ml.predictor import PhishingPredictor
from backend.risk.risk_engine import assess_risk

predictor = PhishingPredictor()

result = predictor.predict(
    "https://example.com/login"
)

report = assess_risk(result)

print("\nPHISHING RISK REPORT")
print("====================")

print("URL:", report["url"])
print("Prediction:", report["prediction"])
print("Risk Score:", report["risk_score"])
print("Risk Level:", report["risk_level"])

print("\nIndicators:")

for indicator in report["indicators"]:
    print("-", indicator)

print("\nRecommendations:")

for recommendation in report["recommendations"]:
    print("-", recommendation)
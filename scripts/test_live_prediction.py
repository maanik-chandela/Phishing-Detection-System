from backend.ml.predictor import PhishingPredictor

predictor = PhishingPredictor()

urls = [
    "https://example.com",
    "https://accounts.example.com/login",
    "http://192.0.2.1/verify-account",
]

for url in urls:

    result = predictor.predict(url)

    print("\nURL:", url)
    print("Prediction:", result["prediction"])
    print(
        "Phishing probability:",
        result["phishing_probability"]
    )
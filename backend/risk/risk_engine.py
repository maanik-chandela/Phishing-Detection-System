def get_risk_level(score: int) -> str:

    if score < 25:
        return "Low"

    if score < 50:
        return "Medium"

    if score < 75:
        return "High"

    return "Critical"


def get_indicators(features: dict) -> list:

    indicators = []

    if features["url_contains_ip"] == 1:
        indicators.append(
            "The URL uses an IP address instead of a domain name."
        )

    if features["uses_https"] == 0:
        indicators.append(
            "The URL does not use HTTPS."
        )

    if features["url_length"] > 100:
        indicators.append(
            "The URL is unusually long."
        )

    if features["no_of_at"] > 0:
        indicators.append(
            "The URL contains an @ symbol."
        )

    if features["has_punycode"] == 1:
        indicators.append(
            "The hostname contains Punycode."
        )

    if features["hostname_digit_ratio"] > 0.3:
        indicators.append(
            "The hostname contains a high proportion of digits."
        )

    if features["num_query_params"] > 5:
        indicators.append(
            "The URL contains many query parameters."
        )

    return indicators


def get_recommendations(level: str) -> list:

    recommendations = [
        "Verify the website address before entering credentials.",
        "Never share OTPs, passwords, or payment information on unverified websites.",
    ]

    if level in ("High", "Critical"):

        recommendations.extend([
            "Avoid entering personal or financial information.",
            "Navigate to the official website independently.",
            "Do not download files from this website.",
        ])

    return recommendations


def assess_risk(prediction_result: dict) -> dict:

    probability = prediction_result["phishing_probability"]

    # This is an initial, uncalibrated model score.
    score = round(probability * 100)

    level = get_risk_level(score)

    indicators = get_indicators(
        prediction_result["features"]
    )

    return {
        **prediction_result,
        "risk_score": score,
        "risk_level": level,
        "indicators": indicators,
        "recommendations": get_recommendations(level),
        "score_calibrated": False,
        "analysis_mode": "URL-only",
    }
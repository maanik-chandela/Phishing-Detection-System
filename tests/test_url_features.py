from backend.features.url_features import extract_url_features


def test_url_features():

    url = (
        "https://accounts.example.com/"
        "login?verify=1"
    )

    features = extract_url_features(url)

    assert features["uses_https"] == 1

    assert features["subdomain_count"] == 1

    assert features["suspicious_keyword_count"] >= 1

    assert features["url_length"] > 0
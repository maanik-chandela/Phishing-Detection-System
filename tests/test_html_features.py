from backend.features.html_features import extract_html_features


def test_html_features():

    html = """
    <html>
        <form>
            <input type="password">
        </form>
        <iframe src="/help"></iframe>
    </html>
    """

    result = extract_html_features(
        html,
        "https://example.com"
    )

    assert result["password_field_count"] == 1

    assert result["form_count"] == 1

    assert result["iframe_count"] == 1
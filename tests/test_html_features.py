from backend.features.html_features import (
    extract_html_features,
)


def test_html_features():

    html = """
    <html>
      <body>

        <form action="https://other.example/submit">
          <input type="text">
          <input type="password">
        </form>

        <iframe src="/frame"></iframe>

        <script src="https://cdn.other.example/app.js"></script>

      </body>
    </html>
    """

    result = extract_html_features(
        html,
        "https://example.com/login"
    )

    assert result["html_password_fields"] == 1

    assert result["html_form_count"] == 1

    assert result["html_iframe_count"] == 1

    assert result["html_external_scripts"] == 1

    assert result["html_external_form_actions"] == 1

def test_empty_html_is_rejected():
    import pytest
    from backend.features.html_features import extract_html_features

    with pytest.raises(ValueError, match="HTML content is empty"):
        extract_html_features("", "https://example.com")


def test_whitespace_html_is_rejected():
    import pytest
    from backend.features.html_features import extract_html_features

    with pytest.raises(ValueError, match="HTML content is empty"):
        extract_html_features("   \n\t ", "https://example.com")


def test_empty_page_url_is_rejected():
    import pytest
    from backend.features.html_features import extract_html_features

    with pytest.raises(ValueError, match="Page URL is empty"):
        extract_html_features("<html><title>Test</title></html>", "")

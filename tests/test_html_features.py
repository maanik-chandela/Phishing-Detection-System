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
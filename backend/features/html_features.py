from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit

HTML_FEATURE_NAMES = [
    "html_password_fields",
    "html_form_count",
    "html_iframe_count",
    "html_external_scripts",
    "html_external_form_actions",
]


def extract_html_features(html: str, page_url: str) -> dict:
    if not isinstance(html, str) or not html.strip():
        raise ValueError("HTML content is empty or invalid")

    if not isinstance(page_url, str) or not page_url.strip():
        raise ValueError("Page URL is empty or invalid")

    soup = BeautifulSoup(html, "html.parser")
    page_host = (urlsplit(page_url).hostname or "").lower()

    password_fields = soup.find_all(
        "input", attrs={"type": "password"}
    )
    forms = soup.find_all("form")
    iframes = soup.find_all("iframe")

    external_scripts = 0
    for script in soup.find_all("script", src=True):
        script_url = urljoin(page_url, script.get("src", ""))
        script_host = (urlsplit(script_url).hostname or "").lower()
        if script_host and script_host != page_host:
            external_scripts += 1

    external_form_actions = 0
    for form in forms:
        action = form.get("action", "")
        if not action:
            continue

        action_url = urljoin(page_url, action)
        action_host = (urlsplit(action_url).hostname or "").lower()
        if action_host and action_host != page_host:
            external_form_actions += 1

    return {
        "html_password_fields": len(password_fields),
        "html_form_count": len(forms),
        "html_iframe_count": len(iframes),
        "html_external_scripts": external_scripts,
        "html_external_form_actions": external_form_actions,
    }

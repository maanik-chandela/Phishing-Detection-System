from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit


def extract_html_features(
    html: str,
    page_url: str,
    redirect_count: int = 0
) -> dict:

    soup = BeautifulSoup(html, "lxml")

    password_fields = soup.find_all(
        "input",
        attrs={"type": "password"}
    )

    forms = soup.find_all("form")

    scripts = soup.find_all(
        "script",
        src=True
    )

    iframes = soup.find_all("iframe")

    page_hostname = (
        urlsplit(page_url).hostname or ""
    ).lower()

    external_scripts = 0

    for script in scripts:

        script_url = urljoin(
            page_url,
            script.get("src", "")
        )

        script_hostname = (
            urlsplit(script_url).hostname or ""
        ).lower()

        if (
            script_hostname
            and script_hostname != page_hostname
        ):
            external_scripts += 1

    return {
        "password_field_count": len(password_fields),

        "form_count": len(forms),

        "external_script_count": external_scripts,

        "iframe_count": len(iframes),

        "redirect_count": redirect_count,
    }
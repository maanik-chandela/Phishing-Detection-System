def fetch_static_html(url: str) -> dict:
    """
    Safely fetch static HTML.

    Returns:
        {
            "html": str | None,
            "final_url": str | None,
            "redirect_count": int,
            "status_code": int | None,
            "fetch_status": str
        }
    """
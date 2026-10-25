from urllib.parse import urlsplit, parse_qsl
import ipaddress
import tldextract


SUSPICIOUS_KEYWORDS = [
    "login",
    "verify",
    "update",
    "secure",
    "account",
    "password",
    "banking",
    "confirm",
    "signin",
    "reset",
]


def extract_url_features(url: str) -> dict:

    parsed = urlsplit(url)

    hostname = parsed.hostname or ""

    extracted = tldextract.extract(hostname)

    subdomain = extracted.subdomain

    try:
        ipaddress.ip_address(hostname)
        has_ip = 1
    except ValueError:
        has_ip = 0

    keyword_count = sum(
        keyword in url.lower()
        for keyword in SUSPICIOUS_KEYWORDS
    )

    features = {
        "url_length": len(url),

        "hostname_length": len(hostname),

        "subdomain_count": (
            len(subdomain.split("."))
            if subdomain
            else 0
        ),

        "has_ip_address": has_ip,

        "uses_https": int(
            parsed.scheme.lower() == "https"
        ),

        "dot_count": url.count("."),

        "hyphen_count": url.count("-"),

        "at_count": url.count("@"),

        "digit_count": sum(
            char.isdigit()
            for char in url
        ),

        "suspicious_keyword_count": keyword_count,

        "path_length": len(parsed.path),

        "query_parameter_count": len(
            parse_qsl(parsed.query)
        ),
    }

    return features

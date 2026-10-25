from urllib.parse import urlsplit, parse_qsl
from ipaddress import ip_address
from math import log2
from collections import Counter
import re

import tldextract


FEATURE_NAMES = [
    "url_length",
    "domain_length",
    "url_contains_ip",
    "uses_https",
    "no_of_dots",
    "no_of_hyphen",
    "no_of_at",
    "special_characters_count",
    "num_query_params",
    "no_of_slashes_inpath",
    "hostname_digit_ratio",
    "has_punycode",
    "has_explicit_port",
    "url_entropy",
    "numeric_proportion",
]


def extract_url_features(url: str) -> dict:

    url = url.strip()

    parsed = urlsplit(url)

    if parsed.scheme.lower() not in ("http", "https"):
        raise ValueError("Only HTTP and HTTPS URLs are supported")

    hostname = parsed.hostname

    if not hostname:
        raise ValueError("URL must contain a hostname")

    hostname = hostname.lower()

    try:
        ip_address(hostname)
        contains_ip = 1
    except ValueError:
        contains_ip = 0

    digit_count = sum(char.isdigit() for char in url)

    hostname_digits = sum(
        char.isdigit() for char in hostname
    )

    counts = Counter(url)

    entropy = -sum(
        (count / len(url)) * log2(count / len(url))
        for count in counts.values()
    )

    try:
        explicit_port = int(parsed.port is not None)
    except ValueError:
        raise ValueError("Invalid URL port")

    special_chars = re.findall(
        r"[^a-zA-Z0-9]",
        url
    )

    return {
        "url_length": len(url),
        "domain_length": len(hostname),
        "url_contains_ip": contains_ip,
        "uses_https": int(parsed.scheme.lower() == "https"),
        "no_of_dots": url.count("."),
        "no_of_hyphen": url.count("-"),
        "no_of_at": url.count("@"),
        "special_characters_count": len(special_chars),
        "num_query_params": len(
            parse_qsl(parsed.query, keep_blank_values=True)
        ),
        "no_of_slashes_inpath": parsed.path.count("/"),
        "hostname_digit_ratio": (
            hostname_digits / len(hostname)
        ),
        "has_punycode": int("xn--" in hostname),
        "has_explicit_port": explicit_port,
        "url_entropy": entropy,
        "numeric_proportion": digit_count / len(url),
    }
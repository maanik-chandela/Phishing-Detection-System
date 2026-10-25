import whois
from datetime import datetime, timezone
from urllib.parse import urlsplit


def extract_domain_features(url: str) -> dict:

    hostname = urlsplit(url).hostname

    features = {
        "domain_age_days": None,
        "registration_info_available": 0,
        "expiry_info_available": 0,
    }

    if not hostname:
        return features

    try:
        domain_info = whois.whois(hostname)

        creation_date = domain_info.creation_date

        expiry_date = domain_info.expiration_date

        if isinstance(creation_date, list):
            creation_date = creation_date[0]

        if isinstance(expiry_date, list):
            expiry_date = expiry_date[0]

        if creation_date:
            if creation_date.tzinfo is None:
                creation_date = creation_date.replace(
                    tzinfo=timezone.utc
                )

            age = (
                datetime.now(timezone.utc)
                - creation_date
            ).days

            if age >= 0:
                features["domain_age_days"] = age
                features["registration_info_available"] = 1

        if expiry_date:
            features["expiry_info_available"] = 1

    except Exception:
        pass

    return features
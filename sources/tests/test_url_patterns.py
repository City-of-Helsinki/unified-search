from collections import namedtuple

from django.urls import get_resolver

NamePattern = namedtuple("NamePattern", ["name", "pattern"])


def test_url_patterns():
    """
    Ensure that the available URL patterns are as expected.
    """
    url_patterns = sorted(
        NamePattern(x.name, str(x.pattern)) for x in get_resolver().url_patterns
    )
    # NOTE: If you add new URL patterns,
    #       please recheck that CORS & CSP settings are appropriate,
    #       and update the openapi.yaml documentation.
    expected_url_patterns = [
        NamePattern("healthz", "healthz"),
        NamePattern("readiness", "readiness"),
    ]
    assert url_patterns == expected_url_patterns

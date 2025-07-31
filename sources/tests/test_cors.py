import pytest
from django.conf import settings


def test_cors_get_method_headers(client):
    """
    Test that the CORS headers are set correctly for GET requests.
    """
    response = client.get("/readiness", HTTP_ORIGIN="https://example.com")
    headers = response.headers

    assert headers.get("Access-Control-Allow-Origin") == "*"
    assert "Access-Control-Allow-Credentials" not in headers
    assert headers.get("Vary") == "origin"
    assert "Access-Control-Allow-Methods" not in headers


def test_cors_options_method_headers(client):
    """
    Test that the CORS headers are set correctly for OPTIONS requests.
    """
    response = client.options("/readiness", HTTP_ORIGIN="https://example.com")
    headers = response.headers

    assert headers.get("Access-Control-Allow-Origin") == "*"
    assert "Access-Control-Allow-Credentials" not in headers
    assert headers.get("Vary") == "origin"
    allowed_methods = sorted(
        method.strip() for method in headers["Access-Control-Allow-Methods"].split(",")
    )
    assert allowed_methods == ["GET", "HEAD"]


@pytest.mark.parametrize(
    "setting_name",
    [
        "CORS_ALLOW_HEADERS",
        "CORS_ALLOW_PRIVATE_NETWORK",
        "CORS_ALLOWED_ORIGIN_REGEXES",
        "CORS_ALLOWED_ORIGINS",
        "CORS_EXPOSE_HEADERS",
        "CORS_PREFLIGHT_MAX_AGE",
        "CORS_URLS_REGEX",
    ],
)
def test_unused_cors_settings(setting_name):
    """
    Test that unused CORS settings are not set in the Django settings.

    @see https://github.com/adamchainz/django-cors-headers/tree/4.7.0?tab=readme-ov-file#configuration
    """
    setting_value = getattr(settings, setting_name, None)
    assert setting_value is None


@pytest.mark.parametrize(
    "setting_name, expected_setting_value",
    [
        ("CORS_ALLOW_ALL_ORIGINS", True),
        ("CORS_ALLOW_CREDENTIALS", False),
        ("CORS_ALLOW_METHODS", ["GET", "HEAD"]),
    ],
)
def test_used_cors_settings(setting_name, expected_setting_value):
    """
    Test that used CORS settings are as set as expected in the Django settings.

    @see https://github.com/adamchainz/django-cors-headers/tree/4.7.0?tab=readme-ov-file#configuration
    """
    setting_value = getattr(settings, setting_name, None)
    assert setting_value == expected_setting_value

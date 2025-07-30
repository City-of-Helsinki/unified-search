import pytest
from django.test import Client


@pytest.fixture
def client():
    """Pytest fixture to provide a Django test client."""
    return Client()


def test_csp_header_present(client):
    """Test that the Content-Security-Policy header is present."""
    response = client.get("/")
    assert "Content-Security-Policy" in response.headers


def test_csp_header_content(client):
    """Test that the CSP header has the expected directives."""
    response = client.get("/")
    csp_header = response.headers["Content-Security-Policy"]
    expected_none_directives = [
        "base-uri",
        "child-src",
        "connect-src",
        "default-src",
        "font-src",
        "form-action",
        "frame-ancestors",
        "frame-src",
        "img-src",
        "manifest-src",
        "media-src",
        "navigate-to",
        "object-src",
        "script-src",
        "style-src",
        "worker-src",
    ]
    sorted_csp_parts = sorted(dir.strip() for dir in csp_header.split(";"))
    expected_sorted_csp_parts = sorted(
        [f"{directive} 'none'" for directive in expected_none_directives]
    )
    # Compare sorted CSP directives because their order can vary
    assert sorted_csp_parts == expected_sorted_csp_parts

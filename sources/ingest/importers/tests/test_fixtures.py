import pytest
import requests
from django.conf import settings

EXPECTED_BLOCKED_URLS = [
    "https://127.0.0.1:1234/a/test/path/",
    "https://example.org/",
]


def test_allow_only_real_elasticsearch_requests_is_autoused(request):
    """
    Test that allow_only_real_elasticsearch_requests fixture is auto-used.
    """
    assert "allow_only_real_elasticsearch_requests" in request.fixturenames


def test_allow_only_real_elasticsearch_requests_success():
    """
    Test that real Elasticsearch requests are allowed and are successful.
    """
    response = requests.get(settings.ES_URI)
    assert response.status_code == 200


@pytest.mark.parametrize("method_name", ["get", "post"])
def test_allow_only_real_elasticsearch_requests_failure(method_name):
    """
    Test that requests to non-Elasticsearch URLs raise AssertionError.
    """
    # Intentionally failing fast on the first URL to make making a real request to
    # non-local address less likely.
    for url in EXPECTED_BLOCKED_URLS:
        with pytest.raises(AssertionError) as exc_info:
            getattr(requests, method_name)(url)
        assert str(exc_info.value) == (
            f"Unmocked {method_name.upper()} request to: {url}\n"
            + "Add a fixture to mock this endpoint."
        )

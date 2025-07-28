from unittest.mock import patch

from django.test import Client
from django.urls import reverse
from health_check.exceptions import ServiceUnavailable


@patch("custom_health_checks.backends.DatabaseHealthCheck.check_status")
def test_healthz_success(mock_check_status, client: Client):  # Use the 'client' fixture
    """
    Test /healthz endpoint with successful health checks.
    """
    mock_check_status.return_value = None  # Simulate successful check
    url = reverse("healthz")
    response = client.get(url)
    assert response.status_code == 200
    assert response.content == b'{"DatabaseHealthCheck": "working"}'


@patch("custom_health_checks.backends.DatabaseHealthCheck.check_status")
def test_healthz_database_error(mock_check_status, client: Client):
    """
    Test /healthz endpoint with a database error.
    """
    mock_check_status.side_effect = ServiceUnavailable("Database error")
    url = reverse("healthz")
    response = client.get(url)
    assert response.status_code == 500
    assert b"Database error" in response.content

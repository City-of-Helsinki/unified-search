import logging

import requests

from ingest.importers.utils.retry import retry_twice_5s_intervals

logger = logging.getLogger(__name__)


def request_json(url, timeout_seconds=20):
    """
    Request a JSON response from the given URL
    with the given timeout and max. 2 retries.

    :return: JSON response from the URL if successful,
             otherwise raises an exception.
    :raise: Exception if the request fails after retries.
    """
    logger.debug(f"Requesting URL {url}")

    def fetch_response():
        response = requests.get(url, timeout=timeout_seconds)
        response.raise_for_status()
        return response

    try:
        response = retry_twice_5s_intervals(fetch_response)
        return response.json()
    except Exception as e:
        logger.error(f"Error while requesting {url}: {e}")
        raise

import logging

import requests

logger = logging.getLogger(__name__)


def request_json(url, timeout_seconds=20):
    logger.debug(f"Requesting URL {url}")
    result = None
    try:
        r = requests.get(url, timeout=timeout_seconds)
        r.raise_for_status()
        result = r.json()
    except Exception as e:
        logger.error(f"Error while requesting {url}: {e}")
        raise
    return result

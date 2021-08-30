import logging

import requests

logger = logging.getLogger(__name__)


def request_json(url):
    logger.debug(f"Requesting URL {url}")
    result = None
    try:
        r = requests.get(url)
        r.raise_for_status()
        result = r.json()
    except Exception as e:
        logger.error(f"Error while requesting {url}: {e}")
        raise
    return result

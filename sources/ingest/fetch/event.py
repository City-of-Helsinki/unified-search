import json
import requests
import logging
from django.conf import settings

from elasticsearch import Elasticsearch


logger = logging.getLogger(__name__)


ES_INDEX = "event"


def fetch():
    url = "https://api.hel.fi/linkedevents/v1/event/"

    payload = {"page_size": 100}
    received_count = 0
    try:
        es = Elasticsearch([settings.ES_URI])
    except ConnectionError as e:
        return "ERROR at {}".format(__name__)

    logger.debug(f"Creating index {ES_INDEX}")

    while url:
        r = requests.get(url, params=payload)
        data = r.json()
        item_count = len(data["data"])
        received_count = received_count + item_count

        for entry in data["data"]:
            entry["origin"] = ES_INDEX
            r = es.index(index=ES_INDEX, doc_type="_doc", body=entry)

        url = data["meta"]["next"]

    logger.info("Received {} items".format(received_count))
    return "Fetch completed by {}".format(__name__)

def delete():
    """ Delete the whole index. """
    try:
        es = Elasticsearch([settings.ES_URI])
        r = es.indices.delete(index=ES_INDEX)
        logger.debug(r)
    except Exception as e:
        return "ERROR at {}".format(__name__)


def set_alias(alias):
    """ Configure alias for index name. """
    try:
        es = Elasticsearch([settings.ES_URI])
        es.indices.put_alias(index=ES_INDEX, name=alias)
    except ConnectionError as e:
        return "ERROR at {}".format(__name__)

import logging
import requests
import json
import time

from elasticsearch import exceptions
from elasticsearch import Elasticsearch


""" Running:
        pytest

    or with full log output:
        pytest --log-cli-level=debug
"""

logging.basicConfig(
    filename="test_es_health.log",
    format="%(filename)s: %(message)s",
    level=logging.DEBUG,
)


def test_es_up():
    logging.debug("Checking ElasticSearch connection")
    r = requests.get("http://localhost:9200")
    logging.debug(json.dumps(json.loads(r.content), indent=4))
    assert r.status_code == 200


def test_es_search():
    """ Search after running management command to fill ES from data sources. """

    es = Elasticsearch([{"host": "localhost", "port": 9200}])

    query = {"query": {"match": {"fi": {"query": "kivist", "fuzziness": "AUTO"}}}}

    s = es.search(index="test-index", body=query)

    hits = s["hits"]["total"]["value"]
    assert hits == 1

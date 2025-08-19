import json
import logging

import requests
from django.conf import settings
from opensearchpy import exceptions, OpenSearch

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
    logging.debug("Checking OpenSearch connection")
    r = requests.get(settings.ES_URI)
    logging.debug(json.dumps(json.loads(r.content), indent=4))
    assert r.status_code == 200


def test_es_basic_operations():
    """Run basic operations for testing purposes."""

    es = OpenSearch([settings.ES_URI])

    try:
        logging.debug("Deleting existing test data")
        es.delete(index="unit-test-index", id=1)
    except exceptions.NotFoundError:
        pass

    logging.debug("Adding test data")
    r = es.index(
        index="unit-test-index",
        id=1,
        body={
            "name": "Koira Koiruli Pöö",
            "height": "49",
            "mass": "10",
            "hair_color": "blond",
            "birth_year": "1999",
            "gender": "male",
        },
    )

    assert r["result"] == "created"

    es.indices.refresh(index="unit-test-index")
    r = es.get(index="unit-test-index", id=1)
    assert r["_id"] == "1"

    s = es.search(index="unit-test-index", body={"query": {"match": {"name": "cat"}}})
    hits = s["hits"]["total"]["value"]
    assert hits == 0

    s = es.search(index="unit-test-index", body={"query": {"match_all": {}}})
    logging.debug(s)
    hits = s["hits"]["total"]["value"]
    assert hits == 1

    s = es.search(index="unit-test-index", body={"query": {"match": {"mass": "10"}}})
    logging.debug(s)
    hits = s["hits"]["total"]["value"]
    assert hits == 1

    s = es.search(
        index="unit-test-index", body={"query": {"match": {"name": "Koiruli"}}}
    )
    logging.debug(s)
    hits = s["hits"]["total"]["value"]
    assert hits == 1

    logging.debug("Deleting test data")
    es.delete(index="unit-test-index", id=1)

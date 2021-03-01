import requests

from elasticsearch import Elasticsearch


def fetch():
    URL = "https://api.hel.fi/servicemap/v2/unit/63871/"

    r = requests.get(URL)
    print(r.status_code)

    data = r.json()
    print(data["name"])

    print("Storing data to Elasticsearch")

    try:
        es = Elasticsearch([{"host": "es01", "port": 9200}])
    except ConnectionError as e:
        return "ERROR at {}".format(__name__)

    r = es.index(index="test-index", doc_type="test", body=data["name"])
    print(r)

    return "Fetch completed by {}".format(__name__)


def delete():
    """ Delete the whole index. """
    try:
        es = Elasticsearch([{"host": "es01", "port": 9200}])
    except ConnectionError as e:
        return "ERROR at {}".format(__name__)

    r = es.indices.delete(index="test-index")
    print(r)

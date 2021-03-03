import json
import requests

from elasticsearch import Elasticsearch


def fetch():
    URL = "https://api.hel.fi/servicemap/v2/unit/"

    try:
        es = Elasticsearch([{"host": "es01", "port": 9200}])
    except ConnectionError as e:
        return "ERROR at {}".format(__name__)

    print("Requesting data at {}".format(__name__))

    r = requests.get(URL)
    print(r.status_code)

    data = r.json()
    print("Received {} items".format(len(data["results"])))

    print("Storing data to Elasticsearch")

    for entry in data["results"]:
        #print(entry)
        r = es.index(index="test-index", doc_type="test", body=str(json.dumps(entry)))
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

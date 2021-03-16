import json
import requests

from elasticsearch import Elasticsearch


def fetch():
    url = "https://api.hel.fi/linkedevents/v1/event/"
    MAX_COUNT = 2000
    payload = {"page_size": 100}
    received_count = 0
    try:
        es = Elasticsearch([{"host": "es01", "port": 9200}])
    except ConnectionError as e:
        return "ERROR at {}".format(__name__)

    print("Requesting data at {}".format(__name__))

    while url and received_count < MAX_COUNT:
        r = requests.get(url, params=payload)
        data = r.json()
        item_count = len(data["data"])
        received_count = received_count + item_count
        print(".", end="")

        for entry in data["data"]:
            r = es.index(index="linkedevents", doc_type="_doc", body=str(json.dumps(entry)))

        url = data["meta"]["next"]

    print(".")
    print("Received {} items".format(received_count))
    return "Fetch completed by {}".format(__name__)

def delete():
    """ Delete the whole index. """
    try:
        es = Elasticsearch([{"host": "es01", "port": 9200}])
    except ConnectionError as e:
        return "ERROR at {}".format(__name__)

    r = es.indices.delete(index="linkedevents")
    print(r)

def set_alias(alias):
    """ Configure alias for index name. """
    try:
        es = Elasticsearch([{"host": "es01", "port": 9200}])
        es.indices.put_alias(index='linkedevents', name=alias)
    except ConnectionError as e:
        return "ERROR at {}".format(__name__)

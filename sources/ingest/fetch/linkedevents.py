import json
import requests
from django.conf import settings

from elasticsearch import Elasticsearch


def fetch():
    url = "https://api.hel.fi/linkedevents/v1/place/"
    MAX_COUNT = 2000
    payload = {"page_size": 100}
    received_count = 0
    try:
        es = Elasticsearch([settings.ES_URI])
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
            entry["origin"] = "linkedevents"
            r = es.index(index="linkedevents", doc_type="_doc", body=str(json.dumps(entry)))

        url = data["meta"]["next"]

    print(".")
    print("Received {} items".format(received_count))
    return "Fetch completed by {}".format(__name__)

def delete():
    """ Delete the whole index. """
    try:
        es = Elasticsearch([settings.ES_URI])
        r = es.indices.delete(index="linkedevents")
        print(r)
    except Exception as e:
        return "ERROR at {}".format(__name__)


def set_alias(alias):
    """ Configure alias for index name. """
    try:
        es = Elasticsearch([settings.ES_URI])
        es.indices.put_alias(index='linkedevents', name=alias)
    except ConnectionError as e:
        return "ERROR at {}".format(__name__)

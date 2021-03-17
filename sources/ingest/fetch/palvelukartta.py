import json
import requests

from elasticsearch import Elasticsearch


def fetch():
    url = "https://www.hel.fi/palvelukarttaws/rest/v4/unit/"

    try:
        es = Elasticsearch([{"host": "es01", "port": 9200}])
    except ConnectionError as e:
        return "ERROR at {}".format(__name__)

    print("Requesting data at {}".format(__name__))

    r = requests.get(url)
    data = r.json()

    for entry in data:
        r = es.index(index="palvelukartta", doc_type="_doc", body=str(json.dumps(entry)))

    return "Fetch completed by {}".format(__name__)

def delete():
    """ Delete the whole index. """
    try:
        es = Elasticsearch([{"host": "es01", "port": 9200}])
    except ConnectionError as e:
        return "ERROR at {}".format(__name__)

    r = es.indices.delete(index="palvelukartta")
    print(r)

def set_alias(alias):
    """ Configure alias for index name. """
    try:
        es = Elasticsearch([{"host": "es01", "port": 9200}])
        es.indices.put_alias(index='palvelukartta', name=alias)
    except ConnectionError as e:
        return "ERROR at {}".format(__name__)

import json
import requests

from elasticsearch import Elasticsearch


def get_ontologyword_ids(id_list):
    info = []

    for _id in id_list:
        url = f"https://www.hel.fi/palvelukarttaws/rest/v4/ontologyword/{_id}/"
        r = requests.get(url)
        info.append(r.json())

    return info


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
        entry["origin"] = "palvelukartta"
        if "ontologyword_ids" in entry and entry['ontologyword_ids']:
            # Enrich data from another API
            entry['ontologyword_ids_enriched'] = get_ontologyword_ids(entry['ontologyword_ids'])

        r = es.index(index="palvelukartta", doc_type="_doc", body=str(json.dumps(entry)))

    return "Fetch completed by {}".format(__name__)

def delete():
    """ Delete the whole index. """
    try:
        es = Elasticsearch([{"host": "es01", "port": 9200}])
        r = es.indices.delete(index="palvelukartta")
        print(r)
    except Exception as e:
        return "ERROR at {}".format(__name__)


def set_alias(alias):
    """ Configure alias for index name. """
    try:
        es = Elasticsearch([{"host": "es01", "port": 9200}])
        es.indices.put_alias(index='palvelukartta', name=alias)
    except ConnectionError as e:
        return "ERROR at {}".format(__name__)

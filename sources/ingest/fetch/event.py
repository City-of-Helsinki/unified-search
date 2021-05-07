import requests
import logging
from dataclasses import dataclass, field, asdict
from typing import List
from django.conf import settings
from datetime import datetime

from elasticsearch import Elasticsearch


logger = logging.getLogger(__name__)


ES_INDEX = "event"


@dataclass
class NodeMeta:
    id: str
    createdAt: datetime
    updatedAt: datetime=None

@dataclass
class LanguageString:
    fi: str
    sv: str
    en: str

@dataclass
class Event:
    meta: NodeMeta = None
    name: LanguageString = None

@dataclass
class Root:
    event: Event

    # TODO: by adding links the whole data can be indexed
    #links: List[LinkedData] = field(default_factory=list)
    #suggest: List[str] = field(default_factory=list)


def create_language_string(d):
    if not d:
        return None
    return LanguageString(
        fi=d.get(f"fi", None),
        sv=d.get(f"sv", None),
        en=d.get(f"en", None)
        )

def fetch():
    url = settings.EVENT_URL

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

            # ID's must be strings to avoid collisions
            entry["id"] = _id = str(entry["id"])

            meta = NodeMeta(id=_id, createdAt=datetime.now())

            event = Event(
                meta=meta,
                name=create_language_string(entry["name"])
            )

            root = Root(event=event)

            r = es.index(index=ES_INDEX, doc_type="_doc", body=asdict(root))

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

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

import requests
from django.conf import settings

from .base import Importer
from .utils.keyword import Keyword
from .utils.language import LanguageStringConverter
from .utils.shared import LanguageString

logger = logging.getLogger(__name__)


@dataclass
class NodeMeta:
    id: str
    createdAt: datetime
    updatedAt: datetime = None


@dataclass
class Event:
    meta: NodeMeta = None
    name: LanguageString = None
    description: LanguageString = None


@dataclass
class LinkedData:
    service: str = None
    origin_url: str = None
    raw_data: Dict = None


OntologyType = Dict[str, Dict[str, List[str]]]


@dataclass
class Root:
    event: Event
    ontology: OntologyType = None
    links: List[LinkedData] = field(default_factory=list)


class EventImporter(Importer[Root]):
    index_base_names = ("event",)

    def run(self):
        url = settings.EVENT_URL
        received_count = 0
        keyword = Keyword()

        while url:
            logger.debug(f"Requesting URL {url}")
            r = requests.get(url)
            data = r.json()
            item_count = len(data["data"])
            received_count = received_count + item_count

            for entry in data["data"]:
                entry["origin"] = self.index_base_names[0]

                # ID's must be strings to avoid collisions
                entry["id"] = _id = str(entry["id"])

                meta = NodeMeta(id=_id, createdAt=datetime.now())

                l = LanguageStringConverter(entry, self.use_fallback_languages)

                entry["keywords_enriched"] = keyword.enrich(entry["keywords"])

                event = Event(
                    meta=meta,
                    name=l.get_language_string("name"),
                    description=l.get_language_string("description"),
                )

                root = Root(event=event)

                root.ontology = keyword.grouped_by_lang(entry["keywords"])

                event_data = LinkedData(
                    service="linkedevents", origin_url=f"{url}{_id}/", raw_data=entry
                )

                root.links.append(event_data)

                self.add_data(root)

            url = data["meta"]["next"]

        logger.info("Received {} items".format(received_count))

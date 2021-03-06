from __future__ import annotations

import base64
import functools
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import List, Optional

import requests
from django.conf import settings
from elasticsearch import Elasticsearch, NotFoundError

from .language import LanguageStringConverter
from .ontology import Ontology
from .shared import LanguageString
from .traffic import request_json

logger = logging.getLogger(__name__)

ES_INDEX = "location"
ES_ADMINISTRATIVE_DIVISION_INDEX = "administrative_division"


@dataclass
class NodeMeta:
    id: str
    createdAt: datetime
    updatedAt: datetime = None


@dataclass
class LinkedData:
    service: str = None
    origin_url: str = None
    raw_data: dict = None


@dataclass
class Address:
    postalCode: str
    streetAddress: LanguageString
    city: LanguageString


@dataclass
class GeoJSONFeature:
    geometry: GeoJSONGeometry


@dataclass
class GeoJSONGeometry:
    coordinates: Coordinates


@dataclass
class Coordinates:
    latitude: float
    longitude: float
    northing_etrs_gk25: int
    easting_etrs_gk25: int
    northing_etrs_tm35fin: int
    easting_etrs_tm35fin: int
    manual_coordinates: bool


@dataclass
class Location:
    url: LanguageString
    address: Address = None
    geoLocation: GeoJSONFeature = None
    administrativeDivisions: List[AdministrativeDivision] = field(default_factory=list)


@dataclass
class OpeningHours:
    url: str
    is_open_now_url: str
    hourLines: List[LanguageString] = field(default_factory=list)


@dataclass
class OntologyObject:
    id: str
    label: LanguageString


@dataclass
class Image:
    url: str
    caption: LanguageString


@dataclass
class AdministrativeDivision:
    id: str
    type: str
    municipality: Optional[str]
    name: LanguageString


@dataclass
class Venue:
    meta: NodeMeta = None
    name: LanguageString = None
    location: Location = None
    description: LanguageString = None

    # TODO
    descriptionResources: str = None
    # annotations imported for this
    partOf: Venue = None
    openingHours: OpeningHours = None
    manager: str = None
    reservationPolicy: str = None
    accessibilityProfile: str = None
    arrivalInstructions: str = None
    additionalInfo: str = None
    facilities: str = None
    images: List[Image] = field(default_factory=list)


@dataclass
class Root:
    venue: Venue
    links: List[LinkedData] = field(default_factory=list)
    suggest: List[str] = field(default_factory=list)


def get_tpr_units():
    url = "https://www.hel.fi/palvelukarttaws/rest/v4/unit/"
    data = request_json(url)
    return data


def get_linkedevents_place(id):
    url = f"https://api.hel.fi/linkedevents/v1/place/tprek:{id}/"
    data = request_json(url)

    # Extra information to raw data
    data["origin"] = "linkedevents"

    return url, data


def get_opening_hours(d):
    results = []
    if "connections" in d and d["connections"]:
        for section in d["connections"]:
            if section["section_type"] == "OPENING_HOURS":
                results.append(section)
    return results


def prefix_and_mask(prefix, body):
    message = f"{prefix}-{body}"
    message_bytes = message.encode("utf-8")
    base64_bytes = base64.b64encode(message_bytes)

    return base64_bytes.decode("utf-8")


def get_ontologywords_as_ontologies(ontologywords):
    ontologies = []

    for ontologyword in ontologywords:
        l = LanguageStringConverter(ontologyword)

        ontologies.append(
            OntologyObject(
                id=str(ontologyword.get("id")),
                label=l.get_language_string("ontologyword"),
            )
        )

        if (
            "extra_searchwords_fi" in ontologyword
            or "extra_searchwords_sv" in ontologyword
            or "extra_searchwords_en" in ontologyword
        ):
            ontologies.append(
                OntologyObject(
                    # A unique id is not available in the source data. To make the id
                    # more opaque we are encoding it.
                    id=prefix_and_mask("es-", ontologyword.get("id")),
                    label=l.get_language_string("extra_searchwords"),
                )
            )

    return ontologies


def get_ontologytree_as_ontologies(ontologytree):
    ontologies = []

    for ontologybranch in ontologytree:
        l = LanguageStringConverter(ontologybranch)

        ontologies.append(
            OntologyObject(
                id=str(ontologybranch.get("id")), label=l.get_language_string("name")
            )
        )

        if (
            "extra_searchwords_fi" in ontologybranch
            or "extra_searchwords_sv" in ontologybranch
            or "extra_searchwords_en" in ontologybranch
        ):
            ontologies.append(
                OntologyObject(
                    # A unique id is not available in the source data. To make the id
                    # more opaque we are encoding it.
                    id=prefix_and_mask("es-", ontologybranch.get("id")),
                    label=l.get_language_string("extra_searchwords"),
                )
            )

    return ontologies


def get_suggestions_from_ontologies(ontologies: List[OntologyObject]):
    ontologies_grouped_by_language = functools.reduce(
        lambda acc, ontology: {
            "fi": acc.get("fi") + [ontology.label.fi],
            "sv": acc.get("sv") + [ontology.label.sv],
            "en": acc.get("en") + [ontology.label.en],
        },
        ontologies,
        {"fi": [], "sv": [], "en": []},
    )

    # Suggestions are stored in shorthand syntax. If you want to add more
    # specific context or weight, you have to store suggestions on a per
    # suggestion basis (example):
    # [
    #     {
    #         "input": "beach",
    #         "weight": 2,
    #         "contexts": {
    #             "language": "en",
    #             "unit": "liikunta"
    #         }
    #     },
    #     {
    #         "input": "social services",
    #         "weight": 2,
    #         "contexts": {
    #             "language": "en",
    #             "unit": "social work"
    #         }
    #     },
    # ]
    suggest = []
    for [language, suggestions_in_language] in ontologies_grouped_by_language.items():
        suggestions_without_empty = list(
            filter(lambda suggestion: type(suggestion) == str, suggestions_in_language)
        )

        suggest.append(
            {"input": suggestions_without_empty, "contexts": {"language": language}}
        )

    return suggest


def define_language_properties():
    languages = [("fi", "finnish"), ("sv", "swedish"), ("en", "english")]
    language_properties = {}

    for [language, analyzer] in languages:
        language_properties[language] = {
            "type": "text",
            "analyzer": analyzer,
            "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
        }

    return language_properties


custom_mappings = {
    "properties": {
        "suggest": {
            "type": "completion",
            "contexts": [
                {
                    "name": "language",
                    "type": "category",
                }
            ],
        },
        "venue": {
            "properties": {
                "name": {"properties": define_language_properties()},
                "description": {"properties": define_language_properties()},
            }
        },
    }
}


def fetch():  # noqa C901 this function could use some refactoring
    try:
        es = Elasticsearch([settings.ES_URI])
    except ConnectionError as e:
        return f"ERROR at {__name__}: {e}"

    logger.debug(f"Creating index {ES_INDEX}")

    try:
        es.indices.create(index=ES_INDEX)
    # TODO
    except BaseException:
        logger.debug("Index location already exists, skipping")

    logger.debug("Applying custom mapping")

    es.indices.put_mapping(index=ES_INDEX, body=custom_mappings)

    logger.debug("Custom mapping set")

    logger.debug("Requesting data at {}".format(__name__))

    ontology = Ontology()

    tpr_units = get_tpr_units()

    count = 0
    for tpr_unit in tpr_units:
        l = LanguageStringConverter(tpr_unit)
        e = lambda k: tpr_unit.get(k, None)  # noqa: E731

        # ID's must be strings to avoid collisions
        tpr_unit["id"] = _id = str(tpr_unit["id"])

        meta = NodeMeta(id=_id, createdAt=datetime.now())

        location = Location(
            url=l.get_language_string("www"),
            address=Address(
                postalCode=e("address_zip"),
                streetAddress=l.get_language_string("street_address"),
                city=l.get_language_string("address_city"),
            ),
            geoLocation=GeoJSONFeature(
                geometry=GeoJSONGeometry(
                    coordinates=Coordinates(
                        latitude=e("latitude"),
                        longitude=e("longitude"),
                        northing_etrs_gk25=e("northing_etrs_gk25"),
                        easting_etrs_gk25=e("easting_etrs_gk25"),
                        northing_etrs_tm35fin=e("northing_etrs_tm35fin"),
                        easting_etrs_tm35fin=e("easting_etrs_tm35fin"),
                        manual_coordinates=e("manual_coordinates"),
                    )
                )
            ),
        )

        opening_hours = OpeningHours(
            url=f"https://hauki.api.hel.fi/v1/resource/tprek:{_id}/opening_hours/",
            is_open_now_url=f"https://hauki.api.hel.fi/v1/resource/tprek:{_id}/is_open_now/",
        )

        # Assuming single image
        images = []
        images.append(
            Image(
                url=e("picture_url"), caption=l.get_language_string("picture_caption")
            )
        )

        venue = Venue(
            name=l.get_language_string("name"),
            description=l.get_language_string("desc"),
            location=location,
            meta=meta,
            openingHours=opening_hours,
            images=images,
        )
        root = Root(venue=venue)

        try:
            place_url, place = get_linkedevents_place(_id)

            place_link = LinkedData(
                service="linkedevents", origin_url=place_url, raw_data=place
            )
            venue.location.administrativeDivisions = [
                AdministrativeDivision(id=le_division.pop("ocd_id"), **le_division)
                for le_division in place["divisions"].copy()
            ]

            root.links.append(place_link)
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
        ) as exc:
            logger.warning(f"Error while fetching {place_url}: {exc}")

        # Extra information to raw data
        tpr_unit["origin"] = "tpr"

        # TODO: Separate words from tree
        # TODO: Remove duplicates
        #       Duplicates are not yet removed, because ontologies are not
        #       returned in a public facing data structure.
        all_ontologies = []
        # Ontology ID's and tree contain plain integers, get corresponding texts
        if tpr_unit.get("ontologyword_ids", None):
            word_ontologies = ontology.enrich_word_ids(tpr_unit["ontologyword_ids"])
            tpr_unit["ontologyword_ids_enriched"] = word_ontologies
            all_ontologies = all_ontologies + get_ontologywords_as_ontologies(
                word_ontologies
            )

        if tpr_unit.get("ontologytree_ids", None):
            tree_ontologies = ontology.enrich_tree_ids(tpr_unit["ontologytree_ids"])
            tpr_unit["ontologytree_ids_enriched"] = tree_ontologies
            all_ontologies = all_ontologies + get_ontologytree_as_ontologies(
                tree_ontologies
            )

        root.suggest = get_suggestions_from_ontologies(all_ontologies)

        link = LinkedData(
            service="tpr",
            origin_url=f"https://www.hel.fi/palvelukarttaws/rest/v4/unit/{_id}/",
            raw_data=tpr_unit,
        )
        root.links.append(link)

        es.index(index=ES_INDEX, doc_type="_doc", body=asdict(root))

        # all encountered administrative divisions are stored in their own index so
        # that they can be easily returned from the GQL API. We might want to change
        # this implementation in the future, maybe even use something else than ES.
        for division in venue.location.administrativeDivisions:
            es.index(
                index=ES_ADMINISTRATIVE_DIVISION_INDEX,
                body=asdict(division),
                id=division.id,
            )

        logger.debug(f"Fethed data count: {count}")
        count = count + 1

    logger.info(f"Fetched {count} items in total")
    return "Fetch completed by {}".format(__name__)


def delete():
    """Delete the whole index."""
    try:
        es = Elasticsearch([settings.ES_URI])
    except ConnectionError as e:
        logger.error(f"ERROR at {__name__}: {e}")
        return

    for index in (ES_ADMINISTRATIVE_DIVISION_INDEX, ES_INDEX):
        try:
            r = es.indices.delete(index=index)
            logger.debug(r)
        except NotFoundError as e:
            logger.debug(e)
        except ConnectionError as e:
            logger.error(f"ERROR at {__name__}: {e}")


def set_alias(alias):
    """Configure alias for index name."""
    try:
        es = Elasticsearch([settings.ES_URI])
        es.indices.put_alias(index=ES_INDEX, name=alias)
    except ConnectionError as e:
        return f"ERROR at {__name__}: {e}"

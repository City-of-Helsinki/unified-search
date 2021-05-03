from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List
from django.utils import timezone
from django.conf import settings

import logging
import base64
import functools
from datetime import datetime

from elasticsearch import Elasticsearch

from .traffic import request_json
from .ontology import Ontology


logger = logging.getLogger(__name__)


@dataclass
class NodeMeta:
    id: str
    createdAt: datetime
    updatedAt: datetime=None

@dataclass
class LinkedData:
    service: str = None
    origin_url: str = None
    raw_data: dict = None

@dataclass
class LanguageString:
    fi: str
    sv: str
    en: str

@dataclass
class Address:
    postal_code: str
    street_address: LanguageString
    city: LanguageString

@dataclass
class GeoJSONFeature:
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


def create_language_string(d, key_prefix):
    return LanguageString(
        fi=d.get(f"{key_prefix}_fi", None),
        sv=d.get(f"{key_prefix}_sv", None),
        en=d.get(f"{key_prefix}_en", None)
        )


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
        ontologies.append(
            OntologyObject(
                id=str(ontologyword.get("id")),
                label=create_language_string(ontologyword, "ontologyword")
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
                    label=create_language_string(ontologyword, "extra_searchwords")
                )
            )

    return ontologies


def get_ontologytree_as_ontologies(ontologytree):
    ontologies = []

    for ontologybranch in ontologytree:
        ontologies.append(
            OntologyObject(
                id=str(ontologybranch.get("id")),
                label=create_language_string(ontologybranch, "name")
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
                    label=create_language_string(ontologybranch, "extra_searchwords")
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


custom_mappings = {
    "properties": {
        "suggest": {    
            "type": "completion",
            "contexts": [
                {
                    "name": "language",
                    "type": "category",
                }
            ]
        }
    }
}

def fetch():
    try:
        es = Elasticsearch([settings.ES_URI])
    except ConnectionError as e:
        return "ERROR at {}".format(__name__)

    logger.debug("Creating index location")

    try:
        es.indices.create(index="location")
    except:
        logger.debug("Index location already exists, skipping")

    logger.debug("Applying custom mapping")

    es.indices.put_mapping(index="location", body=custom_mappings)

    logger.debug("Custom mapping set")

    logger.debug("Requesting data at {}".format(__name__))

    ontology = Ontology()

    tpr_units = get_tpr_units()

    count  = 0
    for tpr_unit in tpr_units:

        e = lambda k: tpr_unit.get(k, None)

        # ID's must be strings to avoid collisions
        tpr_unit["id"] = _id = str(tpr_unit["id"])

        meta = NodeMeta(id=_id, createdAt=datetime.now())
        
        location = Location(
            url=create_language_string(tpr_unit, "www"),
            address = Address(
                postal_code=e("address_zip"),
                street_address=create_language_string(tpr_unit, "street_address"),
                city=create_language_string(tpr_unit, "address_city")
                ),
            geoLocation=GeoJSONFeature(
                latitude=e("latitude"),
                longitude=e("longitude"),
                northing_etrs_gk25=e("northing_etrs_gk25"),
                easting_etrs_gk25 = e("easting_etrs_gk25"),
                northing_etrs_tm35fin = e("northing_etrs_tm35fin"),
                easting_etrs_tm35fin = e("easting_etrs_tm35fin"),
                manual_coordinates = e("manual_coordinates")
                ),
            )

        opening_hours = OpeningHours(
            url=f"http://hauki-test.oc.hel.ninja/v1/resource/tprek:{_id}/opening_hours/",
            is_open_now_url=f"http://hauki-test.oc.hel.ninja/v1/resource/tprek:{_id}/is_open_now/")

        venue = Venue(
            name=create_language_string(tpr_unit, "name"),
            description=create_language_string(tpr_unit, "desc"),
            location=location, 
            meta=meta, 
            openingHours=opening_hours)

        place_url, place = get_linkedevents_place(_id)

        place_link = LinkedData(
            service="linkedevents",
            origin_url=place_url,
            raw_data=place)

        root = Root(venue=venue)
        root.links.append(place_link)

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
            all_ontologies = all_ontologies + get_ontologywords_as_ontologies(word_ontologies)

        if tpr_unit.get("ontologytree_ids", None):
            tree_ontologies = ontology.enrich_tree_ids(tpr_unit["ontologytree_ids"])
            tpr_unit["ontologytree_ids_enriched"] = tree_ontologies
            all_ontologies = all_ontologies + get_ontologytree_as_ontologies(tree_ontologies)

        root.suggest = get_suggestions_from_ontologies(all_ontologies)

        link = LinkedData(
            service="tpr",
            origin_url=f"https://www.hel.fi/palvelukarttaws/rest/v4/unit/{_id}/", 
            raw_data=tpr_unit)
        root.links.append(link)

        r = es.index(index="location", doc_type="_doc", body=asdict(root))

        logger.debug(f"Fethed data count: {count}")
        count = count + 1

    logger.info(f"Fetched {count} items in total")
    return "Fetch completed by {}".format(__name__)


def delete():
    """ Delete the whole index. """
    try:
        es = Elasticsearch([settings.ES_URI])
        r = es.indices.delete(index="location")
        logger.debug(r)
    except Exception as e:
        return "ERROR at {}".format(__name__)


def set_alias(alias):
    """ Configure alias for index name. """
    try:
        es = Elasticsearch([settings.ES_URI])
        es.indices.put_alias(index='location', name=alias)
    except ConnectionError as e:
        return "ERROR at {}".format(__name__)

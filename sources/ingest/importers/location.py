from __future__ import annotations

import base64
import functools
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Union

from .base import Importer
from .utils import (
    AdministrativeDivision,
    AdministrativeDivisionFetcher,
    HaukiOpeningHoursFetcher,
    LanguageString,
    LanguageStringConverter,
    Ontology,
    OpeningHours,
    request_json,
)

logger = logging.getLogger(__name__)


@dataclass
class NodeMeta:
    id: str
    createdAt: datetime
    updatedAt: datetime = None


@dataclass
class LinkedData:
    service: str = None
    origin_url: str = None
    raw_data: Union[dict, list] = None


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
class OntologyObject:
    id: str
    label: LanguageString


@dataclass
class Image:
    url: str
    caption: LanguageString


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
    ontologyWords: List[OntologyObject] = field(default_factory=list)


@dataclass
class GeoPoint:
    latitude: float
    longitude: float


@dataclass
class Root:
    venue: Venue
    location: GeoPoint = None
    links: List[LinkedData] = field(default_factory=list)
    suggest: List[str] = field(default_factory=list)


def get_tpr_units():
    url = "https://www.hel.fi/palvelukarttaws/rest/v4/unit/"
    data = request_json(url)
    return data


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
                "openingHours": {
                    "properties": {
                        "openRanges": {
                            "type": "date_range",
                        }
                    }
                },
            }
        },
        "location": {"type": "geo_point"},
    }
}


class LocationImporter(Importer[Root]):
    index_base_names = ("location",)

    def run(self):  # noqa C901 this function could use some refactoring
        self.apply_mapping(custom_mappings)

        logger.debug("Requesting data at {}".format(__name__))

        ontology = Ontology()

        tpr_units = get_tpr_units()

        opening_hours_fetcher = HaukiOpeningHoursFetcher(t["id"] for t in tpr_units)
        administrative_division_fetcher = AdministrativeDivisionFetcher()

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

            # Assuming single image
            images = []
            images.append(
                Image(
                    url=e("picture_url"),
                    caption=l.get_language_string("picture_caption"),
                )
            )

            (
                opening_hours,
                opening_hours_link,
            ) = opening_hours_fetcher.get_opening_hours_and_link(_id)

            venue = Venue(
                name=l.get_language_string("name"),
                description=l.get_language_string("desc"),
                location=location,
                meta=meta,
                openingHours=opening_hours,
                images=images,
            )
            root = Root(venue=venue)

            if opening_hours_link:
                root.links.append(opening_hours_link)

            coordinates = venue.location.geoLocation.geometry.coordinates
            venue.location.administrativeDivisions = (
                administrative_division_fetcher.get_by_coordinates(
                    longitude=coordinates.longitude, latitude=coordinates.latitude
                )
            )

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
                venue.ontologyWords = [
                    {
                        "id": word["id"],
                        "label": {
                            "fi": word["ontologyword_fi"],
                            "sv": word["ontologyword_sv"],
                            "en": word["ontologyword_en"],
                        },
                    }
                    for word in word_ontologies
                ]

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

            root.location = (
                {"lat": e("latitude"), "lon": e("longitude")}
                if e("latitude") and e("longitude")
                else None
            )

            self.add_data(root)

            logger.debug(f"Fetched data count: {count}")
            count = count + 1

        logger.info(f"Fetched {count} items in total")

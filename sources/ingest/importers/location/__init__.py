from __future__ import annotations

import logging
from datetime import datetime
from email.headerregistry import Address

from typing import List

from ingest.importers.base import Importer
from ingest.importers.location.dataclasses import (
    Accessibility,
    Coordinates,
    GeoJSONFeature,
    GeoJSONGeometry,
    Image,
    LinkedData,
    Location,
    NodeMeta,
    Root,
    ServiceOwner,
    Venue,
)
from ingest.importers.location.enums import ProviderType, ServiceOwnerType
from ingest.importers.location.utils import (
    define_language_properties,
    get_accessibility_viewpoint_id_to_name_mapping,
    get_enriched_accessibility_viewpoints,
    get_ontologytree_as_ontologies,
    get_ontologywords_as_ontologies,
    get_suggestions_from_ontologies,
    get_tpr_units,
    get_unit_id_to_accessibility_sentences_mapping,
    get_unit_id_to_accessibility_shortcomings_mapping,
    get_unit_id_to_accessibility_viewpoint_shortages_mapping,
    get_unit_id_to_resources_mapping,
    get_unit_id_to_target_groups_mapping,
)
from ingest.importers.utils.administrative_division import AdministrativeDivisionFetcher
from ingest.importers.utils import LanguageStringConverter, Ontology, HaukiOpeningHoursFetcher

BATCH_SIZE = 100

logger = logging.getLogger(__name__)


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
                "accessibility": {
                    "properties": {
                        "shortcomings": {
                            "type": "nested",
                            "properties": {
                                "profile": {"type": "keyword"},
                                "count": {
                                    "type": "integer",
                                    "null_value": 9999,  # Larger than any real value
                                },
                            },
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

        unit_id_to_accessibility_shortcomings_mapping = (
            get_unit_id_to_accessibility_shortcomings_mapping()
        )
        unit_id_to_accessibility_sentences_mapping = (
            get_unit_id_to_accessibility_sentences_mapping(self.use_fallback_languages)
        )
        unit_id_to_accessibility_viewpoint_shortages_mapping = (
            get_unit_id_to_accessibility_viewpoint_shortages_mapping(
                self.use_fallback_languages
            )
        )
        unit_id_to_resources_mapping = get_unit_id_to_resources_mapping(
            self.use_fallback_languages
        )
        unit_id_to_target_groups_mapping = get_unit_id_to_target_groups_mapping()
        accessibility_viewpoint_id_to_name_mapping = (
            get_accessibility_viewpoint_id_to_name_mapping(self.use_fallback_languages)
        )
        tpr_units = get_tpr_units()

        opening_hours_fetcher = HaukiOpeningHoursFetcher(t["id"] for t in tpr_units)
        administrative_division_fetcher = AdministrativeDivisionFetcher()

        data_buffer: List[Root] = []
        count = 0
        for tpr_unit in tpr_units:
            l = LanguageStringConverter(tpr_unit, self.use_fallback_languages)
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
                serviceOwner=ServiceOwner(
                    providerType=ProviderType(
                        e("provider_type") or ProviderType.UNKNOWN_PRODUCTION_METHOD
                    ).value,
                    type=ServiceOwnerType(
                        e("displayed_service_owner_type")
                        or ServiceOwnerType.NOT_DISPLAYED
                    ).value,
                    name=l.get_language_string("displayed_service_owner"),
                ),
                resources=unit_id_to_resources_mapping.get(_id, []),
                targetGroups=sorted(
                    target_group.value
                    for target_group in unit_id_to_target_groups_mapping.get(_id, set())
                ),
                location=location,
                meta=meta,
                openingHours=opening_hours,
                accessibility=Accessibility(
                    email=e("accessibility_email"),
                    phone=e("accessibility_phone"),
                    www=e("accessibility_www"),
                    viewpoints=get_enriched_accessibility_viewpoints(
                        e("accessibility_viewpoints"),
                        accessibility_viewpoint_id_to_name_mapping,
                        omit_unknowns=True,
                    ),
                    sentences=unit_id_to_accessibility_sentences_mapping.get(_id, []),
                    shortcomings=unit_id_to_accessibility_shortcomings_mapping.get(
                        _id, []
                    ),
                ),
                images=images,
            )

            # Add accessibility viewpoints' shortages to the venue
            venue.accessibility.set_accessibility_shortages(
                unit_id_to_accessibility_viewpoint_shortages_mapping.get(_id, dict())
            )

            venue.accessibility.fix_unknown_and_zero_shortcomings()

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
                all_ontologies += get_ontologywords_as_ontologies(
                    word_ontologies, self.use_fallback_languages
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
                all_ontologies += get_ontologytree_as_ontologies(
                    tree_ontologies, self.use_fallback_languages
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

            data_buffer.append(root)
            if len(data_buffer) >= BATCH_SIZE:
                self.add_data_bulk(data_buffer)
                data_buffer = []

            logger.debug(f"Fetched data count: {count}")
            count = count + 1

        if data_buffer:
            self.add_data_bulk(data_buffer)

        logger.info(f"Fetched {count} items in total")

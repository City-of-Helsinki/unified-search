from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Callable, List, Optional

from ingest.importers.base import Importer
from ingest.importers.decorators import with_conditional
from ingest.importers.location.api import LocationImporterAPI
from ingest.importers.location.dataclasses import (
    Accessibility,
    Address,
    Connection,
    Coordinates,
    GeoJSONFeature,
    GeoJSONGeometry,
    Image,
    LinkedData,
    Location,
    NodeMeta,
    OntologyObject,
    Reservation,
    Root,
    ServiceOwner,
    Venue,
)
from ingest.importers.location.enums import ProviderType, ServiceOwnerType
from ingest.importers.location.utils import (
    define_language_properties,
    find_reservable_connection,
    get_accessibility_viewpoint_id_to_name_mapping,
    get_enriched_accessibility_viewpoints,
    get_ontologytree_as_ontologies,
    get_ontologywords_as_ontologies,
    get_suggestions_from_ontologies,
    get_unit_id_to_accessibility_sentences_mapping,
    get_unit_id_to_accessibility_shortcomings_mapping,
    get_unit_id_to_accessibility_viewpoint_shortages_mapping,
    get_unit_id_to_connections_mapping,
    get_unit_id_to_target_groups_mapping,
)
from ingest.importers.utils import (
    HaukiOpeningHoursFetcher,
    LanguageStringConverter,
    Ontology,
    OpeningHours,
)
from ingest.importers.utils.administrative_division import AdministrativeDivisionFetcher

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

    def __init__(self, *args, enable_data_fetching=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.enable_data_fetching = enable_data_fetching
        self._init_base_data()

    def _init_base_data(self):
        if not self.enable_data_fetching:
            logger.info(
                "The LocationImporter instance enable_data_fetching is set to `False`."
                "This means that the LocationImporter instance will be initialized with an empty base data."
                "To actually fetch some base data, set the `enable_data_fetching` to `True`."
            )

        api = LocationImporterAPI()

        self.tpr_units = with_conditional(
            self.enable_data_fetching, lambda: api.fetch_tpr_units(), []
        )

        self.unit_id_to_accessibility_shortcomings_mapping = with_conditional(
            self.enable_data_fetching,
            lambda: get_unit_id_to_accessibility_shortcomings_mapping(),
            {},
        )

        self.unit_id_to_accessibility_sentences_mapping = with_conditional(
            self.enable_data_fetching,
            lambda: get_unit_id_to_accessibility_sentences_mapping(
                self.use_fallback_languages
            ),
            {},
        )

        self.unit_id_to_accessibility_viewpoint_shortages_mapping = with_conditional(
            self.enable_data_fetching,
            lambda: get_unit_id_to_accessibility_viewpoint_shortages_mapping(
                self.use_fallback_languages
            ),
            {},
        )

        self.unit_id_to_target_groups_mapping = with_conditional(
            self.enable_data_fetching,
            lambda: get_unit_id_to_target_groups_mapping(),
            {},
        )

        self.accessibility_viewpoint_id_to_name_mapping = with_conditional(
            self.enable_data_fetching,
            lambda: get_accessibility_viewpoint_id_to_name_mapping(
                self.use_fallback_languages
            ),
            {},
        )

        self.unit_id_to_connections_mapping = with_conditional(
            self.enable_data_fetching,
            lambda: get_unit_id_to_connections_mapping(self.use_fallback_languages),
            {},
        )

        self.opening_hours_fetcher = (
            HaukiOpeningHoursFetcher(t["id"] for t in self.tpr_units)
            if self.enable_data_fetching and len(self.tpr_units)
            else None
        )

        self.administrative_division_fetcher = (
            AdministrativeDivisionFetcher() if self.enable_data_fetching else None
        )

        self.ontology = Ontology() if self.enable_data_fetching else None
        logger.info("LocationImporter base data initialized")

    def _create_location(self, l: LanguageStringConverter, e: Callable[[Any], Any]):
        return Location(
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

    def _create_images(self, l: LanguageStringConverter, e: Callable[[Any], Any]):
        # Assume single image
        return [
            Image(
                url=e("picture_url"),
                caption=l.get_language_string("picture_caption"),
            )
        ]

    def _create_reservation(self, connections: Optional[Connection]):
        if connections and len(connections):
            reservation_connection = find_reservable_connection(connections)
            if reservation_connection:
                return Reservation(
                    reservable=True,
                    externalReservationUrl=reservation_connection.www,
                )
            return Reservation(reservable=False, externalReservationUrl=None)
        return None

    def _create_venue(
        self,
        l: LanguageStringConverter,
        e: Callable[[Any], Any],
        _id: str,
        opening_hours: OpeningHours,
        ontology_words: List[OntologyObject],
    ):
        location = self._create_location(l, e)
        meta = NodeMeta(id=_id, createdAt=datetime.now())
        # Assuming single image
        images = self._create_images(l, e)
        connections = self.unit_id_to_connections_mapping.get(_id)
        reservation = self._create_reservation(connections)
        venue = Venue(
            name=l.get_language_string("name"),
            description=l.get_language_string("desc"),
            serviceOwner=ServiceOwner(
                providerType=ProviderType(
                    e("provider_type") or ProviderType.UNKNOWN_PRODUCTION_METHOD
                ).value,
                type=ServiceOwnerType(
                    e("displayed_service_owner_type") or ServiceOwnerType.NOT_DISPLAYED
                ).value,
                name=l.get_language_string("displayed_service_owner"),
            ),
            targetGroups=sorted(
                target_group.value
                for target_group in self.unit_id_to_target_groups_mapping.get(
                    _id, set()
                )
            ),
            location=location,
            meta=meta,
            openingHours=opening_hours,
            reservation=reservation,
            accessibility=Accessibility(
                email=e("accessibility_email"),
                phone=e("accessibility_phone"),
                www=e("accessibility_www"),
                viewpoints=get_enriched_accessibility_viewpoints(
                    e("accessibility_viewpoints"),
                    self.accessibility_viewpoint_id_to_name_mapping,
                    omit_unknowns=True,
                ),
                sentences=self.unit_id_to_accessibility_sentences_mapping.get(_id, []),
                shortcomings=self.unit_id_to_accessibility_shortcomings_mapping.get(
                    _id, []
                ),
            ),
            images=images,
            ontologyWords=ontology_words,
        )

        # Add accessibility viewpoints' shortages to the venue
        venue.accessibility.set_accessibility_shortages(
            self.unit_id_to_accessibility_viewpoint_shortages_mapping.get(_id, dict())
        )
        venue.accessibility.fix_unknown_and_zero_shortcomings()

        coordinates = venue.location.geoLocation.geometry.coordinates

        if self.administrative_division_fetcher:
            venue.location.administrativeDivisions = (
                self.administrative_division_fetcher.get_by_coordinates(
                    longitude=coordinates.longitude, latitude=coordinates.latitude
                )
            )

        return venue

    def _collect_ontologies(self, tpr_unit: Any):
        # TODO: Separate words from tree
        # TODO: Remove duplicates
        #       Duplicates are not yet removed, because ontologies are not
        #       returned in a public facing data structure.
        all_ontologies = []
        ontology_words = []
        # Ontology ID's and tree contain plain integers, get corresponding texts
        if tpr_unit.get("ontologyword_ids", None):
            word_ontologies = self.ontology.enrich_word_ids(
                tpr_unit["ontologyword_ids"]
            )
            tpr_unit["ontologyword_ids_enriched"] = word_ontologies
            all_ontologies += get_ontologywords_as_ontologies(
                word_ontologies, self.use_fallback_languages
            )
            ontology_words = [
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
            tree_ontologies = self.ontology.enrich_tree_ids(
                tpr_unit["ontologytree_ids"]
            )
            tpr_unit["ontologytree_ids_enriched"] = tree_ontologies
            all_ontologies += get_ontologytree_as_ontologies(
                tree_ontologies, self.use_fallback_languages
            )

        return (all_ontologies, ontology_words)

    def _create_root_from_tpr_unit(self, tpr_unit: Any) -> Root:
        l = LanguageStringConverter(tpr_unit, self.use_fallback_languages)
        e = lambda k: tpr_unit.get(k, None)  # noqa: E731
        # ID's must be strings to avoid collisions
        tpr_unit["id"] = _id = str(tpr_unit["id"])
        # Extra information to raw data
        tpr_unit["origin"] = "tpr"

        link = LinkedData(
            service="tpr",
            origin_url=f"https://www.hel.fi/palvelukarttaws/rest/v4/unit/{_id}/",
            raw_data=tpr_unit,
        )

        (
            opening_hours,
            opening_hours_link,
        ) = (
            self.opening_hours_fetcher.get_opening_hours_and_link(_id)
            if self.opening_hours_fetcher
            else ([], "")
        )

        (all_ontologies, ontology_words) = self._collect_ontologies(tpr_unit)

        venue = self._create_venue(l, e, _id, opening_hours, ontology_words)

        location = (
            {"lat": e("latitude"), "lon": e("longitude")}
            if e("latitude") and e("longitude")
            else None
        )

        root = Root(
            venue=venue,
            links=[link],
            suggest=get_suggestions_from_ontologies(all_ontologies),
            location=location,
        )

        if opening_hours_link:
            root.links.append(opening_hours_link)

        return root

    def run(self):  # noqa C901 this function could use some refactoring
        """
        Import location data.
        :return the count of units imported.
        """
        self.apply_mapping(custom_mappings)

        logger.debug("Requesting data at {}".format(__name__))

        data_buffer: List[Root] = []
        count = 0

        if self.enable_data_fetching:
            for tpr_unit in self.tpr_units:
                logger.debug(f"Fetching data for an id '{tpr_unit['id']}'.")
                root = self._create_root_from_tpr_unit(tpr_unit)
                data_buffer.append(root)
                if len(data_buffer) >= BATCH_SIZE:
                    self.add_data_bulk(data_buffer)
                    data_buffer = []
                logger.debug(f"Fetched data count: {count}")
                count = count + 1

            if data_buffer:
                self.add_data_bulk(data_buffer)

            logger.info(f"Fetched {count} items in total")
        return count

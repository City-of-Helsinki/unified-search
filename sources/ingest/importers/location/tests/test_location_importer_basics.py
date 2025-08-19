import pytest

from ingest.importers.location.dataclasses import Connection, Reservation
from ingest.importers.location.enums import ConnectionTag
from ingest.importers.location.importers import LocationImporter
from ingest.importers.utils.shared import LanguageString


@pytest.mark.django_db
def test_location_importer_with_data_init(
    mocked_ontology_trees,
    mocked_ontology_words,
    mocked_tpr_units_response,
    mocked_service_map_connections_response,
    mocked_service_map_accessibility_sentence_viewpoint_response,
    mocked_service_map_accessibility_shortage_viewpoint_response,
    mocked_opening_hours_response,
    mocked_service_map_unit_viewpoint_response,
    mocked_service_map_accessibility_viewpoint_response,
    mocked_service_registry_description_viewpoint_response,
    mocked_geo_municipalities,
    mocked_geo_divisions,
    es,
):
    importer = LocationImporter(enable_data_fetching=True)
    assert len(importer.tpr_units) == 2
    assert len(importer.unit_id_to_accessibility_shortcomings_mapping) == 3
    assert len(importer.unit_id_to_accessibility_sentences_mapping) == 2
    assert len(importer.unit_id_to_accessibility_viewpoint_shortages_mapping) == 2
    assert len(importer.unit_id_to_target_groups_mapping) == 8
    assert len(importer.unit_id_to_connections_mapping) == 2
    assert len(importer.accessibility_viewpoint_id_to_name_mapping) == 14
    assert importer.base_run() == len(importer.tpr_units)


def test_location_importer_without_data_init():
    importer = LocationImporter(enable_data_fetching=False)
    assert len(importer.tpr_units) == 0
    assert len(importer.unit_id_to_accessibility_shortcomings_mapping) == 0
    assert len(importer.unit_id_to_accessibility_sentences_mapping) == 0
    assert len(importer.unit_id_to_accessibility_viewpoint_shortages_mapping) == 0
    assert len(importer.unit_id_to_target_groups_mapping) == 0
    assert len(importer.unit_id_to_connections_mapping) == 0
    assert len(importer.accessibility_viewpoint_id_to_name_mapping) == 0
    assert importer.base_run() == 0


def test_create_reservation():
    importer = LocationImporter(enable_data_fetching=False)
    # assert importer._create_reservation(None) == None
    test_connection = Connection(
        section_type="TEST",
        name=LanguageString(
            fi="nimi",
            sv="namn",
            en="name",
        ),
        tags=[],
    )
    assert importer._create_reservation([test_connection]) == Reservation(
        reservable=False,
        externalReservationUrl=None,
    )
    test_connection = Connection(
        section_type="TEST",
        name=LanguageString(
            fi="nimi",
            sv="namn",
            en="name",
        ),
        www=LanguageString(
            fi="www.hel.fi",
            sv="www.hel.fi/sv",
            en="www.hel.fi/en",
        ),
        tags=[ConnectionTag.RESERVABLE.value],
    )
    reservation = importer._create_reservation([test_connection])
    assert reservation.reservable is True
    assert reservation.externalReservationUrl == test_connection.www

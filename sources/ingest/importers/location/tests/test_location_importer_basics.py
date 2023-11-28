import pytest

from ingest.importers.location.importers import LocationImporter


@pytest.mark.django_db
def test_location_importer_run_happy_path(
    mocked_ontology_trees,
    mocked_ontology_words,
    mocked_tpr_units_response,
    mocked_service_map_accessibility_sentence_viewpoint_response,
    mocked_service_map_accessibility_shortage_viewpoint_response,
    mocked_opening_hours_response,
    mocked_service_map_unit_viewpoint_response,
    mocked_service_map_accessibility_viewpoint_response,
    mocked_service_registry_description_viewpoint_response,
    mocked_geo_municipalities,
    mocked_geo_divisions,
):
    importer = LocationImporter()
    assert len(importer.tpr_units) == 2
    assert len(importer.unit_id_to_accessibility_shortcomings_mapping) == 3
    assert len(importer.unit_id_to_accessibility_sentences_mapping) == 2
    assert len(importer.unit_id_to_accessibility_viewpoint_shortages_mapping) == 2
    assert len(importer.unit_id_to_target_groups_mapping) == 8
    assert len(importer.accessibility_viewpoint_id_to_name_mapping) == 14
    assert importer.run() == len(importer.tpr_units)

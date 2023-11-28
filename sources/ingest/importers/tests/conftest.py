import pytest
from django.conf import settings
from opensearchpy import OpenSearch

from ingest.importers.tests.mocks import (
    MOCK_OPENING_HOURS_RESPONSE,
    MOCKED_SERVICE_MAP_ACCESSIBILITY_SENTENCE_VIEWPOINT_RESPONSE,
    MOCKED_SERVICE_MAP_ACCESSIBILITY_SHORTAGE_VIEWPOINT_RESPONSE,
    MOCKED_SERVICE_MAP_ACCESSIBILITY_VIEWPOINT_RESPONSE,
    MOCKED_SERVICE_MAP_CONNECTIONS_RESPONSE,
    MOCKED_SERVICE_MAP_UNIT_VIEWPOINT_RESPONSE,
    MOCKED_SERVICE_MAP_UNITS_RESPONSE,
    MOCKED_SERVICE_REGISTRY_DESCRIPTION_VIEWPOINT_RESPONSE,
    ontology_tree,
    ontology_words,
)


@pytest.fixture
def mocked_ontology_trees(mocker):
    return mocker.patch(
        "ingest.importers.utils.ontology.Ontology._get_ontology_tree_ids",
        return_value=ontology_tree,
    )


@pytest.fixture
def mocked_ontology_words(mocker):
    return mocker.patch(
        "ingest.importers.utils.ontology.Ontology._get_ontology_word_ids",
        return_value=ontology_words,
    )


@pytest.fixture()
def mocked_tpr_units_response(mocker):
    return mocker.patch(
        "ingest.importers.location.api.LocationImporterAPI.fetch_tpr_units",
        return_value=MOCKED_SERVICE_MAP_UNITS_RESPONSE,
    )


@pytest.fixture()
def mocked_service_map_connections_response(mocker):
    return mocker.patch(
        "ingest.importers.location.api.LocationImporterAPI.fetch_connections",
        return_value=MOCKED_SERVICE_MAP_CONNECTIONS_RESPONSE,
    )


@pytest.fixture
def mocked_service_map_accessibility_sentence_viewpoint_response(mocker):
    return mocker.patch(
        "ingest.importers.location.api.LocationImporterAPI.fetch_accessibility_sentence",
        return_value=MOCKED_SERVICE_MAP_ACCESSIBILITY_SENTENCE_VIEWPOINT_RESPONSE,
    )


@pytest.fixture
def mocked_service_map_accessibility_shortage_viewpoint_response(mocker):
    return mocker.patch(
        "ingest.importers.location.api.LocationImporterAPI.fetch_accessibility_shortages",
        return_value=MOCKED_SERVICE_MAP_ACCESSIBILITY_SHORTAGE_VIEWPOINT_RESPONSE,
    )


@pytest.fixture()
def mocked_opening_hours_response(mocker):
    return mocker.patch(
        "ingest.importers.utils.opening_hours.request_json",
        return_value=MOCK_OPENING_HOURS_RESPONSE,
    )


@pytest.fixture
def mocked_service_map_unit_viewpoint_response(mocker):
    return mocker.patch(
        "ingest.importers.location.api.LocationImporterAPI.fetch_accessibility_shortcoming",
        return_value=MOCKED_SERVICE_MAP_UNIT_VIEWPOINT_RESPONSE,
    )


@pytest.fixture(scope="module", autouse=True)
def mocked_service_map_accessibility_viewpoint_response(module_mocker):
    return module_mocker.patch(
        "ingest.importers.location.api.LocationImporterAPI.fetch_accessibility_viewpoint",
        return_value=MOCKED_SERVICE_MAP_ACCESSIBILITY_VIEWPOINT_RESPONSE,
    )


@pytest.fixture
def mocked_service_registry_description_viewpoint_response(mocker):
    return mocker.patch(
        "ingest.importers.location.api.LocationImporterAPI.fetch_services",
        return_value=MOCKED_SERVICE_REGISTRY_DESCRIPTION_VIEWPOINT_RESPONSE,
    )


@pytest.fixture
def es():
    es = OpenSearch([settings.ES_URI])
    yield es
    es.indices.delete("test_*")


@pytest.fixture
def mocked_geo_municipalities(mocker):
    return mocker.patch(
        "ingest.importers.utils.administrative_division.geo_import_finnish_municipalities",
        return_value=[],
    )


@pytest.fixture
def mocked_geo_divisions(mocker):
    return mocker.patch(
        "ingest.importers.utils.administrative_division.geo_import_helsinki_divisions",
        return_value=[],
    )

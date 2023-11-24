import pytest
from django.conf import settings
from opensearchpy import OpenSearch

from ingest.importers.tests.mocks import (
    MOCK_OPENING_HOURS_RESPONSE,
    MOCKED_SERVICE_MAP_ACCESSIBILITY_SENTENCE_VIEWPOINT_RESPONSE,
    MOCKED_SERVICE_MAP_ACCESSIBILITY_SHORTAGE_VIEWPOINT_RESPONSE,
    MOCKED_SERVICE_MAP_ACCESSIBILITY_VIEWPOINT_RESPONSE,
    MOCKED_SERVICE_MAP_UNIT_VIEWPOINT_RESPONSE,
    MOCKED_SERVICE_MAP_UNITS_RESPONSE,
    MOCKED_SERVICE_REGISTRY_DESCRIPTION_VIEWPOINT_RESPONSE,
)


@pytest.fixture()
def patch_get_tpr_units_response(mocker):
    return mocker.patch(
        "ingest.importers.location.utils.get_tpr_units",
        return_value=MOCKED_SERVICE_MAP_UNITS_RESPONSE,
    )


@pytest.fixture
def mocked_service_map_accessibility_sentence_viewpoint_response(mocker):
    return mocker.patch(
        "ingest.importers.location.utils.request_json",
        return_value=MOCKED_SERVICE_MAP_ACCESSIBILITY_SENTENCE_VIEWPOINT_RESPONSE,
    )


@pytest.fixture
def mocked_service_map_accessibility_shortage_viewpoint_response(mocker):
    return mocker.patch(
        "ingest.importers.location.utils.request_json",
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
        "ingest.importers.location.utils.request_json",
        return_value=MOCKED_SERVICE_MAP_UNIT_VIEWPOINT_RESPONSE,
    )


@pytest.fixture(scope="module", autouse=True)
def mocked_service_map_accessibility_viewpoint_response(module_mocker):
    return module_mocker.patch(
        "ingest.importers.location.utils.request_json",
        return_value=MOCKED_SERVICE_MAP_ACCESSIBILITY_VIEWPOINT_RESPONSE,
    )


@pytest.fixture
def mocked_service_registry_description_viewpoint_response(mocker):
    return mocker.patch(
        "ingest.importers.location.utils.request_json",
        return_value=MOCKED_SERVICE_REGISTRY_DESCRIPTION_VIEWPOINT_RESPONSE,
    )


@pytest.fixture
def es():
    es = OpenSearch([settings.ES_URI])
    yield es
    es.indices.delete("test_*")

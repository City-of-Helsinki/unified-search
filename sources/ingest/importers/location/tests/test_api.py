from unittest.mock import patch

from ingest.importers.location.api import LocationImporterAPI
from ingest.importers.tests.mocks import (
    MOCKED_LINKED_EVENTS_PLACES_RESPONSE,
    MOCKED_SERVICE_MAP_ACCESSIBILITY_SENTENCE_VIEWPOINT_RESPONSE,
    MOCKED_SERVICE_MAP_ACCESSIBILITY_SHORTAGE_VIEWPOINT_RESPONSE,
    MOCKED_SERVICE_MAP_ACCESSIBILITY_VIEWPOINT_RESPONSE,
    MOCKED_SERVICE_MAP_UNITS_RESPONSE,
    MOCKED_SERVICE_REGISTRY_DESCRIPTION_VIEWPOINT_RESPONSE,
)


@patch(
    "ingest.importers.location.api.request_json",
    return_value=MOCKED_SERVICE_MAP_UNITS_RESPONSE,
)
def test_fetch_tpr_units(mocked_response):
    data = LocationImporterAPI.fetch_tpr_units()
    assert len(data) == len(MOCKED_SERVICE_MAP_UNITS_RESPONSE) == 2


@patch(
    "ingest.importers.location.api.request_json",
    return_value=MOCKED_SERVICE_MAP_UNITS_RESPONSE,
)
def test_fetch_culture_and_leisure_division_tpr_units(mocked_response):
    data = LocationImporterAPI.fetch_culture_and_leisure_division_tpr_units()
    assert len(data) == len(MOCKED_SERVICE_MAP_UNITS_RESPONSE) == 2


@patch(
    "ingest.importers.location.api.request_json",
    return_value=MOCKED_LINKED_EVENTS_PLACES_RESPONSE,
)
def test_fetch_event_counts_per_tpr_unit(mocked_response):
    data = LocationImporterAPI.fetch_event_counts_per_tpr_unit()
    # Only TPR unit IDs are included in the mapping, others are ignored
    assert data == {"6964": 286, "7076": 284}


@patch(
    "ingest.importers.location.api.request_json",
    return_value=MOCKED_SERVICE_MAP_ACCESSIBILITY_SHORTAGE_VIEWPOINT_RESPONSE,
)
def test_fetch_accessibility_shortcoming(mocked_response):
    data = LocationImporterAPI.fetch_accessibility_shortcoming(
        LocationImporterAPI.accessibility_shortcoming_counts_endpoint
    )
    assert (
        len(data)
        == len(MOCKED_SERVICE_MAP_ACCESSIBILITY_SHORTAGE_VIEWPOINT_RESPONSE)
        == 4
    )


@patch(
    "ingest.importers.location.api.request_json",
    return_value=MOCKED_SERVICE_MAP_ACCESSIBILITY_SHORTAGE_VIEWPOINT_RESPONSE,
)
@patch(
    "ingest.importers.location.api.LocationImporterAPI.fetch_accessibility_shortcoming",
    return_value={
        "next": None,
        "results": MOCKED_SERVICE_MAP_ACCESSIBILITY_SHORTAGE_VIEWPOINT_RESPONSE,
    },
)
def test_fetch_unit_ids_and_accessibility_shortcoming_counts(fetcher, mocked_response):
    data = LocationImporterAPI.fetch_unit_ids_and_accessibility_shortcoming_counts()
    assert fetcher.call_count > 0
    assert (
        len(data)
        == len(MOCKED_SERVICE_MAP_ACCESSIBILITY_SHORTAGE_VIEWPOINT_RESPONSE)
        == 4
    )


@patch(
    "ingest.importers.location.api.request_json",
    return_value=MOCKED_SERVICE_MAP_ACCESSIBILITY_VIEWPOINT_RESPONSE,
)
def test_fetch_accessibility_viewpoint(mocked_response):
    data = LocationImporterAPI.fetch_accessibility_viewpoint()
    assert len(data) == len(MOCKED_SERVICE_MAP_ACCESSIBILITY_VIEWPOINT_RESPONSE) == 14


@patch(
    "ingest.importers.location.api.request_json",
    return_value=MOCKED_SERVICE_MAP_ACCESSIBILITY_SENTENCE_VIEWPOINT_RESPONSE,
)
def test_fetch_accessibility_sentence(mocked_response):
    data = LocationImporterAPI.fetch_accessibility_sentence()
    assert (
        len(data)
        == len(MOCKED_SERVICE_MAP_ACCESSIBILITY_SENTENCE_VIEWPOINT_RESPONSE)
        == 3
    )


@patch(
    "ingest.importers.location.api.request_json",
    return_value=MOCKED_SERVICE_MAP_ACCESSIBILITY_SHORTAGE_VIEWPOINT_RESPONSE,
)
def test_fetch_accessibility_shortages(mocked_response):
    data = LocationImporterAPI.fetch_accessibility_shortages()
    assert (
        len(data)
        == len(MOCKED_SERVICE_MAP_ACCESSIBILITY_SHORTAGE_VIEWPOINT_RESPONSE)
        == 4
    )


@patch(
    "ingest.importers.location.api.request_json",
    return_value=MOCKED_SERVICE_REGISTRY_DESCRIPTION_VIEWPOINT_RESPONSE,
)
def test_fetch_services(mocked_response):
    data = LocationImporterAPI.fetch_services()
    assert len(data) == len(MOCKED_SERVICE_REGISTRY_DESCRIPTION_VIEWPOINT_RESPONSE) == 4

import pytest
import requests
from django.conf import settings
from elasticsearch import Elasticsearch

from ingest.importers.tests.mocks import (
    MOCK_OPENING_HOURS_RESPONSE,
    MOCKED_EVENT_COUNTS_PER_TPR_UNIT_RESPONSE,
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
def mocked_culture_and_leisure_division_tpr_units_response(mocker):
    return mocker.patch(
        "ingest.importers.location.api.LocationImporterAPI.fetch_culture_and_leisure_division_tpr_units",
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


@pytest.fixture()
def mocked_event_counts_per_tpr_unit_response(mocker):
    return mocker.patch(
        "ingest.importers.location.api.LocationImporterAPI.fetch_event_counts_per_tpr_unit",
        return_value=MOCKED_EVENT_COUNTS_PER_TPR_UNIT_RESPONSE,
    )


@pytest.fixture
def es():
    es = Elasticsearch([settings.ES_URI])
    yield es
    es.indices.delete(index="test_*")


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


def allow_only_requests_to_urls(mocker, allowed_urls: list):
    """
    Allow requests (GET, HEAD, POST, PUT, DELETE, OPTIONS and PATCH)
    only to allowed URLs, and require all other connections to be mocked.

    :param mocker: The pytest-mock mocker fixture.
    :param allowed_urls: A list of allowed URLs.
    :raises AssertionError: If an unmocked request is made to a URL
                            not in the allowed_urls list.
    """
    original_methods = {
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods
        # except no CONNECT or TRACE methods
        method: getattr(requests, method)
        for method in ["get", "head", "post", "put", "delete", "options", "patch"]
    }

    for method in original_methods.keys():

        def raise_error_if_not_allowed_url(*args, _method=method, **kwargs):
            url = args[0] if args else kwargs.get("url", "")
            if url not in allowed_urls:
                raise AssertionError(
                    f"Unmocked {_method.upper()} request to: {url}\n"
                    f"Add a fixture to mock this endpoint."
                )
            # If we get here, it's an allowed connection
            return original_methods[_method](*args, **kwargs)

        mocker.patch.object(
            requests, method, side_effect=raise_error_if_not_allowed_url
        )


# By default, allow only real requests to Elasticsearch in tests
@pytest.fixture(scope="module", autouse=True)
def allow_only_real_elasticsearch_requests(module_mocker):
    """
    Allow real (i.e. unmocked) requests only to Elasticsearch,
    and require all other connections to be mocked.
    """
    allow_only_requests_to_urls(module_mocker, allowed_urls=[settings.ES_URI])

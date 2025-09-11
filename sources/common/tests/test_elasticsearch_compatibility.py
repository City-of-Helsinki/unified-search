from unittest import mock

import pytest

from ..elasticsearch_compatibility import (
    get_compatible_elasticsearch_package,
    get_elasticsearch_package_for_version,
    get_elasticsearch_server_major_version,
)


def empty_function():
    pass


UNSUPPORTED_OR_INVALID_VERSIONS = (-1, 0, 1, 7, 10, 999, None)


@pytest.mark.parametrize(
    "mocked_version_number, expected_version",
    [
        ("8", 8),
        ("9", 9),
        ("8.5.0", 8),
        ("8.12", 8),
        ("9.1.3", 9),
        ("9.4321.1234", 9),
        ("10.1.2.3.4.5", 10),
        ("999.888.777", 999),
    ],
)
def test_get_elasticsearch_server_major_version_success(
    mocked_version_number, expected_version
):
    """
    Test that the function correctly extracts the major version from various formats.
    """
    with mock.patch("requests.get") as mock_get:
        mock_get.return_value.raise_for_status = empty_function
        mock_get.return_value.json.return_value = {
            "version": {"number": mocked_version_number}
        }
        result = get_elasticsearch_server_major_version()
        assert result == expected_version


@pytest.mark.parametrize(
    "mocked_version_number", [8, "abc", "v8", "version 8", "", None, ".8"]
)
def test_get_elasticsearch_server_major_version_failure_with_wrong_version_format(
    mocked_version_number,
):
    """
    Test that the function raises an exception when the version format is incorrect.
    """
    with mock.patch("requests.get") as mock_get:
        mock_get.return_value.raise_for_status = empty_function
        mock_get.return_value.json.return_value = {
            "version": {"number": mocked_version_number}
        }
        with pytest.raises((AttributeError, ValueError)):
            get_elasticsearch_server_major_version()


def test_get_elasticsearch_server_major_version_failure_with_wrong_structure():
    """
    Test that the function raises KeyError when the JSON structure is not as expected.
    """
    with mock.patch("requests.get") as mock_get:
        mock_get.return_value.raise_for_status = empty_function
        mock_get.return_value.json.return_value = {}
        with pytest.raises(KeyError):
            get_elasticsearch_server_major_version()


@pytest.mark.parametrize(
    "mocked_es_uri",
    [
        "https://localhost:9200",
        "https://example.com:9200",
        "https://es-server-test:443",
    ],
)
def test_get_elasticsearch_server_major_version_uses_es_uri(settings, mocked_es_uri):
    """
    Test that the function uses the ES_URI from settings.
    """
    settings.ES_URI = mocked_es_uri
    with mock.patch("requests.get") as mock_get:
        mock_get.return_value.raise_for_status = empty_function
        mock_get.return_value.json.return_value = {"version": {"number": "8.5.0"}}
        get_elasticsearch_server_major_version()
        mock_get.assert_called_once_with(mocked_es_uri)


@pytest.mark.parametrize("version", ["8", "9", 8, 9])
def test_get_elasticsearch_package_for_version_success(version):
    """
    Test that returned package is correct for supported Elasticsearch versions.
    """
    result = get_elasticsearch_package_for_version(version)
    # Check result package version
    assert result.__name__.startswith("elasticsearch")
    assert str(result.__version__[0]) == str(version)  # e.g. __version__ = (9, 0, 3)
    # Check that some used components are accessible through the package
    assert callable(result.Elasticsearch)
    assert callable(result.helpers.bulk)
    assert issubclass(result.exceptions.NotFoundError, Exception)


@pytest.mark.parametrize("version", UNSUPPORTED_OR_INVALID_VERSIONS)
def test_get_elasticsearch_package_for_version_failure(version):
    """
    Test that the function raises ValueError for unsupported Elasticsearch versions.
    """
    with pytest.raises(ValueError):
        get_elasticsearch_package_for_version(version)


@pytest.mark.parametrize("mocked_version_number", [8, 9])
def test_get_compatible_elasticsearch_package_success(mocked_version_number):
    """
    Test that the function returns the correct package based on the return value of
    get_elasticsearch_server_major_version function.
    """
    with mock.patch(
        "common.elasticsearch_compatibility.get_elasticsearch_server_major_version"
    ) as mock_get_server_version:
        mock_get_server_version.return_value = mocked_version_number
        result = get_compatible_elasticsearch_package()
        assert result == get_elasticsearch_package_for_version(mocked_version_number)


@pytest.mark.parametrize("mocked_version_number", UNSUPPORTED_OR_INVALID_VERSIONS)
def test_get_compatible_elasticsearch_package_failure(mocked_version_number):
    """
    Test that the function raises ValueError when server's Elasticsearch version
    is unsupported.
    """
    with mock.patch(
        "common.elasticsearch_compatibility.get_elasticsearch_server_major_version"
    ) as mock_get_server_version:
        mock_get_server_version.return_value = mocked_version_number
        with pytest.raises(ValueError):
            get_compatible_elasticsearch_package()

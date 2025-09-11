import elasticsearch8
import elasticsearch8.helpers
import elasticsearch9
import elasticsearch9.helpers
import requests
from django.conf import settings


def get_elasticsearch_server_major_version() -> int:
    """
    Get the major version of the current Elasticsearch server.

    :return: Major version number as an integer.
    """
    response = requests.get(settings.ES_URI)
    response.raise_for_status()
    return int(response.json()["version"]["number"].split(".")[0])


def get_elasticsearch_package_for_version(elasticsearch_version):
    """
    Get the appropriate elasticsearch package for the given Elasticsearch version.

    :return: elasticsearch package compatible with the given Elasticsearch version
    :raises ValueError: If the Elasticsearch version is unsupported.
    """
    match str(elasticsearch_version):
        case "8":
            return elasticsearch8
        case "9":
            return elasticsearch9
    raise ValueError(
        f"Unsupported Elasticsearch version: {elasticsearch_version}."
        + "Must be 8 or 9."
    )


def get_compatible_elasticsearch_package():
    """
    Get elasticsearch package compatible with current Elasticsearch server.

    :return: The Elasticsearch package compatible with current Elasticsearch server.
    :raises ValueError: If the Elasticsearch version is unsupported.
    """
    es_version = get_elasticsearch_server_major_version()
    return get_elasticsearch_package_for_version(es_version)

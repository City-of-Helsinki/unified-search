from typing import List

from ingest.importers.location.types import TPRUnitResponse
from ingest.importers.utils.traffic import request_json

DEFAULT_TIMEOUT = 20


class LocationImporterAPI:
    tpr_units_endpoint = (
        "https://www.hel.fi/palvelukarttaws/rest/v4/unit/?newfeatures=yes"
    )
    accessibility_shortcoming_counts_endpoint = "https://api.hel.fi/servicemap/v2/unit/?format=json&only=accessibility_shortcoming_count&page_size=1000"  # noqa
    accessibility_viewpoint_endpoint = (
        "https://www.hel.fi/palvelukarttaws/rest/v4/accessibility_viewpoint/"
    )
    accessibility_sentence_endpoint = (
        "https://www.hel.fi/palvelukarttaws/rest/v4/accessibility_sentence/"
    )
    accessibility_shortages_endpoint = (
        "https://www.hel.fi/palvelukarttaws/rest/v4/accessibility_shortage/"
    )
    services_endpoint = "https://www.hel.fi/palvelukarttaws/rest/vpalvelurekisteri/description/?alldata=yes"
    connections_endpoint = "https://www.hel.fi/palvelukarttaws/rest/v4/connection/"

    @classmethod
    def fetch_tpr_units(cls, timeout_seconds=DEFAULT_TIMEOUT) -> TPRUnitResponse:
        return request_json(cls.tpr_units_endpoint, timeout_seconds=timeout_seconds)

    @classmethod
    def fetch_accessibility_shortcoming(cls, url: str, timeout_seconds=DEFAULT_TIMEOUT):
        return request_json(url, timeout_seconds=timeout_seconds)

    @classmethod
    def fetch_unit_ids_and_accessibility_shortcoming_counts(
        cls, timeout_seconds=DEFAULT_TIMEOUT
    ) -> List[dict]:
        """
        Get all unit IDs and their accessibility shortcoming counts
        from new service map API.

        :return: A list of dictionaries each containing unit ID ("id") as integer and
            its accessibility shortcoming counts ("accessibility_shortcoming_count")
            in a dictionary.
        """
        accumulated_results = []
        url = cls.accessibility_shortcoming_counts_endpoint
        while url:
            units = cls.fetch_accessibility_shortcoming(
                url=url, timeout_seconds=timeout_seconds
            )
            accumulated_results += units["results"]
            url = units["next"]
        return accumulated_results

    @classmethod
    def fetch_accessibility_viewpoint(cls, timeout_seconds=DEFAULT_TIMEOUT):
        return request_json(
            cls.accessibility_viewpoint_endpoint, timeout_seconds=timeout_seconds
        )

    @classmethod
    def fetch_accessibility_sentence(cls, timeout_seconds=120):
        return request_json(
            cls.accessibility_sentence_endpoint, timeout_seconds=timeout_seconds
        )

    @classmethod
    def fetch_accessibility_shortages(cls, timeout_seconds=DEFAULT_TIMEOUT):
        return request_json(
            cls.accessibility_shortages_endpoint, timeout_seconds=timeout_seconds
        )

    @classmethod
    def fetch_services(cls, timeout_seconds=120):
        return request_json(cls.services_endpoint, timeout_seconds=timeout_seconds)

    @classmethod
    def fetch_connections(cls, timeout_seconds=DEFAULT_TIMEOUT):
        return request_json(cls.connections_endpoint, timeout_seconds=timeout_seconds)

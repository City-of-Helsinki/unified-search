from typing import List

from ingest.importers.location.types import TPRUnitResponse
from ingest.importers.utils.traffic import request_json

DEFAULT_TIMEOUT = 20

# Department ID of "Kulttuurin ja vapaa-ajan toimiala" (a.k.a. KuVa) i.e.
# "Culture and Leisure Division" in Helsinki. See
# https://www.hel.fi/palvelukarttaws/rest/v4/department/55ed20a5-6a3a-447c-958c-2b537b9e6ee2
CULTURE_AND_LEISURE_DIVISION_DEPARTMENT_ID = "55ed20a5-6a3a-447c-958c-2b537b9e6ee2"


class LocationImporterAPI:
    tpr_units_endpoint = (
        "https://www.hel.fi/palvelukarttaws/rest/v4/unit/?newfeatures=yes"
    )
    # Using department ID for suborganization ID, works although sounds incompatible:
    # https://www.hel.fi/palvelukarttaws/restpages/ver4.html#_filter_units
    culture_and_leisure_division_tpr_units_endpoint = (
        "https://www.hel.fi/palvelukarttaws/rest/v4/unit/?suborganization="
        + CULTURE_AND_LEISURE_DIVISION_DEPARTMENT_ID
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
    linked_events_place_endpoint = (
        "https://api.hel.fi/linkedevents/v1/place/?format=json&page_size=100"
    )

    @classmethod
    def fetch_tpr_units(cls, timeout_seconds=DEFAULT_TIMEOUT) -> TPRUnitResponse:
        return request_json(cls.tpr_units_endpoint, timeout_seconds=timeout_seconds)

    @classmethod
    def fetch_culture_and_leisure_division_tpr_units(
        cls, timeout_seconds=DEFAULT_TIMEOUT
    ) -> TPRUnitResponse:
        return request_json(
            cls.culture_and_leisure_division_tpr_units_endpoint,
            timeout_seconds=timeout_seconds,
        )

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

    @staticmethod
    def get_tpr_unit_id_to_event_count_mapping(places: List[dict]) -> dict[str, int]:
        """
        Get a mapping of TPR unit ID to total event count from a list of Linked Events
        place endpoint data.

        :param places: A list of place data dictionaries from Linked Events
                       place endpoint.
        :return: A dictionary with TPR unit ID ("id") as string without "tprek:"
                 prefix, and its total event count ("event_count").
        """
        result = {}
        for place in places:
            place_id = place["id"]
            if place_id.startswith("tprek:"):
                tpr_unit_id = place_id.split(":")[-1]
                event_count = place["n_events"]
                result[tpr_unit_id] = event_count
        return result

    @classmethod
    def fetch_event_counts_per_tpr_unit(
        cls, timeout_seconds=DEFAULT_TIMEOUT
    ) -> dict[str, int]:
        """
        Get all event counts per TPR unit ID from Linked Events location API.

        :return: A dictionary with TPR unit ID ("id") as string without "tprek:"
                 prefix, and its total event count ("event_count").
        """
        tpr_unit_id_to_event_count = {}
        url = cls.linked_events_place_endpoint
        while url:
            places = request_json(url, timeout_seconds=timeout_seconds)
            tpr_unit_id_to_event_count.update(
                cls.get_tpr_unit_id_to_event_count_mapping(places.get("data", []))
            )
            url = places["meta"]["next"]
        return tpr_unit_id_to_event_count

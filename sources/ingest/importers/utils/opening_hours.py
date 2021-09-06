from dataclasses import dataclass, field
from datetime import date, time, timedelta
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Union
from urllib.parse import urlencode

from django.utils.timezone import localdate
from humps import camelize
from requests import RequestException

from .shared import LinkedData
from .traffic import request_json

DEFAULT_BATCH_SIZE = 100
# TODO make configurable
HAUKI_BASE_URL = "https://hauki.api.hel.fi/v1/"

HAUKI_RESOURCE_URL = HAUKI_BASE_URL + "resource/tprek:{venue_id}/"
HAUKI_OPENING_HOURS_URL = HAUKI_BASE_URL + "opening_hours/"


@dataclass
class OpeningHoursTimes:
    startTime: time
    endTime: time
    endTimeOnNextDay: bool
    resourceState: str
    fullDay: bool


@dataclass
class OpeningHoursDay:
    date: date
    times: List[OpeningHoursTimes]


@dataclass
class OpeningHours:
    url: str
    is_open_now_url: str
    data: List[OpeningHoursDay] = field(default_factory=list)


RawHours = List[dict]
RawHoursById = Dict[str, RawHours]


class HaukiOpeningHoursFetcher:
    """Fetches venue opening hours from Hauki in batches.

    Usage:

    1) Instantiate the class with all the venues IDs opening hours will be needed for
    2) call get_opening_hours_and_link(venue_id) for every venue

    For the batch importing to work optimally, the order of the method calls should
    match the order of the ID list.

    If opening hours for a venue cannot be fetched from Hauki, the returned link object
    will be None, but the returned OpeningHours object is still usable.

    Example:

    fetcher = HaukiOpeningHoursFetcher(venue["id"] for venue in venues)
    for venue in venues:
        opening_hours, link = fetcher(venue["id"])
        print(f"Hauki URL: {opening_hours.url}")  # OpeningHours obj always returned
        if not link:
            print("Could not fetch opening hours from Hauki.")
    """

    def __init__(
        self,
        all_venue_ids: Iterable[Union[str, int]],
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        self.batch_size = batch_size
        self.all_venue_ids: Tuple[str] = tuple(str(i) for i in all_venue_ids)
        self.data: RawHoursById = {}

    def get_opening_hours_and_link(
        self, venue_id: Union[str, int]
    ) -> Tuple[OpeningHours, Optional[LinkedData]]:
        venue_id = str(venue_id)
        hauki_resource_url = HAUKI_RESOURCE_URL.format(venue_id=venue_id)

        opening_hours = OpeningHours(
            url=f"{hauki_resource_url}opening_hours/",
            is_open_now_url=f"{hauki_resource_url}is_open_now/",
        )

        try:
            data = self.get_opening_hours_for_venue(venue_id)
        except RequestException:
            return opening_hours, None

        opening_hours.data = camelize(data)
        opening_hours_link = LinkedData(
            service="hauki",
            origin_url=opening_hours.url,
            raw_data=data,
        )

        return opening_hours, opening_hours_link

    def get_opening_hours_for_venue(self, venue_id: str) -> RawHours:
        if venue_id not in self.data:
            self.data = self.fetch_next_batch(venue_id)
        return self.data[venue_id]

    def fetch_next_batch(self, start_venue_id: str) -> RawHoursById:
        try:
            index = self.all_venue_ids.index(start_venue_id)
        except ValueError:
            # Something abnormal going on: The given ID cannot be found in the all IDs
            # list, so cannot fetch a batch. Fetch just this one as a fallback and add
            # the ID to the list.
            ids_to_fetch = [start_venue_id]
            self.all_venue_ids += ("start_venue_id",)
        else:
            ids_to_fetch = self.all_venue_ids[index : index + self.batch_size]
        return self.fetch(ids_to_fetch)

    def fetch(self, ids: Sequence[str]) -> RawHoursById:
        today = localdate()
        tomorrow = today + timedelta(days=1)
        prefixed_ids = (f"tprek:{i}" for i in ids)
        params = {
            "start_date": today,
            "end_date": tomorrow,
            "resource": ",".join(prefixed_ids),
        }
        url = f"{HAUKI_OPENING_HOURS_URL}?{urlencode(params)}"
        response = request_json(url)

        result_map = {}
        for result in response["results"]:
            origin_id = self.get_tprek_origin_id(result)
            if origin_id:
                result_map[origin_id] = result["opening_hours"]

        return {i: result_map.get(i, []) for i in ids}

    @staticmethod
    def get_tprek_origin_id(data: dict) -> Optional[str]:
        return next(
            (
                o
                for o in data["resource"]["origins"]
                if o["data_source"]["id"] == "tprek"
            ),
            {},
        ).get("origin_id")

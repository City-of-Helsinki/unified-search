from copy import copy
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Union
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

from django.utils.timezone import localdate, make_aware
from humps import camelize
from requests import RequestException

from .shared import LinkedData
from .traffic import request_json

DEFAULT_BATCH_SIZE = 100
# TODO make configurable
HAUKI_BASE_URL = "https://hauki.api.hel.fi/v1/"
NUMBER_OF_DAYS_TO_FETCH = 7
DEFAULT_TIME_ZONE = "Europe/Helsinki"

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
class OpeningHoursTimesRange:
    gte: str
    lt: str


@dataclass
class OpeningHours:
    url: str
    is_open_now_url: str
    data: List[OpeningHoursDay] = field(default_factory=list)
    openRanges: List[OpeningHoursTimesRange] = field(default_factory=list)


@dataclass
class DateTimeRange:
    """Helper dataclass for manipulating datetime ranges to build opening hours times ranges."""  # noqa

    start: datetime
    end: datetime

    def as_opening_hours_times_range(self) -> OpeningHoursTimesRange:
        return OpeningHoursTimesRange(
            gte=self.start.isoformat(), lt=self.end.isoformat()
        )


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

        opening_hours.openRanges = self.get_open_ranges(data)
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
        end_date = today + timedelta(days=NUMBER_OF_DAYS_TO_FETCH)
        prefixed_ids = (f"tprek:{i}" for i in ids)
        params = {
            "start_date": today,
            "end_date": end_date,
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

    def get_open_ranges(self, data: RawHours) -> List[OpeningHoursTimesRange]:
        """Get datetime ranges when the venue is open."""

        open_ranges: List[DateTimeRange] = []
        closed_ranges: List[DateTimeRange] = []

        for day_data in data:
            day = datetime.date(datetime.strptime(day_data["date"], "%Y-%m-%d"))

            for time_data in day_data["times"]:
                # Skip other states than "open" and "closed" at least for now
                if time_data["resource_state"] not in ("open", "closed"):
                    continue

                # If the data is not for full day, require both the start time and the
                # end time
                if not (
                    time_data["full_day"]
                    or (
                        time_data["start_time"]
                        and time_data["end_time"]
                        and time_data["start_time"] != time_data["end_time"]
                    )
                ):
                    continue

                if time_data["full_day"]:
                    start_time = end_time = "00:00:00"
                    end_time_on_next_day = True
                else:
                    start_time = time_data["start_time"]
                    end_time = time_data["end_time"]
                    end_time_on_next_day = time_data["end_time_on_next_day"]

                range_list = (
                    open_ranges
                    if time_data["resource_state"] == "open"
                    else closed_ranges
                )
                range_list.append(
                    DateTimeRange(
                        start=self.get_datetime_from_date_and_time(day, start_time),
                        end=self.get_datetime_from_date_and_time(
                            day + timedelta(days=1) if end_time_on_next_day else day,
                            end_time,
                        ),
                    )
                )

        # Override times when open by times when closed
        open_ranges = self.datetime_range_list_difference(open_ranges, closed_ranges)

        return [r.as_opening_hours_times_range() for r in open_ranges]

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

    @staticmethod
    def get_datetime_from_date_and_time(day, dt):
        return make_aware(
            datetime.combine(day, datetime.strptime(dt, "%H:%M:%S").time()),
            timezone=ZoneInfo(DEFAULT_TIME_ZONE),
        )

    @staticmethod
    def datetime_range_list_difference(
        minuend_ranges: List[DateTimeRange],
        subtrahend_ranges: List[DateTimeRange],
    ) -> List[DateTimeRange]:
        """Subtract a datetime range list from a datetime range list."""

        # Loop over the subtrahend ranges and subtract each of them from all of the
        # minuend ranges. NOTE: the minuend ranges list is (possibly) updated between
        # subtrahend ranges.
        for subtrahend_range in subtrahend_ranges:
            minuend_ranges = sum(
                (
                    HaukiOpeningHoursFetcher.datetime_range_difference(
                        minuend_range, subtrahend_range
                    )
                    for minuend_range in minuend_ranges
                ),
                [],
            )
        return minuend_ranges

    @staticmethod
    def datetime_range_difference(
        minuend: DateTimeRange, subtrahend: DateTimeRange
    ) -> List[DateTimeRange]:
        """Subtract a datetime range from a datetime range."""

        if subtrahend.start <= minuend.start and subtrahend.end >= minuend.end:
            # subtrahend covers minuend completely
            #  mmmm
            # ssssss
            return []
        elif subtrahend.end <= minuend.start or subtrahend.start >= minuend.end:
            # subtrahend completely outside minuend
            # mmmmmm
            #        ssssss
            return [copy(minuend)]
        elif subtrahend.start > minuend.start and subtrahend.end < minuend.end:
            # subtrahend in the middle of minuend, the result is two ranges
            # mmmmmm
            #  ssss
            return [
                DateTimeRange(start=minuend.start, end=subtrahend.start),
                DateTimeRange(start=subtrahend.end, end=minuend.end),
            ]
        else:
            # here we have only two possibilities left
            if subtrahend.start <= minuend.start:
                #    mmmmmm
                # ssssss
                return [DateTimeRange(start=subtrahend.end, end=minuend.end)]
            else:
                # mmmmmm
                #    ssssss
                return [DateTimeRange(start=minuend.start, end=subtrahend.start)]

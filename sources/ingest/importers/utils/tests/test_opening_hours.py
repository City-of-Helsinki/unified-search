import datetime
from dataclasses import asdict

import pytest

from .. import HaukiOpeningHoursFetcher
from ..opening_hours import DateTimeRange

MOCK_RESPONSE = {
    "count": 5,
    "next": None,
    "previous": None,
    "results": [
        {
            "resource": {
                "id": 11,
                "name": {
                    "fi": "Leikkipuisto Kannelmäki",
                    "sv": "Lekparken Kannelmäki",
                    "en": "Playground Kannelmäki",
                },
                "timezone": "Europe/Helsinki",
                "origins": [
                    {
                        "data_source": {
                            "id": "tprek",
                            "name": {"fi": None, "sv": None, "en": None},
                        },
                        "origin_id": "1",
                    }
                ],
            },
            "opening_hours": [
                {
                    "date": "2021-09-03",
                    "times": [
                        {
                            "name": "",
                            "description": "",
                            "start_time": "11:00:00",
                            "end_time": "18:00:00",
                            "end_time_on_next_day": False,
                            "resource_state": "open",
                            "full_day": False,
                            "periods": [1267],
                        }
                    ],
                }
            ],
        },
        {
            "resource": {
                "id": 22,
                "name": {
                    "fi": "Leikkipuisto Kaunokki",
                    "sv": "Lekparken Kaunokki",
                    "en": "Playground Kaunokki",
                },
                "timezone": "Europe/Helsinki",
                "origins": [
                    {
                        "data_source": {
                            "id": "tprek",
                            "name": {"fi": None, "sv": None, "en": None},
                        },
                        "origin_id": "4",
                    }
                ],
            },
            "opening_hours": [
                {
                    "date": "2021-09-03",
                    "times": [
                        {
                            "name": "",
                            "description": "",
                            "start_time": "09:00:00",
                            "end_time": "16:00:00",
                            "end_time_on_next_day": False,
                            "resource_state": "open",
                            "full_day": False,
                            "periods": [1306],
                        }
                    ],
                },
                {
                    "date": "2021-09-03",
                    "times": [
                        {
                            "name": "",
                            "description": "",
                            "start_time": "10:00:00",
                            "end_time": "11:00:00",
                            "end_time_on_next_day": False,
                            "resource_state": "closed",
                            "full_day": False,
                            "periods": [1306],
                        }
                    ],
                },
                {
                    "date": "2021-09-04",
                    "times": [
                        {
                            "name": "",
                            "description": "",
                            "start_time": None,
                            "end_time": None,
                            "end_time_on_next_day": False,
                            "resource_state": "open",
                            "full_day": True,
                            "periods": [1306],
                        }
                    ],
                },
                {
                    "date": "2021-09-05",
                    "times": [
                        {
                            "name": "",
                            "description": "",
                            "start_time": None,
                            "end_time": None,
                            "end_time_on_next_day": False,
                            "resource_state": "closed",
                            "full_day": True,
                            "periods": [1306],
                        }
                    ],
                },
                {
                    "date": "2021-09-06",
                    "times": [
                        {
                            "name": "",
                            "description": "",
                            "start_time": "09:00:00",
                            "end_time": "05:00:00",
                            "end_time_on_next_day": True,
                            "resource_state": "open",
                            "full_day": False,
                            "periods": [1306],
                        }
                    ],
                },
            ],
        },
    ],
}


@pytest.fixture()
def patched_request_json(mocker):
    return mocker.patch(
        "ingest.importers.utils.opening_hours.request_json", return_value=MOCK_RESPONSE
    )


def test_opening_hours_fetcher_data(patched_request_json, snapshot):
    ids = tuple(range(1, 5))
    fetcher = HaukiOpeningHoursFetcher(ids, batch_size=2)

    for i in ids:
        opening_hours, link = fetcher.get_opening_hours_and_link(i)

        snapshot.assert_match(asdict(opening_hours), f"opening_hours {i}")
        snapshot.assert_match(asdict(link), f"link {i}")


@pytest.mark.parametrize(
    "batch_size, expected_request_count",
    (
        (1, 4),
        (2, 2),
        (3, 2),
        (4, 1),
    ),
)
def test_opening_hours_fetcher_request_number(
    patched_request_json, batch_size, expected_request_count
):
    ids = tuple(range(1, 5))
    fetcher = HaukiOpeningHoursFetcher(ids, batch_size=batch_size)

    for i in ids:
        fetcher.get_opening_hours_and_link(i)

    assert patched_request_json.call_count == expected_request_count


# use just seconds instead of complete datetimes to make these tests just 4/5 cryptic
def get_datetime_range_from_seconds(sec_1, sec_2):
    return DateTimeRange(
        start=datetime.datetime(2021, 9, 21, 12, 00, sec_1),
        end=datetime.datetime(2021, 9, 21, 12, 00, sec_2),
    )


@pytest.mark.parametrize(
    "open_range, closed_range, expected_result",
    (
        ((4, 7), (1, 3), [(4, 7)]),
        ((4, 7), (1, 4), [(4, 7)]),
        ((4, 7), (1, 6), [(6, 7)]),
        ((4, 7), (4, 6), [(6, 7)]),
        ((4, 7), (5, 6), [(4, 5), (6, 7)]),
        ((4, 7), (5, 7), [(4, 5)]),
        ((4, 7), (5, 8), [(4, 5)]),
        ((4, 7), (7, 8), [(4, 7)]),
        ((4, 7), (8, 9), [(4, 7)]),
        ((4, 7), (4, 7), []),
        ((4, 7), (3, 7), []),
        ((4, 7), (4, 8), []),
    ),
)
def test_datetime_range_difference(open_range, closed_range, expected_result):
    open_range = get_datetime_range_from_seconds(*open_range)
    closed_range = get_datetime_range_from_seconds(*closed_range)

    result_list = HaukiOpeningHoursFetcher.datetime_range_difference(
        open_range, closed_range
    )

    assert [(r.start.second, r.end.second) for r in result_list] == expected_result


@pytest.mark.parametrize(
    "open_ranges, closed_ranges, expected_result",
    (
        ([], [(4, 8)], []),
        ([(2, 4), (6, 8)], [(1, 2), (4, 6), (8, 9)], [(2, 4), (6, 8)]),
        ([(3, 5), (7, 9)], [(4, 8)], [(3, 4), (8, 9)]),
        ([(2, 8)], [(2, 3), (5, 6)], [(3, 5), (6, 8)]),
        ([(3, 5)], [(7, 8), (4, 8)], [(3, 4)]),
        ([(3, 5)], [(7, 8), (3, 8)], []),
    ),
)
def test_datetime_range_list_difference(open_ranges, closed_ranges, expected_result):
    open_ranges = [get_datetime_range_from_seconds(*r) for r in open_ranges]
    closed_ranges = [get_datetime_range_from_seconds(*r) for r in closed_ranges]

    result_list = HaukiOpeningHoursFetcher.datetime_range_list_difference(
        open_ranges, closed_ranges
    )

    assert [(r.start.second, r.end.second) for r in result_list] == expected_result

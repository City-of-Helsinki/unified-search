from dataclasses import asdict

import pytest

from .. import HaukiOpeningHoursFetcher

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
                }
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

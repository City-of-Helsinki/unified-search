# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_opening_hours_fetcher_data link 1'] = {
    'origin_url': 'https://hauki.api.hel.fi/v1/resource/tprek:1/opening_hours/',
    'raw_data': [
        {
            'date': '2021-09-03',
            'times': [
                {
                    'description': '',
                    'end_time': '18:00:00',
                    'end_time_on_next_day': False,
                    'full_day': False,
                    'name': '',
                    'periods': [
                        1267
                    ],
                    'resource_state': 'open',
                    'start_time': '11:00:00'
                }
            ]
        }
    ],
    'service': 'hauki'
}

snapshots['test_opening_hours_fetcher_data link 2'] = {
    'origin_url': 'https://hauki.api.hel.fi/v1/resource/tprek:2/opening_hours/',
    'raw_data': [
    ],
    'service': 'hauki'
}

snapshots['test_opening_hours_fetcher_data link 3'] = {
    'origin_url': 'https://hauki.api.hel.fi/v1/resource/tprek:3/opening_hours/',
    'raw_data': [
    ],
    'service': 'hauki'
}

snapshots['test_opening_hours_fetcher_data link 4'] = {
    'origin_url': 'https://hauki.api.hel.fi/v1/resource/tprek:4/opening_hours/',
    'raw_data': [
        {
            'date': '2021-09-03',
            'times': [
                {
                    'description': '',
                    'end_time': '16:00:00',
                    'end_time_on_next_day': False,
                    'full_day': False,
                    'name': '',
                    'periods': [
                        1306
                    ],
                    'resource_state': 'open',
                    'start_time': '09:00:00'
                }
            ]
        },
        {
            'date': '2021-09-03',
            'times': [
                {
                    'description': '',
                    'end_time': '11:00:00',
                    'end_time_on_next_day': False,
                    'full_day': False,
                    'name': '',
                    'periods': [
                        1306
                    ],
                    'resource_state': 'closed',
                    'start_time': '10:00:00'
                }
            ]
        },
        {
            'date': '2021-09-04',
            'times': [
                {
                    'description': '',
                    'end_time': None,
                    'end_time_on_next_day': False,
                    'full_day': True,
                    'name': '',
                    'periods': [
                        1306
                    ],
                    'resource_state': 'open',
                    'start_time': None
                }
            ]
        },
        {
            'date': '2021-09-05',
            'times': [
                {
                    'description': '',
                    'end_time': None,
                    'end_time_on_next_day': False,
                    'full_day': True,
                    'name': '',
                    'periods': [
                        1306
                    ],
                    'resource_state': 'closed',
                    'start_time': None
                }
            ]
        },
        {
            'date': '2021-09-06',
            'times': [
                {
                    'description': '',
                    'end_time': '05:00:00',
                    'end_time_on_next_day': True,
                    'full_day': False,
                    'name': '',
                    'periods': [
                        1306
                    ],
                    'resource_state': 'open',
                    'start_time': '09:00:00'
                }
            ]
        }
    ],
    'service': 'hauki'
}

snapshots['test_opening_hours_fetcher_data opening_hours 1'] = {
    'data': [
        {
            'date': '2021-09-03',
            'times': [
                {
                    'description': '',
                    'endTime': '18:00:00',
                    'endTimeOnNextDay': False,
                    'fullDay': False,
                    'name': '',
                    'periods': [
                        1267
                    ],
                    'resourceState': 'open',
                    'startTime': '11:00:00'
                }
            ]
        }
    ],
    'is_open_now_url': 'https://hauki.api.hel.fi/v1/resource/tprek:1/is_open_now/',
    'openRanges': [
        {
            'gte': '2021-09-03T11:00:00+03:00',
            'lt': '2021-09-03T18:00:00+03:00'
        }
    ],
    'url': 'https://hauki.api.hel.fi/v1/resource/tprek:1/opening_hours/'
}

snapshots['test_opening_hours_fetcher_data opening_hours 2'] = {
    'data': [
    ],
    'is_open_now_url': 'https://hauki.api.hel.fi/v1/resource/tprek:2/is_open_now/',
    'openRanges': [
    ],
    'url': 'https://hauki.api.hel.fi/v1/resource/tprek:2/opening_hours/'
}

snapshots['test_opening_hours_fetcher_data opening_hours 3'] = {
    'data': [
    ],
    'is_open_now_url': 'https://hauki.api.hel.fi/v1/resource/tprek:3/is_open_now/',
    'openRanges': [
    ],
    'url': 'https://hauki.api.hel.fi/v1/resource/tprek:3/opening_hours/'
}

snapshots['test_opening_hours_fetcher_data opening_hours 4'] = {
    'data': [
        {
            'date': '2021-09-03',
            'times': [
                {
                    'description': '',
                    'endTime': '16:00:00',
                    'endTimeOnNextDay': False,
                    'fullDay': False,
                    'name': '',
                    'periods': [
                        1306
                    ],
                    'resourceState': 'open',
                    'startTime': '09:00:00'
                }
            ]
        },
        {
            'date': '2021-09-03',
            'times': [
                {
                    'description': '',
                    'endTime': '11:00:00',
                    'endTimeOnNextDay': False,
                    'fullDay': False,
                    'name': '',
                    'periods': [
                        1306
                    ],
                    'resourceState': 'closed',
                    'startTime': '10:00:00'
                }
            ]
        },
        {
            'date': '2021-09-04',
            'times': [
                {
                    'description': '',
                    'endTime': None,
                    'endTimeOnNextDay': False,
                    'fullDay': True,
                    'name': '',
                    'periods': [
                        1306
                    ],
                    'resourceState': 'open',
                    'startTime': None
                }
            ]
        },
        {
            'date': '2021-09-05',
            'times': [
                {
                    'description': '',
                    'endTime': None,
                    'endTimeOnNextDay': False,
                    'fullDay': True,
                    'name': '',
                    'periods': [
                        1306
                    ],
                    'resourceState': 'closed',
                    'startTime': None
                }
            ]
        },
        {
            'date': '2021-09-06',
            'times': [
                {
                    'description': '',
                    'endTime': '05:00:00',
                    'endTimeOnNextDay': True,
                    'fullDay': False,
                    'name': '',
                    'periods': [
                        1306
                    ],
                    'resourceState': 'open',
                    'startTime': '09:00:00'
                }
            ]
        }
    ],
    'is_open_now_url': 'https://hauki.api.hel.fi/v1/resource/tprek:4/is_open_now/',
    'openRanges': [
        {
            'gte': '2021-09-03T09:00:00+03:00',
            'lt': '2021-09-03T10:00:00+03:00'
        },
        {
            'gte': '2021-09-03T11:00:00+03:00',
            'lt': '2021-09-03T16:00:00+03:00'
        },
        {
            'gte': '2021-09-04T00:00:00+03:00',
            'lt': '2021-09-05T00:00:00+03:00'
        },
        {
            'gte': '2021-09-06T09:00:00+03:00',
            'lt': '2021-09-07T05:00:00+03:00'
        }
    ],
    'url': 'https://hauki.api.hel.fi/v1/resource/tprek:4/opening_hours/'
}

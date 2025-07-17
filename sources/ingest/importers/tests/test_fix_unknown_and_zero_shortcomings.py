from typing import List

import pytest

from ingest.importers.location.constants import NO_SHORTCOMINGS_SHORTAGE_TEXT_VARIANTS
from ingest.importers.location.dataclasses import (
    Accessibility,
    AccessibilityShortcoming,
    AccessibilityViewpoint,
)
from ingest.importers.location.dataclasses import (
    AccessibilityViewpointID as VpID,
)
from ingest.importers.location.enums import AccessibilityViewpointValue
from ingest.importers.utils.shared import LanguageString

SHORTAGE_1, SHORTAGE_2, SHORTAGE_3 = [
    LanguageString(fi=f"Puute {i}", sv=f"Brist {i}", en=f"Shortage {i}")
    for i in [1, 2, 3]
]
SHORTAGES_1_2 = [SHORTAGE_1, SHORTAGE_2]
SHORTAGES_1_2_3 = [SHORTAGE_1, SHORTAGE_2, SHORTAGE_3]


ALL_GREEN_SHORTCOMINGS = [
    AccessibilityShortcoming(profile="hearing_aid", count=0),
    AccessibilityShortcoming(profile="reduced_mobility", count=0),
    AccessibilityShortcoming(profile="rollator", count=0),
    AccessibilityShortcoming(profile="stroller", count=0),
    AccessibilityShortcoming(profile="visually_impaired", count=0),
    AccessibilityShortcoming(profile="wheelchair", count=0),
]

ALL_UNKNOWN_SHORTCOMINGS = [
    AccessibilityShortcoming(profile="hearing_aid", count=None),
    AccessibilityShortcoming(profile="reduced_mobility", count=None),
    AccessibilityShortcoming(profile="rollator", count=None),
    AccessibilityShortcoming(profile="stroller", count=None),
    AccessibilityShortcoming(profile="visually_impaired", count=None),
    AccessibilityShortcoming(profile="wheelchair", count=None),
]

TEST_VIEWPOINT_NAME = LanguageString(fi="Testi", sv="Test", en="Test")


def _green(viewpoint_id: VpID) -> AccessibilityViewpoint:
    """
    Create an AccessibilityViewpoint with "green" value
    """
    return AccessibilityViewpoint(
        id=viewpoint_id.value,
        value=AccessibilityViewpointValue.GREEN.value,
        name=TEST_VIEWPOINT_NAME,
        shortages=NO_SHORTCOMINGS_SHORTAGE_TEXT_VARIANTS,
    )


def _unknown(viewpoint_id: VpID) -> AccessibilityViewpoint:
    """
    Create an AccessibilityViewpoint with "unknown" value
    """
    return AccessibilityViewpoint(
        id=viewpoint_id.value,
        value=AccessibilityViewpointValue.UNKNOWN.value,
        name=TEST_VIEWPOINT_NAME,
        shortages=[],
    )


def _red(viewpoint_id: VpID, *shortages: LanguageString) -> AccessibilityViewpoint:
    """
    Create an AccessibilityViewpoint with "red" value and given shortages
    """
    return AccessibilityViewpoint(
        id=viewpoint_id.value,
        value=AccessibilityViewpointValue.RED.value,
        name=TEST_VIEWPOINT_NAME,
        shortages=[*shortages],
    )


ALL_GREEN_VIEWPOINTS = [_green(viewpoint_id) for viewpoint_id in VpID]
ALL_UNKNOWN_VIEWPOINTS = [_unknown(viewpoint_id) for viewpoint_id in VpID]
ALL_RED_VIEWPOINTS_WITH_SHORTAGES = [
    _red(viewpoint_id, *SHORTAGES_1_2_3) for viewpoint_id in VpID
]
ALL_RED_VIEWPOINTS_WITHOUT_SHORTAGES = [_red(viewpoint_id) for viewpoint_id in VpID]


def make_test_accessibility(
    viewpoints: List[AccessibilityViewpoint],
    shortcomings: List[AccessibilityShortcoming],
) -> Accessibility:
    """
    Create a test Accessibility object with given viewpoints and shortcomings
    """
    return Accessibility(
        email="test_email",
        phone="test_phone",
        www="test_www",
        viewpoints=viewpoints,
        sentences=[],
        shortcomings=shortcomings,
    )


def test_shortages_not_set_raises_error():
    accessibility = make_test_accessibility(
        viewpoints=[
            AccessibilityViewpoint(
                id=VpID.WHEELCHAIR.value,
                value=AccessibilityViewpointValue.RED.value,
                name=TEST_VIEWPOINT_NAME,
                shortages=None,
            )
        ],
        shortcomings=[],
    )
    with pytest.raises(ValueError):
        accessibility.fix_unknown_and_zero_shortcomings()


@pytest.mark.parametrize(
    "viewpoint_value",
    [
        AccessibilityViewpointValue.RED,
        AccessibilityViewpointValue.GREEN,
        AccessibilityViewpointValue.UNKNOWN,
    ],
)
@pytest.mark.parametrize(
    "shortages",
    [[], NO_SHORTCOMINGS_SHORTAGE_TEXT_VARIANTS, [SHORTAGE_1], SHORTAGES_1_2_3],
)
def test_choose_accessibility_perspective_viewpoint_is_ignored(
    viewpoint_value: AccessibilityViewpointValue,
    shortages: List[LanguageString],
):
    accessibility = make_test_accessibility(
        viewpoints=[
            AccessibilityViewpoint(
                id=VpID.CHOOSE_ACCESSIBILITY_PERSPECTIVE.value,
                value=viewpoint_value.value,
                name=TEST_VIEWPOINT_NAME,
                shortages=shortages,
            )
        ],
        shortcomings=[],
    )
    assert accessibility.fix_unknown_and_zero_shortcomings()
    assert accessibility.shortcomings == ALL_UNKNOWN_SHORTCOMINGS


def test_no_data():
    accessibility = make_test_accessibility(viewpoints=[], shortcomings=[])
    assert accessibility.fix_unknown_and_zero_shortcomings()
    assert accessibility.shortcomings == ALL_UNKNOWN_SHORTCOMINGS


def test_all_unknown():
    accessibility = make_test_accessibility(
        viewpoints=ALL_UNKNOWN_VIEWPOINTS, shortcomings=[]
    )
    assert accessibility.fix_unknown_and_zero_shortcomings()
    assert accessibility.shortcomings == ALL_UNKNOWN_SHORTCOMINGS


def test_all_green():
    accessibility = make_test_accessibility(
        viewpoints=ALL_GREEN_VIEWPOINTS, shortcomings=[]
    )
    assert accessibility.fix_unknown_and_zero_shortcomings()
    assert accessibility.shortcomings == ALL_GREEN_SHORTCOMINGS


def test_partial_green_only():
    accessibility = make_test_accessibility(
        viewpoints=[
            _green(VpID.REDUCED_MOBILITY_ARRIVE_BY_OWN_CAR),
            _green(VpID.ROLLATOR_ARRIVE_BY_OWN_CAR),
            _green(VpID.ROLLATOR_ARRIVE_BY_DROPOFF),
            _green(VpID.VISUALLY_IMPAIRED),
            _green(VpID.WHEELCHAIR),
            _green(VpID.WHEELCHAIR_ARRIVE_BY_OWN_CAR),
        ],
        shortcomings=[],
    )
    assert accessibility.fix_unknown_and_zero_shortcomings()
    assert accessibility.shortcomings == ALL_UNKNOWN_SHORTCOMINGS


@pytest.mark.parametrize(
    "viewpoints",
    [
        ALL_GREEN_VIEWPOINTS,
        ALL_UNKNOWN_VIEWPOINTS,
        ALL_RED_VIEWPOINTS_WITH_SHORTAGES,
        ALL_RED_VIEWPOINTS_WITHOUT_SHORTAGES,
    ],
)
def test_nothing_happens_when_all_already_red(viewpoints: List[AccessibilityViewpoint]):
    orig_shortcomings = [
        AccessibilityShortcoming(profile="hearing_aid", count=1),
        AccessibilityShortcoming(profile="reduced_mobility", count=2),
        AccessibilityShortcoming(profile="rollator", count=3),
        AccessibilityShortcoming(profile="stroller", count=4),
        AccessibilityShortcoming(profile="visually_impaired", count=5),
        AccessibilityShortcoming(profile="wheelchair", count=6),
    ]
    accessibility = make_test_accessibility(
        viewpoints=viewpoints, shortcomings=orig_shortcomings[:]
    )
    assert not accessibility.fix_unknown_and_zero_shortcomings()
    assert len(accessibility.shortcomings) == len(orig_shortcomings)
    assert all(
        sc1 == sc2 for sc1, sc2 in zip(accessibility.shortcomings, orig_shortcomings)
    )


def test_unknown_to_red_unique_shortages_count():
    accessibility = make_test_accessibility(
        viewpoints=[
            _red(VpID.HEARING_AID, *SHORTAGES_1_2),
            _red(VpID.ROLLATOR, SHORTAGE_1),
            _red(VpID.ROLLATOR_ARRIVE_BY_OWN_CAR, SHORTAGE_2),
            _red(VpID.ROLLATOR_ARRIVE_BY_DROPOFF, SHORTAGE_3),
            _red(VpID.VISUALLY_IMPAIRED, SHORTAGE_1),
            _red(VpID.VISUALLY_IMPAIRED_ARRIVE_BY_DROPOFF, SHORTAGE_2),
            _red(VpID.WHEELCHAIR, *SHORTAGES_1_2_3),
            _red(VpID.WHEELCHAIR_ARRIVE_BY_OWN_CAR, SHORTAGE_2),
            _red(VpID.WHEELCHAIR_ARRIVE_BY_DROPOFF, SHORTAGE_3),
        ],
        shortcomings=[],
    )
    assert accessibility.fix_unknown_and_zero_shortcomings()
    assert accessibility.shortcomings == [
        AccessibilityShortcoming(profile="hearing_aid", count=2),
        AccessibilityShortcoming(profile="reduced_mobility", count=None),
        AccessibilityShortcoming(profile="rollator", count=3),
        AccessibilityShortcoming(profile="stroller", count=None),
        AccessibilityShortcoming(profile="visually_impaired", count=2),
        AccessibilityShortcoming(profile="wheelchair", count=3),
    ]


def test_all_red_but_no_shortages_means_unknown():
    accessibility = make_test_accessibility(
        viewpoints=ALL_RED_VIEWPOINTS_WITHOUT_SHORTAGES,
        shortcomings=[],
    )
    assert accessibility.fix_unknown_and_zero_shortcomings()
    assert accessibility.shortcomings == ALL_UNKNOWN_SHORTCOMINGS


def test_all_or_partial_red_but_no_real_shortages_means_unknown():
    accessibility = make_test_accessibility(
        viewpoints=[
            # Hearing aid -> unknown
            # - profile with a single viewpoint
            # - red but no real shortages i.e. only texts meaning "no shortages"
            _red(VpID.HEARING_AID, *NO_SHORTCOMINGS_SHORTAGE_TEXT_VARIANTS),
            # Reduced mobility -> unknown
            # - profile with 3 viewpoints
            # - no unknowns
            # - reds but no shortages
            _red(VpID.REDUCED_MOBILITY),
            _red(VpID.REDUCED_MOBILITY_ARRIVE_BY_OWN_CAR),
            _green(VpID.REDUCED_MOBILITY_ARRIVE_BY_DROPOFF),
            # Rollator -> unknown
            # - profile with 3 viewpoints
            # - no unknowns
            # - reds but shortages
            _green(VpID.ROLLATOR),
            _red(VpID.ROLLATOR_ARRIVE_BY_OWN_CAR),
            _red(VpID.ROLLATOR_ARRIVE_BY_DROPOFF),
            # Stroller -> unknown
            # - profile with a single viewpoint
            # - red but no shortages
            _red(VpID.STROLLER),
            # Visually impaired -> unknown
            # - profile with 2 viewpoints
            # - no unknowns
            # - red but no shortages
            _green(VpID.VISUALLY_IMPAIRED),
            _red(VpID.VISUALLY_IMPAIRED_ARRIVE_BY_DROPOFF),
            # Wheelchair -> unknown
            # - profile with 3 viewpoints
            # - no unknowns
            # - reds but no shortages
            _green(VpID.WHEELCHAIR),
            _red(VpID.WHEELCHAIR_ARRIVE_BY_OWN_CAR),
            _red(VpID.WHEELCHAIR_ARRIVE_BY_DROPOFF),
        ],
        shortcomings=[
            AccessibilityShortcoming(profile="reduced_mobility", count=None),
            AccessibilityShortcoming(profile="rollator", count=0),
        ],
    )
    assert accessibility.fix_unknown_and_zero_shortcomings()
    assert accessibility.shortcomings == ALL_UNKNOWN_SHORTCOMINGS


def test_unknown_to_green_single_viewpoint_in_profile():
    accessibility = make_test_accessibility(
        viewpoints=[_green(VpID.STROLLER)], shortcomings=[]
    )
    assert accessibility.fix_unknown_and_zero_shortcomings()
    assert accessibility.shortcomings == [
        AccessibilityShortcoming(profile="hearing_aid", count=None),
        AccessibilityShortcoming(profile="reduced_mobility", count=None),
        AccessibilityShortcoming(profile="rollator", count=None),
        AccessibilityShortcoming(profile="stroller", count=0),
        AccessibilityShortcoming(profile="visually_impaired", count=None),
        AccessibilityShortcoming(profile="wheelchair", count=None),
    ]


def test_unknown_to_green_multiple_viewpoints_in_profile():
    accessibility = make_test_accessibility(
        viewpoints=[
            _green(VpID.WHEELCHAIR),
            _green(VpID.WHEELCHAIR_ARRIVE_BY_OWN_CAR),
            _green(VpID.WHEELCHAIR_ARRIVE_BY_DROPOFF),
        ],
        shortcomings=[],
    )
    assert accessibility.fix_unknown_and_zero_shortcomings()
    assert accessibility.shortcomings == [
        AccessibilityShortcoming(profile="hearing_aid", count=None),
        AccessibilityShortcoming(profile="reduced_mobility", count=None),
        AccessibilityShortcoming(profile="rollator", count=None),
        AccessibilityShortcoming(profile="stroller", count=None),
        AccessibilityShortcoming(profile="visually_impaired", count=None),
        AccessibilityShortcoming(profile="wheelchair", count=0),
    ]


def test_unknown_to_unknown_partial_coverage_of_multiple_viewpoints_in_profile():
    accessibility = make_test_accessibility(
        viewpoints=[
            _green(VpID.REDUCED_MOBILITY),
            _green(VpID.REDUCED_MOBILITY_ARRIVE_BY_DROPOFF),
            _green(VpID.VISUALLY_IMPAIRED),
            _green(VpID.WHEELCHAIR),
            _unknown(VpID.WHEELCHAIR_ARRIVE_BY_OWN_CAR),
            _green(VpID.WHEELCHAIR_ARRIVE_BY_DROPOFF),
        ],
        shortcomings=[],
    )
    assert accessibility.fix_unknown_and_zero_shortcomings()
    assert accessibility.shortcomings == ALL_UNKNOWN_SHORTCOMINGS

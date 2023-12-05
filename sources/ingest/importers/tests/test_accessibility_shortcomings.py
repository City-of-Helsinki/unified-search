from ingest.importers.location.dataclasses import AccessibilityShortcoming
from ingest.importers.location.utils import (
    get_unit_id_to_accessibility_shortcomings_mapping,
)


def test_get_unit_id_to_accessibility_shortcomings_mapping(
    mocked_service_map_unit_viewpoint_response,
):
    assert get_unit_id_to_accessibility_shortcomings_mapping() == {
        "71688": [],
        "71689": [
            AccessibilityShortcoming(profile="reduced_mobility", count=3),
            AccessibilityShortcoming(profile="rollator", count=4),
            AccessibilityShortcoming(profile="visually_impaired", count=6),
            AccessibilityShortcoming(profile="wheelchair", count=4),
        ],
        "72023": [
            AccessibilityShortcoming(profile="hearing_aid", count=1),
            AccessibilityShortcoming(profile="reduced_mobility", count=1),
            AccessibilityShortcoming(profile="rollator", count=2),
            AccessibilityShortcoming(profile="stroller", count=5),
            AccessibilityShortcoming(profile="visually_impaired", count=2),
            AccessibilityShortcoming(profile="wheelchair", count=2),
        ],
    }

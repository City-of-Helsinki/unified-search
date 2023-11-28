# Accessibility shortage texts that mean "no accessibility shortcomings",
# see e.g. https://www.hel.fi/palvelukarttaws/rest/v4/unit/5/accessibility_shortage/
from typing import Dict, List

from ingest.importers.location.enums import (
    AccessibilityProfile,
    AccessibilityViewpointID,
)
from ingest.importers.utils.shared import LanguageString

NO_SHORTCOMINGS_SHORTAGE_TEXT_VARIANTS: List[LanguageString] = [
    LanguageString(fi="Ei puutteita.", sv="Inga brister.", en="No shortcomings."),
    LanguageString(
        fi="Ei tiedettyjä puutteita.",
        sv="Inga kända brister.",
        en="No known shortcomings.",
    ),
]


# AccessibilityProfile to AccessibilityViewpointID values mapping i.e.
# Dict[AccessibilityProfile, List[AccessibilityViewpointID]] but as Dict[str, List[str]]
ACCESSIBILITY_PROFILE_VIEWPOINTS: Dict[str, List[str]] = {
    AccessibilityProfile.HEARING_AID.value: [
        AccessibilityViewpointID.HEARING_AID.value,
    ],
    AccessibilityProfile.REDUCED_MOBILITY.value: [
        AccessibilityViewpointID.REDUCED_MOBILITY.value,
        AccessibilityViewpointID.REDUCED_MOBILITY_ARRIVE_BY_OWN_CAR.value,
        AccessibilityViewpointID.REDUCED_MOBILITY_ARRIVE_BY_DROPOFF.value,
    ],
    AccessibilityProfile.ROLLATOR.value: [
        AccessibilityViewpointID.ROLLATOR.value,
        AccessibilityViewpointID.ROLLATOR_ARRIVE_BY_OWN_CAR.value,
        AccessibilityViewpointID.ROLLATOR_ARRIVE_BY_DROPOFF.value,
    ],
    AccessibilityProfile.STROLLER.value: [
        AccessibilityViewpointID.STROLLER.value,
    ],
    AccessibilityProfile.VISUALLY_IMPAIRED.value: [
        AccessibilityViewpointID.VISUALLY_IMPAIRED.value,
        AccessibilityViewpointID.VISUALLY_IMPAIRED_ARRIVE_BY_DROPOFF.value,
    ],
    AccessibilityProfile.WHEELCHAIR.value: [
        AccessibilityViewpointID.WHEELCHAIR.value,
        AccessibilityViewpointID.WHEELCHAIR_ARRIVE_BY_OWN_CAR.value,
        AccessibilityViewpointID.WHEELCHAIR_ARRIVE_BY_DROPOFF.value,
    ],
}

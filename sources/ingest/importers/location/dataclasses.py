import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set, Union

from ingest.importers.location.constants import (
    ACCESSIBILITY_PROFILE_VIEWPOINTS,
    NO_SHORTCOMINGS_SHORTAGE_TEXT_VARIANTS,
)
from ingest.importers.location.enums import (
    AccessibilityProfile,
    AccessibilityViewpointID,
    AccessibilityViewpointValue,
)
from ingest.importers.utils import LanguageString, OpeningHours
from ingest.importers.utils.administrative_division import AdministrativeDivision

BATCH_SIZE = 100

logger = logging.getLogger(__name__)


@dataclass
class ServiceOwner:
    providerType: str  # ProviderType as string to fix OpenSearch serialization
    type: str  # ServiceOwnerType as string to fix OpenSearch serialization
    name: LanguageString


@dataclass(eq=True)
class AccessibilitySentence:
    sentenceGroupName: str
    sentenceGroup: LanguageString
    sentence: LanguageString


@dataclass(eq=True, order=True)
class AccessibilityViewpoint:
    id: str  # AccessibilityViewpointID as string to fix OpenSearch serialization
    name: LanguageString
    value: str  # AccessibilityViewpointValue as string to fix OpenSearch serialization
    shortages: Optional[List[LanguageString]] = None


@dataclass
class NodeMeta:
    id: str
    createdAt: datetime
    updatedAt: datetime = None


@dataclass
class LinkedData:
    service: str = None
    origin_url: str = None
    raw_data: Union[dict, list] = None


@dataclass
class Address:
    postalCode: str
    streetAddress: LanguageString
    city: LanguageString


@dataclass
class Coordinates:
    latitude: float
    longitude: float
    northing_etrs_gk25: int
    easting_etrs_gk25: int
    northing_etrs_tm35fin: int
    easting_etrs_tm35fin: int
    manual_coordinates: bool


@dataclass
class GeoJSONGeometry:
    coordinates: Coordinates


@dataclass
class GeoJSONFeature:
    geometry: GeoJSONGeometry


@dataclass
class Location:
    url: LanguageString
    address: Address = None
    geoLocation: GeoJSONFeature = None
    administrativeDivisions: List[AdministrativeDivision] = field(default_factory=list)


@dataclass
class OntologyObject:
    id: str
    label: LanguageString


@dataclass
class Image:
    url: str
    caption: LanguageString


@dataclass(eq=True, order=True)
class AccessibilityShortcoming:
    """
    Accessibility shortcoming of an AccessibilityProfile,
    e.g. hearing_aid has 3 shortcomings
    """

    profile: str  # AccessibilityProfile as string to fix OpenSearch serialization
    count: Optional[int]  # None means unknown


@dataclass
class ResourceType:
    id: str
    mainType: str  # ResourceMainType as string to fix OpenSearch serialization
    name: LanguageString


@dataclass
class ResourceUserPermissions:
    canMakeReservations: bool


@dataclass
class Resource:
    id: str
    name: LanguageString
    description: LanguageString
    type: ResourceType
    userPermissions: ResourceUserPermissions
    reservable: bool
    reservationInfo: Optional[LanguageString]
    genericTerms: Optional[LanguageString]
    paymentTerms: Optional[LanguageString]
    specificTerms: Optional[LanguageString]
    responsibleContactInfo: Optional[LanguageString]
    externalReservationUrl: Optional[str]


@dataclass
class GeoPoint:
    latitude: float
    longitude: float


@dataclass
class Accessibility:
    email: str
    phone: str
    www: str
    viewpoints: List[AccessibilityViewpoint]
    sentences: List[AccessibilitySentence]
    shortcomings: List[AccessibilityShortcoming]

    def set_accessibility_shortages(
        self,
        viewpoint_id_to_shortages: Dict[str, List[LanguageString]],
    ) -> None:
        for viewpoint in self.viewpoints:
            viewpoint.shortages = viewpoint_id_to_shortages.get(viewpoint.id, [])[:]

    def viewpoint_id_to_shortages(self) -> Dict[str, List[LanguageString]]:
        """
        Mapping from AccessibilityViewpointID values to their accessibility shortages

        @warning This method should only be called after set_accessibility_shortages()
            has been called.
        @raises ValueError If any viewpoints' shortages have not been set i.e.
            any(vp.shortages is None for vp in self.viewpoints)
        @return A mapping from AccessibilityViewpointID values to their accessibility
            shortages
        """
        result: Dict[str, List[LanguageString]] = {
            viewpoint_id.value: [] for viewpoint_id in AccessibilityViewpointID
        }
        for viewpoint in self.viewpoints:
            if viewpoint.shortages is None:
                raise ValueError(
                    "Viewpoint's shortages have not been set, please call "
                    "self.set_accessibility_shortages before calling this method"
                )
            result[viewpoint.id] = viewpoint.shortages
        return result

    def viewpoint_id_to_value(self) -> Dict[str, str]:
        """
        Mapping from AccessibilityViewpointID values to their
        AccessibilityViewpointValue values

        @return A mapping from AccessibilityViewpointID values to their
                AccessibilityViewpointValue values
        """
        result: Dict[str, str] = {
            viewpoint_id.value: AccessibilityViewpointValue.UNKNOWN.value
            for viewpoint_id in AccessibilityViewpointID
        }
        for viewpoint in self.viewpoints:
            result[viewpoint.id] = viewpoint.value
        return result

    def profile_shortcomings(self) -> Dict[str, Optional[int]]:
        """
        Mapping from all possible AccessibilityProfile values to their accessibility
        shortcomings counts, or to null if unknown

        @return A mapping from all possible AccessibilityProfile values to their
                accessibility shortcomings counts, or to null if unknown
        """
        result: Dict[str, Optional[int]] = {
            profile.value: None for profile in AccessibilityProfile
        }
        for shortcoming in self.shortcomings:
            result[shortcoming.profile] = shortcoming.count
        return result

    def update_shortcomings(
        self, profile_shortcomings: Dict[str, Optional[int]]
    ) -> bool:
        """
        Update self.shortcomings using given mapping from AccessibilityProfile values to
        their optional shortcoming counts.

        @return True if self.shortcomings contents got changed, False otherwise.
        """
        fixed_shortcomings = [
            AccessibilityShortcoming(profile=profile, count=count)
            for profile, count in profile_shortcomings.items()
        ]
        has_changed = len(self.shortcomings) != len(fixed_shortcomings) or any(
            sc1 != sc2 for sc1, sc2 in zip(self.shortcomings, fixed_shortcomings)
        )
        self.shortcomings = fixed_shortcomings
        return has_changed

    def fix_unknown_and_zero_shortcomings(self) -> bool:
        """
        Fix unknown and zero accessibility shortcomings using accessibility viewpoints
        and accessibility shortages.

        @warning This method should only be called after set_accessibility_shortages()
            has been called.
        @raises ValueError If any viewpoints' shortages have not been set i.e.
            any(vp.shortages is None for vp in self.viewpoints)
        @return True if any shortcomings were fixed, False otherwise.
        """
        profile_shortcomings = self.profile_shortcomings()
        viewpoint_id_to_shortages = self.viewpoint_id_to_shortages()
        viewpoint_id_to_value = self.viewpoint_id_to_value()

        for profile, viewpoint_ids in ACCESSIBILITY_PROFILE_VIEWPOINTS.items():
            profile_statuses: Set[str] = {
                viewpoint_id_to_value[_id] for _id in viewpoint_ids
            }
            any_reds = AccessibilityViewpointValue.RED.value in profile_statuses
            any_unknowns = AccessibilityViewpointValue.UNKNOWN.value in profile_statuses
            all_greens = profile_statuses == {AccessibilityViewpointValue.GREEN.value}

            if profile_shortcomings[profile] in [None, 0]:
                if any_unknowns:
                    profile_shortcomings[profile] = None  # Mark as unknown
                elif any_reds:
                    profile_shortcomings[profile] = (
                        unique_shortages_count_for_viewpoint_ids(
                            viewpoint_ids, viewpoint_id_to_shortages
                        )
                        or None
                    )  # If "red" but no shortages mark as unknown
                elif all_greens:
                    profile_shortcomings[profile] = 0

        return self.update_shortcomings(profile_shortcomings)


@dataclass
class Venue:
    meta: NodeMeta = None
    name: LanguageString = None
    location: Location = None
    description: LanguageString = None
    serviceOwner: Optional[ServiceOwner] = None
    resources: List[Resource] = field(default_factory=list)
    # List[TargetGroup] as List[str] to fix OpenSearch serialization:
    targetGroups: List[str] = field(default_factory=list)

    # TODO
    descriptionResources: str = None
    partOf: "Venue" = None
    openingHours: OpeningHours = None
    manager: str = None
    reservationPolicy: str = None
    accessibility: Optional[Accessibility] = None
    arrivalInstructions: str = None
    additionalInfo: str = None
    facilities: str = None
    images: List[Image] = field(default_factory=list)
    ontologyWords: List[OntologyObject] = field(default_factory=list)


@dataclass
class Root:
    venue: Venue
    location: GeoPoint = None
    links: List[LinkedData] = field(default_factory=list)
    suggest: List[str] = field(default_factory=list)


def unique_shortages_count_for_viewpoint_ids(
    viewpoint_ids: List[str],
    viewpoint_id_to_shortages: Dict[str, List[LanguageString]],
):
    """
    Count unique accessibility shortages for given accessibility viewpoint IDs.

    @param viewpoint_ids A list of AccessibilityViewpointID values
    @param viewpoint_id_to_shortages A mapping from AccessibilityViewpointID values to
        their accessibility shortages
    @note Omits known accessibility shortages that mean "no accessibility shortcomings"
        in the calculation.
    @return The number of unique accessibility shortages for the given accessibility
            viewpoint IDs
    """
    return len(
        set(
            shortage
            for viewpoint_id in viewpoint_ids
            for shortage in viewpoint_id_to_shortages.get(viewpoint_id, [])
        )
        - set(NO_SHORTCOMINGS_SHORTAGE_TEXT_VARIANTS)
    )

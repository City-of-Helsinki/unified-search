from __future__ import annotations

import base64
import functools
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Union

from .base import Importer
from .utils import (
    AdministrativeDivision,
    AdministrativeDivisionFetcher,
    HaukiOpeningHoursFetcher,
    LanguageString,
    LanguageStringConverter,
    Ontology,
    OpeningHours,
    request_json,
)

BATCH_SIZE = 100

logger = logging.getLogger(__name__)


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
class GeoJSONFeature:
    geometry: GeoJSONGeometry


@dataclass
class GeoJSONGeometry:
    coordinates: Coordinates


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


class TargetGroup(Enum):
    ASSOCIATIONS = "ASSOCIATIONS"
    CHILDREN_AND_FAMILIES = "CHILDREN_AND_FAMILIES"
    DISABLED = "DISABLED"
    ELDERLY_PEOPLE = "ELDERLY_PEOPLE"
    ENTERPRISES = "ENTERPRISES"
    IMMIGRANTS = "IMMIGRANTS"
    INDIVIDUALS = "INDIVIDUALS"
    YOUTH = "YOUTH"


class ProviderType(Enum):
    ASSOCIATION = "ASSOCIATION"
    CONTRACT_SCHOOL = "CONTRACT_SCHOOL"
    MUNICIPALITY = "MUNICIPALITY"
    OTHER_PRODUCTION_METHOD = "OTHER_PRODUCTION_METHOD"
    PAYMENT_COMMITMENT = "PAYMENT_COMMITMENT"
    PRIVATE_COMPANY = "PRIVATE_COMPANY"
    PURCHASED_SERVICE = "PURCHASED_SERVICE"
    SELF_PRODUCED = "SELF_PRODUCED"
    SUPPORTED_OPERATIONS = "SUPPORTED_OPERATIONS"
    UNKNOWN_PRODUCTION_METHOD = "UNKNOWN_PRODUCTION_METHOD"
    VOUCHER_SERVICE = "VOUCHER_SERVICE"


class ServiceOwnerType(Enum):
    MUNICIPAL_SERVICE = "MUNICIPAL_SERVICE"
    NOT_DISPLAYED = "NOT_DISPLAYED"
    PRIVATE_CONTRACT_SCHOOL = "PRIVATE_CONTRACT_SCHOOL"
    PRIVATE_SERVICE = "PRIVATE_SERVICE"
    PURCHASED_SERVICE = "PURCHASED_SERVICE"
    SERVICE_BY_JOINT_MUNICIPAL_AUTHORITY = "SERVICE_BY_JOINT_MUNICIPAL_AUTHORITY"
    SERVICE_BY_MUNICIPALLY_OWNED_COMPANY = "SERVICE_BY_MUNICIPALLY_OWNED_COMPANY"
    SERVICE_BY_MUNICIPAL_GROUP_ENTITY = "SERVICE_BY_MUNICIPAL_GROUP_ENTITY"
    SERVICE_BY_OTHER_MUNICIPALITY = "SERVICE_BY_OTHER_MUNICIPALITY"
    SERVICE_BY_REGIONAL_COOPERATION_ORGANIZATION = (
        "SERVICE_BY_REGIONAL_COOPERATION_ORGANIZATION"
    )
    SERVICE_BY_WELLBEING_AREA = "SERVICE_BY_WELLBEING_AREA"
    STATE_CONTRACT_SCHOOL = "STATE_CONTRACT_SCHOOL"
    STATE_SERVICE = "STATE_SERVICE"
    SUPPORTED_OPERATIONS = "SUPPORTED_OPERATIONS"
    VOUCHER_SERVICE = "VOUCHER_SERVICE"


@dataclass
class ServiceOwner:
    providerType: str  # ProviderType as string to fix OpenSearch serialization
    type: str  # ServiceOwnerType as string to fix OpenSearch serialization
    name: LanguageString


class AccessibilityViewpointID(Enum):
    """
    Accessibility viewpoint ID values
     - 00: Choose accessibility perspective
     - 11: I am a wheelchair user
     - 12: I am a wheelchair user - arrive by my car
     - 13: I am a wheelchair user - arrive with pick-up and drop-off traffic
     - 21: I have reduced mobility, but I walk
     - 22: I have reduced mobility, but I walk - arrive by my car
     - 23: I have reduced mobility, but I walk - arrive with pick-up and drop-off traffic
     - 31: I am a rollator user
     - 32: I am a rollator user - arrive by my car
     - 33: I am a rollator user - arrive with pick-up and drop-off traffic
     - 41: I am a stroller pusher
     - 51: I am visually impaired
     - 52: I am visually impaired - arrive with pick-up and drop-off traffic
     - 61: I use a hearing aid
    Values taken from https://www.hel.fi/palvelukarttaws/rest/v4/accessibility_viewpoint/
    """

    CHOOSE_ACCESSIBILITY_PERSPECTIVE = "00"  # Has value "unknown", for UI purposes
    HEARING_AID = "61"
    REDUCED_MOBILITY = "21"
    REDUCED_MOBILITY_ARRIVE_BY_OWN_CAR = "22"
    REDUCED_MOBILITY_ARRIVE_BY_DROPOFF = "23"
    ROLLATOR = "31"
    ROLLATOR_ARRIVE_BY_OWN_CAR = "32"
    ROLLATOR_ARRIVE_BY_DROPOFF = "33"
    STROLLER = "41"
    VISUALLY_IMPAIRED = "51"
    VISUALLY_IMPAIRED_ARRIVE_BY_DROPOFF = "52"
    WHEELCHAIR = "11"
    WHEELCHAIR_ARRIVE_BY_OWN_CAR = "12"
    WHEELCHAIR_ARRIVE_BY_DROPOFF = "13"


class AccessibilityViewpointValue(Enum):
    UNKNOWN = "unknown"
    RED = "red"
    GREEN = "green"


# Accessibility shortage texts that mean "no accessibility shortcomings",
# see e.g. https://www.hel.fi/palvelukarttaws/rest/v4/unit/5/accessibility_shortage/
NO_SHORTCOMINGS_SHORTAGE_TEXT_VARIANTS: List[LanguageString] = [
    LanguageString(fi="Ei puutteita.", sv="Inga brister.", en="No shortcomings."),
    LanguageString(
        fi="Ei tiedettyjä puutteita.",
        sv="Inga kända brister.",
        en="No known shortcomings.",
    ),
]


@dataclass(eq=True, order=True)
class AccessibilityViewpoint:
    id: str  # AccessibilityViewpointID as string to fix OpenSearch serialization
    name: LanguageString
    value: str  # AccessibilityViewpointValue as string to fix OpenSearch serialization
    shortages: Optional[List[LanguageString]] = None


class AccessibilityProfile(Enum):
    HEARING_AID = "hearing_aid"
    REDUCED_MOBILITY = "reduced_mobility"
    ROLLATOR = "rollator"
    STROLLER = "stroller"
    VISUALLY_IMPAIRED = "visually_impaired"
    WHEELCHAIR = "wheelchair"


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


@dataclass(eq=True, order=True)
class AccessibilityShortcoming:
    """
    Accessibility shortcoming of an AccessibilityProfile,
    e.g. hearing_aid has 3 shortcomings
    """

    profile: str  # AccessibilityProfile as string to fix OpenSearch serialization
    count: Optional[int]  # None means unknown


@dataclass(eq=True)
class AccessibilitySentence:
    sentenceGroupName: str
    sentenceGroup: LanguageString
    sentence: LanguageString


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
        profile_shortcomings: Dict[str, Optional[int]] = {
            profile.value: None for profile in AccessibilityProfile
        }
        for shortcoming in self.shortcomings:
            profile_shortcomings[shortcoming.profile] = shortcoming.count

        viewpoint_id_to_shortages: Dict[str, List[LanguageString]] = {
            viewpoint_id.value: [] for viewpoint_id in AccessibilityViewpointID
        }
        for viewpoint in self.viewpoints:
            if viewpoint.shortages is None:
                raise ValueError(
                    "Viewpoint's shortages have not been set, please call "
                    "self.set_accessibility_shortages before calling this method"
                )
            viewpoint_id_to_shortages[viewpoint.id] = viewpoint.shortages

        viewpoint_id_to_value: Dict[str, str] = {
            viewpoint_id.value: AccessibilityViewpointValue.UNKNOWN.value
            for viewpoint_id in AccessibilityViewpointID
        }
        for viewpoint in self.viewpoints:
            viewpoint_id_to_value[viewpoint.id] = viewpoint.value

        for profile, viewpoint_ids in ACCESSIBILITY_PROFILE_VIEWPOINTS.items():
            profile_statuses = {viewpoint_id_to_value[_id] for _id in viewpoint_ids}
            any_reds = AccessibilityViewpointValue.RED.value in profile_statuses
            any_unknowns = AccessibilityViewpointValue.UNKNOWN.value in profile_statuses
            all_greens = profile_statuses == {AccessibilityViewpointValue.GREEN.value}
            if profile_shortcomings[profile] in [None, 0]:
                if any_unknowns:
                    profile_shortcomings[profile] = None  # Mark as unknown
                elif any_reds:
                    unique_shortages_count_for_profile = (
                        len(
                            set(
                                shortage
                                for viewpoint_id in viewpoint_ids
                                for shortage in viewpoint_id_to_shortages.get(
                                    viewpoint_id, []
                                )
                            )
                            - set(NO_SHORTCOMINGS_SHORTAGE_TEXT_VARIANTS)
                        )
                        or None
                    )  # If "red" but no shortages mark as unknown
                    profile_shortcomings[profile] = unique_shortages_count_for_profile
                elif all_greens:
                    profile_shortcomings[profile] = 0

        fixed_shortcomings = [
            AccessibilityShortcoming(profile=profile, count=count)
            for profile, count in profile_shortcomings.items()
        ]
        has_changed = len(self.shortcomings) != len(fixed_shortcomings) or any(
            sc1 != sc2 for sc1, sc2 in zip(self.shortcomings, fixed_shortcomings)
        )
        self.shortcomings = fixed_shortcomings
        return has_changed


class ResourceMainType(Enum):
    ITEM = "item"
    PERSON = "person"
    SPACE = "space"


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
    # annotations imported for this
    partOf: Venue = None
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
class GeoPoint:
    latitude: float
    longitude: float


@dataclass
class Root:
    venue: Venue
    location: GeoPoint = None
    links: List[LinkedData] = field(default_factory=list)
    suggest: List[str] = field(default_factory=list)


def get_tpr_units():
    # Use newfeatures=yes parameter to get displayed_service_owner_type and
    # displayed_service_owner_(fi|sv|en) fields included, see documentation at
    # https://www.hel.fi/palvelukarttaws/restpages/ver4.html
    url = "https://www.hel.fi/palvelukarttaws/rest/v4/unit/?newfeatures=yes"
    data = request_json(url)
    return data


def prefix_and_mask(prefix, body):
    message = f"{prefix}-{body}"
    message_bytes = message.encode("utf-8")
    base64_bytes = base64.b64encode(message_bytes)

    return base64_bytes.decode("utf-8")


def get_ontologywords_as_ontologies(ontologywords, use_fallback_languages: bool):
    ontologies = []

    for ontologyword in ontologywords:
        l = LanguageStringConverter(ontologyword, use_fallback_languages)

        ontologies.append(
            OntologyObject(
                id=str(ontologyword.get("id")),
                label=l.get_language_string("ontologyword"),
            )
        )

        if (
            "extra_searchwords_fi" in ontologyword
            or "extra_searchwords_sv" in ontologyword
            or "extra_searchwords_en" in ontologyword
        ):
            ontologies.append(
                OntologyObject(
                    # A unique id is not available in the source data. To make the id
                    # more opaque we are encoding it.
                    id=prefix_and_mask("es-", ontologyword.get("id")),
                    label=l.get_language_string("extra_searchwords"),
                )
            )

    return ontologies


def get_ontologytree_as_ontologies(ontologytree, use_fallback_languages: bool):
    ontologies = []

    for ontologybranch in ontologytree:
        l = LanguageStringConverter(ontologybranch, use_fallback_languages)

        ontologies.append(
            OntologyObject(
                id=str(ontologybranch.get("id")), label=l.get_language_string("name")
            )
        )

        if (
            "extra_searchwords_fi" in ontologybranch
            or "extra_searchwords_sv" in ontologybranch
            or "extra_searchwords_en" in ontologybranch
        ):
            ontologies.append(
                OntologyObject(
                    # A unique id is not available in the source data. To make the id
                    # more opaque we are encoding it.
                    id=prefix_and_mask("es-", ontologybranch.get("id")),
                    label=l.get_language_string("extra_searchwords"),
                )
            )

    return ontologies


def get_suggestions_from_ontologies(ontologies: List[OntologyObject]):
    ontologies_grouped_by_language = functools.reduce(
        lambda acc, ontology: {
            "fi": acc.get("fi") + [ontology.label.fi],
            "sv": acc.get("sv") + [ontology.label.sv],
            "en": acc.get("en") + [ontology.label.en],
        },
        ontologies,
        {"fi": [], "sv": [], "en": []},
    )

    # Suggestions are stored in shorthand syntax. If you want to add more
    # specific context or weight, you have to store suggestions on a per
    # suggestion basis (example):
    # [
    #     {
    #         "input": "beach",
    #         "weight": 2,
    #         "contexts": {
    #             "language": "en",
    #             "unit": "liikunta"
    #         }
    #     },
    #     {
    #         "input": "social services",
    #         "weight": 2,
    #         "contexts": {
    #             "language": "en",
    #             "unit": "social work"
    #         }
    #     },
    # ]
    suggest = []
    for [language, suggestions_in_language] in ontologies_grouped_by_language.items():
        suggestions_without_empty = list(
            filter(lambda suggestion: type(suggestion) == str, suggestions_in_language)
        )

        suggest.append(
            {"input": suggestions_without_empty, "contexts": {"language": language}}
        )

    return suggest


def define_language_properties():
    languages = [("fi", "finnish"), ("sv", "swedish"), ("en", "english")]
    language_properties = {}

    for [language, analyzer] in languages:
        language_properties[language] = {
            "type": "text",
            "analyzer": analyzer,
            "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
        }

    return language_properties


custom_mappings = {
    "properties": {
        "suggest": {
            "type": "completion",
            "contexts": [
                {
                    "name": "language",
                    "type": "category",
                }
            ],
        },
        "venue": {
            "properties": {
                "name": {"properties": define_language_properties()},
                "description": {"properties": define_language_properties()},
                "openingHours": {
                    "properties": {
                        "openRanges": {
                            "type": "date_range",
                        }
                    }
                },
            }
        },
        "location": {"type": "geo_point"},
    }
}


def get_respa_resources() -> List[dict]:
    """
    Get all resources from Respa API
    """
    accumulated_results = []
    url = "https://api.hel.fi/respa/v1/resource/?format=json&page_size=500"
    while url:
        respa_resources = request_json(url, timeout_seconds=120)
        accumulated_results += respa_resources["results"]
        url = respa_resources["next"]
    return accumulated_results


def get_unit_ids_and_accessibility_shortcoming_counts() -> List[dict]:
    """
    Get all unit IDs and their accessibility shortcoming counts from new service map API

    :return: A list of dictionaries each containing unit ID ("id") as integer and its
             accessibility shortcoming counts ("accessibility_shortcoming_count") in a
             dictionary.
    """
    accumulated_results = []
    url = "https://api.hel.fi/servicemap/v2/unit/?format=json&only=accessibility_shortcoming_count&page_size=1000"
    while url:
        units = request_json(url)
        accumulated_results += units["results"]
        url = units["next"]
    return accumulated_results


def create_accessibility_shortcomings(
    accessibility_shortcoming_counts: Dict[str, int]
) -> List[AccessibilityShortcoming]:
    """
    Create a list of accessibility shortcomings from a dictionary of accessibility
    shortcoming counts

    :param accessibility_shortcoming_counts: A dictionary of accessibility shortcoming
                                             counts of a unit.
    :return: A list of accessibility shortcomings.
    """
    return sorted(
        (
            AccessibilityShortcoming(
                profile=AccessibilityProfile(accessibility_profile).value,
                count=shortcoming_count,
            )
            for accessibility_profile, shortcoming_count in accessibility_shortcoming_counts.items()
        )
    )


def get_unit_id_to_accessibility_shortcomings_mapping() -> Dict[
    str, List[AccessibilityShortcoming]
]:
    """
    Get mapping of unit IDs to their accessibility shortcomings from new service map API
    """
    return {
        str(unit["id"]): create_accessibility_shortcomings(
            unit.get("accessibility_shortcoming_count", {})
        )
        for unit in get_unit_ids_and_accessibility_shortcoming_counts()
    }


def get_accessibility_viewpoint_id_to_name_mapping(
    use_fallback_languages: bool,
) -> Dict[str, LanguageString]:
    """
    Get accessibility viewpoint ID to name mapping from service map API.

    Documentation about the service map API's accessibility viewpoint endpoint:
    - https://www.hel.fi/palvelukarttaws/restpages/ver4.html#_accessibility_viewpoint

    :return: Mapping from accessibility viewpoint ID to accessibility viewpoint name.

    Example of a possible return value:
    {
        "11": LanguageString(fi="Olen pyörätuolin käyttäjä",
                             sv="Jag är en rullstolsanvändare",
                             en="I am a wheelchair user")
        },
        "61": LanguageString(fi="Käytän kuulolaitetta",
                             sv="Jag använder en hörapparat",
                             en="I use a hearing aid")
        }
    }
    """
    url = "https://www.hel.fi/palvelukarttaws/rest/v4/accessibility_viewpoint/"
    accessibility_viewpoints = request_json(url)
    return {
        viewpoint["id"]: LanguageStringConverter(
            viewpoint, use_fallback_languages
        ).get_language_string("name")
        for viewpoint in accessibility_viewpoints
    }


def create_accessibility_sentence(
    accessibility_sentence: dict, use_fallback_languages: bool
) -> AccessibilitySentence:
    """
    Create AccessibilitySentence object from a dictionary containing a single
    accessibility sentence from
    https://www.hel.fi/palvelukarttaws/rest/v4/accessibility_sentence/

    Documentation about the endpoint:
    - https://www.hel.fi/palvelukarttaws/restpages/ver4_en.html

    Example of input:
    e.g.
    {
        "unit_id": 6365,
        "sentence_group_name": "Sisätilat",
        "sentence_group_fi": "Sisätilat",
        "sentence_group_sv": "I lokalen",
        "sentence_group_en": "In the facility",
        "sentence_fi": "Asiointipisteen ovet erottuvat selkeästi.",
        "sentence_sv": "Dörrarna vid servicepunkten är lätta att urskilja.",
        "sentence_en": "The doors in the customer service point stand out clearly."
    }

    :return: AccessibilitySentence object containing the given accessibility sentence
    """
    return AccessibilitySentence(
        sentenceGroupName=accessibility_sentence["sentence_group_name"],
        sentenceGroup=LanguageStringConverter(
            accessibility_sentence, use_fallback_languages
        ).get_language_string("sentence_group"),
        sentence=LanguageStringConverter(
            accessibility_sentence, use_fallback_languages
        ).get_language_string("sentence"),
    )


def get_unit_id_to_accessibility_sentences_mapping(
    use_fallback_languages: bool,
) -> Dict[str, List[AccessibilitySentence]]:
    """
    Get a mapping of unit IDs to their accessibility sentences from service map API.
    """
    url = "https://www.hel.fi/palvelukarttaws/rest/v4/accessibility_sentence/"
    accessibility_sentences = request_json(url, timeout_seconds=120)
    result = defaultdict(list)
    for sentence in accessibility_sentences:
        result[str(sentence["unit_id"])].append(
            create_accessibility_sentence(sentence, use_fallback_languages)
        )
    return result


def get_unit_id_to_accessibility_viewpoint_shortages_mapping(
    use_fallback_languages: bool,
) -> Dict[str, Dict[str, List[LanguageString]]]:
    """
    Get a mapping of unit IDs to their accessibility viewpoints' IDs to their
    list of accessibility shortages from service map API.
    """
    url = "https://www.hel.fi/palvelukarttaws/rest/v4/accessibility_shortage/"
    accessibility_shortages = request_json(url, timeout_seconds=120)
    result = defaultdict(lambda: defaultdict(list))
    for shortage in accessibility_shortages:
        unit_id = str(shortage["unit_id"])
        viewpoint_id = str(shortage["viewpoint_id"])
        l = LanguageStringConverter(shortage, use_fallback_languages)
        result[unit_id][viewpoint_id].append(l.get_language_string("shortage"))
    return result


def get_accessibility_viewpoint_id_to_value_mapping(
    accessibility_viewpoints: Optional[str],
) -> Dict[str, str]:
    """
    Converts service map API's unit's accessibility_viewpoints string to a mapping from
    the accessibility viewpoint ID to the unit's accessibility viewpoint value.

    :param accessibility_viewpoints: A string of comma separated pairs of accessibility
                                     viewpoint IDs and their values separated with
                                     colons, e.g. "00:unknown,11:red".
    :return: A dictionary of accessibility viewpoint IDs and their values, e.g.
             {"00": "unknown", "11": "red"}.

    Documentation about accessibility viewpoint endpoint:
    - https://www.hel.fi/palvelukarttaws/restpages/ver4.html#_accessibility_viewpoint

    Accessibility viewpoint values:
    - https://www.hel.fi/palvelukarttaws/rest/v4/accessibility_viewpoint/

    The IDs are the same as in the accessibility viewpoint endpoint, e.g.
    https://www.hel.fi/palvelukarttaws/rest/v4/accessibility_viewpoint/
    ...
    {
        "id": "11",
        "name_fi": "Olen pyörätuolin käyttäjä",
        "name_sv": "Jag är en rullstolsanvändare",
        "name_en": "I am a wheelchair user",
        "values": [
            "unknown",
            "green",
            "red"
        ]
    },
    ...

    All accessibility viewpoints' values are limited to "unknown", "green" and "red".
    """
    return (
        dict(
            accessibility_viewpoint.split(":")
            for accessibility_viewpoint in accessibility_viewpoints.split(",")
        )
        if accessibility_viewpoints
        else {}
    )


def get_enriched_accessibility_viewpoints(
    accessibility_viewpoints: Optional[str],
    accessibility_viewpoint_id_to_name_mapping: Dict[str, LanguageString],
    omit_unknowns: bool,
) -> List[AccessibilityViewpoint]:
    """
    Converts service map API's unit's accessibility_viewpoints string to a list of
    AccessibilityViewpoint objects.

    :param accessibility_viewpoints: A string of comma separated pairs of accessibility
                                     viewpoint IDs and their values separated with
                                     colons, e.g. "00:unknown,11:red".
    :param accessibility_viewpoint_id_to_name_mapping: A dictionary of accessibility
                                                       viewpoint IDs mapped to their
                                                       names.
    :param omit_unknowns: Whether to omit accessibility viewpoints with value "unknown".
    :return: A list of AccessibilityViewpoint objects without viewpoints with value
             "unknown" if omit_unknowns is True, otherwise with all viewpoints.

    Example return value:
        get_enriched_accessibility_viewpoints(
            '11:red,21:green,61:unknown',
            get_accessibility_viewpoint_id_to_name_mapping(use_fallback_languages=True),
            omit_unknowns=True
        ) == [
            AccessibilityViewpoint(
                id='11',
                name=LanguageString(fi='Olen pyörätuolin käyttäjä',
                                    sv='Jag är en rullstolsanvändare',
                                    en='I am a wheelchair user'),
                value='red'
            ),
            AccessibilityViewpoint(
                id='21',
                name=LanguageString(fi='Olen liikkumisesteinen, mutta kävelen',
                                    sv='Jag är rörelsehindrad, men jag går',
                                    en='I have reduced mobility, but I walk'),
                value='green'
            )
        ]
    """
    id_to_value_mapping = get_accessibility_viewpoint_id_to_value_mapping(
        accessibility_viewpoints
    )
    return [
        AccessibilityViewpoint(
            id=viewpoint_id,
            name=accessibility_viewpoint_id_to_name_mapping[viewpoint_id],
            value=AccessibilityViewpointValue(viewpoint_value).value,
        )
        for viewpoint_id, viewpoint_value in id_to_value_mapping.items()
        if (
            not omit_unknowns
            or viewpoint_value != AccessibilityViewpointValue.UNKNOWN.value
        )
    ]


def create_resource_type(
    respa_resource_type: dict, use_fallback_languages: bool
) -> ResourceType:
    """
    Create a ResourceType object from a Respa resource's type.
    """
    l = LanguageStringConverter(respa_resource_type, use_fallback_languages)
    return ResourceType(
        id=respa_resource_type["id"],
        mainType=ResourceMainType(respa_resource_type["main_type"]).value,
        name=l.get_language_string("name"),
    )


def create_resource_user_permissions(
    respa_user_permissions: dict,
) -> ResourceUserPermissions:
    """
    Create a ResourceUserPermissions object from a Respa user permissions
    """
    return ResourceUserPermissions(
        canMakeReservations=respa_user_permissions["can_make_reservations"],
    )


def create_exportable_resource(
    respa_resource: dict, use_fallback_languages: bool
) -> Resource:
    """
    Create a Resource object from a Respa resource.
    """
    l = LanguageStringConverter(respa_resource, use_fallback_languages)
    return Resource(
        id=respa_resource["id"],
        name=l.get_language_string("name"),
        description=l.get_language_string("description"),
        type=create_resource_type(respa_resource["type"], use_fallback_languages),
        userPermissions=create_resource_user_permissions(
            respa_resource["user_permissions"]
        ),
        reservable=respa_resource["reservable"],
        reservationInfo=l.get_language_string("reservation_info"),
        genericTerms=l.get_language_string("generic_terms"),
        paymentTerms=l.get_language_string("payment_terms"),
        specificTerms=l.get_language_string("specific_terms"),
        responsibleContactInfo=l.get_language_string("responsible_contact_info"),
        externalReservationUrl=respa_resource["external_reservation_url"],
    )


def get_unit_id_to_resources_mapping(
    use_fallback_languages: bool,
) -> Dict[str, List[Resource]]:
    """
    Get a mapping of unit IDs to their resources from Respa API.
    """
    result = defaultdict(list)
    for respa_resource in get_respa_resources():
        unit_id = str(respa_resource.get("unit", ""))
        # Remove 'tprek:' prefix from unit IDs (e.g. "tprek:50174" or "axarwdco746q")
        removable_prefix = "tprek:"
        if unit_id.startswith(removable_prefix):
            unit_id = unit_id[len(removable_prefix) :]
        result[unit_id].append(
            create_exportable_resource(respa_resource, use_fallback_languages)
        )
    return result


def get_unit_id_to_target_groups_mapping() -> Dict[str, Set[TargetGroup]]:
    """
    Get a mapping of unit IDs to their target groups from palvelukuvausrekisteri, see
    https://www.hel.fi/palvelukarttaws/restpages/palvelurekisteri.html for documentation
    """
    url = "https://www.hel.fi/palvelukarttaws/rest/vpalvelurekisteri/description/?alldata=yes"
    services = request_json(url, timeout_seconds=120)
    result = defaultdict(set)
    for service in services:
        unit_ids = service.get("unit_ids", [])
        target_groups = service.get("target_groups", [])
        for unit_id in unit_ids:
            result[str(unit_id)] |= set(map(TargetGroup, target_groups))
    return result


class LocationImporter(Importer[Root]):
    index_base_names = ("location",)

    def run(self):  # noqa C901 this function could use some refactoring
        self.apply_mapping(custom_mappings)

        logger.debug("Requesting data at {}".format(__name__))

        ontology = Ontology()

        unit_id_to_accessibility_shortcomings_mapping = (
            get_unit_id_to_accessibility_shortcomings_mapping()
        )
        unit_id_to_accessibility_sentences_mapping = (
            get_unit_id_to_accessibility_sentences_mapping(self.use_fallback_languages)
        )
        unit_id_to_accessibility_viewpoint_shortages_mapping = (
            get_unit_id_to_accessibility_viewpoint_shortages_mapping(
                self.use_fallback_languages
            )
        )
        unit_id_to_resources_mapping = get_unit_id_to_resources_mapping(
            self.use_fallback_languages
        )
        unit_id_to_target_groups_mapping = get_unit_id_to_target_groups_mapping()
        accessibility_viewpoint_id_to_name_mapping = (
            get_accessibility_viewpoint_id_to_name_mapping(self.use_fallback_languages)
        )
        tpr_units = get_tpr_units()

        opening_hours_fetcher = HaukiOpeningHoursFetcher(t["id"] for t in tpr_units)
        administrative_division_fetcher = AdministrativeDivisionFetcher()

        data_buffer: List[Root] = []
        count = 0
        for tpr_unit in tpr_units:
            l = LanguageStringConverter(tpr_unit, self.use_fallback_languages)
            e = lambda k: tpr_unit.get(k, None)  # noqa: E731

            # ID's must be strings to avoid collisions
            tpr_unit["id"] = _id = str(tpr_unit["id"])

            meta = NodeMeta(id=_id, createdAt=datetime.now())

            location = Location(
                url=l.get_language_string("www"),
                address=Address(
                    postalCode=e("address_zip"),
                    streetAddress=l.get_language_string("street_address"),
                    city=l.get_language_string("address_city"),
                ),
                geoLocation=GeoJSONFeature(
                    geometry=GeoJSONGeometry(
                        coordinates=Coordinates(
                            latitude=e("latitude"),
                            longitude=e("longitude"),
                            northing_etrs_gk25=e("northing_etrs_gk25"),
                            easting_etrs_gk25=e("easting_etrs_gk25"),
                            northing_etrs_tm35fin=e("northing_etrs_tm35fin"),
                            easting_etrs_tm35fin=e("easting_etrs_tm35fin"),
                            manual_coordinates=e("manual_coordinates"),
                        )
                    )
                ),
            )

            # Assuming single image
            images = []
            images.append(
                Image(
                    url=e("picture_url"),
                    caption=l.get_language_string("picture_caption"),
                )
            )

            (
                opening_hours,
                opening_hours_link,
            ) = opening_hours_fetcher.get_opening_hours_and_link(_id)

            venue = Venue(
                name=l.get_language_string("name"),
                description=l.get_language_string("desc"),
                serviceOwner=ServiceOwner(
                    providerType=ProviderType(
                        e("provider_type") or ProviderType.UNKNOWN_PRODUCTION_METHOD
                    ).value,
                    type=ServiceOwnerType(
                        e("displayed_service_owner_type")
                        or ServiceOwnerType.NOT_DISPLAYED
                    ).value,
                    name=l.get_language_string("displayed_service_owner"),
                ),
                resources=unit_id_to_resources_mapping.get(_id, []),
                targetGroups=sorted(
                    target_group.value
                    for target_group in unit_id_to_target_groups_mapping.get(_id, set())
                ),
                location=location,
                meta=meta,
                openingHours=opening_hours,
                accessibility=Accessibility(
                    email=e("accessibility_email"),
                    phone=e("accessibility_phone"),
                    www=e("accessibility_www"),
                    viewpoints=get_enriched_accessibility_viewpoints(
                        e("accessibility_viewpoints"),
                        accessibility_viewpoint_id_to_name_mapping,
                        omit_unknowns=True,
                    ),
                    sentences=unit_id_to_accessibility_sentences_mapping.get(_id, []),
                    shortcomings=unit_id_to_accessibility_shortcomings_mapping.get(
                        _id, []
                    ),
                ),
                images=images,
            )

            # Add accessibility viewpoints' shortages to the venue
            venue.accessibility.set_accessibility_shortages(
                unit_id_to_accessibility_viewpoint_shortages_mapping.get(_id, dict())
            )

            venue.accessibility.fix_unknown_and_zero_shortcomings()

            root = Root(venue=venue)

            if opening_hours_link:
                root.links.append(opening_hours_link)

            coordinates = venue.location.geoLocation.geometry.coordinates
            venue.location.administrativeDivisions = (
                administrative_division_fetcher.get_by_coordinates(
                    longitude=coordinates.longitude, latitude=coordinates.latitude
                )
            )

            # Extra information to raw data
            tpr_unit["origin"] = "tpr"

            # TODO: Separate words from tree
            # TODO: Remove duplicates
            #       Duplicates are not yet removed, because ontologies are not
            #       returned in a public facing data structure.
            all_ontologies = []
            # Ontology ID's and tree contain plain integers, get corresponding texts
            if tpr_unit.get("ontologyword_ids", None):
                word_ontologies = ontology.enrich_word_ids(tpr_unit["ontologyword_ids"])
                tpr_unit["ontologyword_ids_enriched"] = word_ontologies
                all_ontologies += get_ontologywords_as_ontologies(
                    word_ontologies, self.use_fallback_languages
                )
                venue.ontologyWords = [
                    {
                        "id": word["id"],
                        "label": {
                            "fi": word["ontologyword_fi"],
                            "sv": word["ontologyword_sv"],
                            "en": word["ontologyword_en"],
                        },
                    }
                    for word in word_ontologies
                ]

            if tpr_unit.get("ontologytree_ids", None):
                tree_ontologies = ontology.enrich_tree_ids(tpr_unit["ontologytree_ids"])
                tpr_unit["ontologytree_ids_enriched"] = tree_ontologies
                all_ontologies += get_ontologytree_as_ontologies(
                    tree_ontologies, self.use_fallback_languages
                )

            root.suggest = get_suggestions_from_ontologies(all_ontologies)

            link = LinkedData(
                service="tpr",
                origin_url=f"https://www.hel.fi/palvelukarttaws/rest/v4/unit/{_id}/",
                raw_data=tpr_unit,
            )
            root.links.append(link)

            root.location = (
                {"lat": e("latitude"), "lon": e("longitude")}
                if e("latitude") and e("longitude")
                else None
            )

            data_buffer.append(root)
            if len(data_buffer) >= BATCH_SIZE:
                self.add_data_bulk(data_buffer)
                data_buffer = []

            logger.debug(f"Fetched data count: {count}")
            count = count + 1

        if data_buffer:
            self.add_data_bulk(data_buffer)

        logger.info(f"Fetched {count} items in total")

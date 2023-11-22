from __future__ import annotations

from enum import Enum


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


class AccessibilityProfile(Enum):
    HEARING_AID = "hearing_aid"
    REDUCED_MOBILITY = "reduced_mobility"
    ROLLATOR = "rollator"
    STROLLER = "stroller"
    VISUALLY_IMPAIRED = "visually_impaired"
    WHEELCHAIR = "wheelchair"

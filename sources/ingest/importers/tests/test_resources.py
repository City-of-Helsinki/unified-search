import pytest

from ..location import (
    get_unit_id_to_resources_mapping,
    Resource,
    ResourceType,
    ResourceUserPermissions,
)
from ..utils import LanguageString

MOCKED_RESPA_RESOURCE_RESPONSE = {
    "count": 3,
    "next": None,
    "previous": None,
    "results": [
        {
            "id": "axayciqmqfja",
            "products": [
                {
                    "id": "axay4b73rdva",
                    "type": "rent",
                    "name": {"fi": "Tenniskenttä 2 - Ala-Malmi"},
                    "description": {"fi": "Tenniskenttä 2 - Ala-Malmi"},
                    "price": {
                        "type": "per_period",
                        "tax_percentage": "10.00",
                        "amount": "7.30",
                        "period": "01:00:00",
                    },
                    "max_quantity": 1,
                }
            ],
            "purposes": [
                {
                    "name": {
                        "fi": "Liikkua tai pelata",
                        "en": "Sports or games",
                        "sv": "Motionera eller spela",
                    },
                    "parent": None,
                    "id": "sports",
                }
            ],
            "images": [
                {
                    "url": "https://api.hel.fi/respa/resource_image/1181",
                    "type": "other",
                    "caption": None,
                },
                {
                    "url": "https://api.hel.fi/respa/resource_image/1179",
                    "type": "other",
                    "caption": None,
                },
                {
                    "url": "https://api.hel.fi/respa/resource_image/1178",
                    "type": "main",
                    "caption": None,
                },
                {
                    "url": "https://api.hel.fi/respa/resource_image/1180",
                    "type": "other",
                    "caption": None,
                },
                {
                    "url": "https://api.hel.fi/respa/resource_image/1204",
                    "type": "ground_plan",
                    "caption": None,
                },
            ],
            "equipment": [],
            "type": {
                "name": {
                    "fi": "Liikuntapaikka",
                    "en": "Sports field",
                    "sv": "Idrottsplats",
                },
                "main_type": "space",
                "id": "awqjgibywfvq",
            },
            "opening_hours": [
                {
                    "date": "2023-07-26",
                    "opens": "2023-07-26T08:00:00+03:00",
                    "closes": "2023-07-26T21:00:00+03:00",
                }
            ],
            "reservations": None,
            "user_permissions": {
                "can_make_reservations": True,
                "can_ignore_opening_hours": False,
                "is_admin": False,
                "is_manager": False,
                "is_viewer": False,
                "can_bypass_payment": False,
            },
            "supported_reservation_extra_fields": [
                "billing_email_address",
                "billing_first_name",
                "billing_last_name",
                "billing_phone_number",
                "participants",
            ],
            "required_reservation_extra_fields": [
                "billing_email_address",
                "billing_first_name",
                "billing_last_name",
            ],
            "is_favorite": False,
            "generic_terms": {"fi": "terms fi", "en": "terms en", "sv": "terms sv"},
            "payment_terms": {
                "fi": "payment_terms_fi",
                "en": "payment_terms_en",
                "sv": "payment_terms_sv",
            },
            "accessibility_base_url": "https://example.org/axayciqmqfja",
            "reservable_days_in_advance": 14,
            "reservable_max_days_in_advance": 14,
            "reservable_before": "2023-08-10T00:00:00Z",
            "reservable_min_days_in_advance": None,
            "reservable_after": None,
            "max_price_per_hour": 7.0,
            "min_price_per_hour": 7.0,
            "created_at": "2021-05-04T16:34:09.717587+03:00",
            "modified_at": "2021-05-04T16:34:09.717606+03:00",
            "public": True,
            "name": {
                "fi": "Tenniskenttä 2 - Ala-Malmi",
                "en": "Tennis court 2 - Ala-Malmi",
                "sv": "Tennisplan 2 - Nedre-Malm",
            },
            "description": {
                "fi": "Varattavissa kaudelle 2023!",
                "en": "Reservable for season 2023!",
                "sv": "Bokningen för säsongen 2023 är öppen!",
            },
            "need_manual_confirmation": False,
            "authentication": "weak",
            "people_capacity": 4,
            "area": 260,
            "min_period": "00:30:00",
            "max_period": "02:00:00",
            "slot_size": "00:30:00",
            "max_reservations_per_user": 2,
            "reservable": True,
            "reservation_info": {
                "fi": "reservation_info_fi",
                "en": "reservation_info_en",
                "sv": "reservation_info_sv",
            },
            "responsible_contact_info": {
                "fi": "responsible_contact_info_fi",
                "en": "responsible_contact_info_en",
                "sv": "responsible_contact_info_sv",
            },
            "specific_terms": {
                "fi": "specific_terms_fi",
                "en": "specific_terms_en",
                "sv": "specific_terms_sv",
            },
            "min_price": "7.00",
            "max_price": "7.00",
            "price_type": "hourly",
            "generate_access_codes": True,
            "external_reservation_url": None,
            "reservation_extra_questions": "",
            "created_by": None,
            "modified_by": None,
            "unit": "tprek:42086",
            "attachments": [],
            "location": None,
        },
        {
            "id": "axaxxck4ub7a",
            "products": [
                {
                    "id": "axay4cnjl37a",
                    "type": "rent",
                    "name": {"fi": "Tenniskenttä 3 - Ala-Malmi"},
                    "description": {"fi": "Tenniskenttä 3 - Ala-Malmi"},
                    "price": {
                        "type": "per_period",
                        "tax_percentage": "10.00",
                        "amount": "7.30",
                        "period": "01:00:00",
                    },
                    "max_quantity": 1,
                }
            ],
            "purposes": [
                {
                    "name": {
                        "fi": "Liikkua tai pelata",
                        "en": "Sports or games",
                        "sv": "Motionera eller spela",
                    },
                    "parent": None,
                    "id": "sports",
                }
            ],
            "images": [
                {
                    "url": "https://api.hel.fi/respa/resource_image/1185",
                    "type": "other",
                    "caption": None,
                },
                {
                    "url": "https://api.hel.fi/respa/resource_image/1183",
                    "type": "other",
                    "caption": None,
                },
                {
                    "url": "https://api.hel.fi/respa/resource_image/1182",
                    "type": "other",
                    "caption": None,
                },
                {
                    "url": "https://api.hel.fi/respa/resource_image/1184",
                    "type": "main",
                    "caption": None,
                },
                {
                    "url": "https://api.hel.fi/respa/resource_image/1205",
                    "type": "ground_plan",
                    "caption": None,
                },
            ],
            "equipment": [],
            "type": {
                "name": {
                    "fi": "Liikuntapaikka",
                    "en": "Sports field",
                    "sv": "Idrottsplats",
                },
                "main_type": "space",
                "id": "awqjgibywfvq",
            },
            "opening_hours": [
                {
                    "date": "2023-07-26",
                    "opens": "2023-07-26T08:00:00+03:00",
                    "closes": "2023-07-26T21:00:00+03:00",
                }
            ],
            "reservations": None,
            "user_permissions": {
                "can_make_reservations": True,
                "can_ignore_opening_hours": False,
                "is_admin": False,
                "is_manager": False,
                "is_viewer": False,
                "can_bypass_payment": False,
            },
            "supported_reservation_extra_fields": [
                "billing_email_address",
                "billing_first_name",
                "billing_last_name",
                "billing_phone_number",
                "participants",
            ],
            "required_reservation_extra_fields": [
                "billing_email_address",
                "billing_first_name",
                "billing_last_name",
            ],
            "is_favorite": False,
            "generic_terms": {
                "fi": "generic_terms_fi",
                "en": "generic_terms_en",
                "sv": "generic_terms_sv",
            },
            "payment_terms": {
                "fi": "payment_terms_fi",
                "en": "payment_terms_en",
                "sv": "payment_terms_sv",
            },
            "accessibility_base_url": "https://example.org/axaxxck4ub7a",
            "reservable_days_in_advance": 14,
            "reservable_max_days_in_advance": 14,
            "reservable_before": "2023-08-10T00:00:00Z",
            "reservable_min_days_in_advance": None,
            "reservable_after": None,
            "max_price_per_hour": 7.0,
            "min_price_per_hour": 7.0,
            "created_at": "2021-05-04T09:53:33.217020+03:00",
            "modified_at": "2021-05-04T09:53:33.217040+03:00",
            "public": True,
            "name": {
                "fi": "Tenniskenttä 3 - Ala-Malmi",
                "en": "Tennis court 3 - Ala-Malmi",
                "sv": "Tennisplan 3 - Nedre-Malm",
            },
            "description": {
                "fi": "description_fi",
                "en": "description_en",
                "sv": "description_sv",
            },
            "need_manual_confirmation": False,
            "authentication": "weak",
            "people_capacity": 4,
            "area": None,
            "min_period": "00:30:00",
            "max_period": "02:00:00",
            "slot_size": "00:30:00",
            "max_reservations_per_user": 2,
            "reservable": True,
            "reservation_info": {
                "fi": "reservation_info_fi",
                "en": "reservation_info_en",
                "sv": "reservation_info_sv",
            },
            "responsible_contact_info": {
                "fi": "responsible_contact_info_fi",
                "en": "responsible_contact_info_en",
                "sv": "responsible_contact_info_sv",
            },
            "specific_terms": {
                "fi": "specific_terms_fi",
                "en": "specific_terms_en",
                "sv": "specific_terms_sv",
            },
            "min_price": "7.00",
            "max_price": "7.00",
            "price_type": "hourly",
            "generate_access_codes": True,
            "external_reservation_url": None,
            "reservation_extra_questions": "",
            "created_by": None,
            "modified_by": None,
            "unit": "tprek:42086",
            "attachments": [],
            "location": None,
        },
        {
            "id": "aweyzvgot72q",
            "products": [],
            "purposes": [
                {
                    "name": {
                        "fi": "Järjestää tapahtuman",
                        "en": "Organize event",
                        "sv": "Arrangera evenemanget",
                    },
                    "parent": None,
                    "id": "events",
                }
            ],
            "images": [
                {
                    "url": "https://api.hel.fi/respa/resource_image/1175",
                    "type": "main",
                    "caption": None,
                },
                {
                    "url": "https://api.hel.fi/respa/resource_image/1176",
                    "type": "other",
                    "caption": None,
                },
                {
                    "url": "https://api.hel.fi/respa/resource_image/641",
                    "type": "map",
                    "caption": None,
                },
                {
                    "url": "https://api.hel.fi/respa/resource_image/1177",
                    "type": "other",
                    "caption": None,
                },
            ],
            "equipment": [],
            "type": {
                "name": {
                    "fi": "Tapahtumatila",
                    "en": "Event space",
                    "sv": "Evenemangsutrymme",
                },
                "main_type": "space",
                "id": "event_space",
            },
            "opening_hours": [{"date": "2023-07-26", "opens": None, "closes": None}],
            "reservations": None,
            "user_permissions": {
                "can_make_reservations": True,
                "can_ignore_opening_hours": False,
                "is_admin": False,
                "is_manager": False,
                "is_viewer": False,
                "can_bypass_payment": False,
            },
            "supported_reservation_extra_fields": [
                "reserver_name",
                "reserver_phone_number",
                "event_description",
                "number_of_participants",
                "reserver_email_address",
                "event_subject",
            ],
            "required_reservation_extra_fields": [
                "reserver_name",
                "reserver_phone_number",
                "event_description",
                "number_of_participants",
                "reserver_email_address",
                "event_subject",
            ],
            "is_favorite": False,
            "generic_terms": {"fi": "info fi", "en": "info en", "sv": "info sv"},
            "payment_terms": "",
            "accessibility_base_url": "https://example.org/aweyzvgot72q",
            "reservable_days_in_advance": None,
            "reservable_max_days_in_advance": None,
            "reservable_before": None,
            "reservable_min_days_in_advance": None,
            "reservable_after": None,
            "max_price_per_hour": None,
            "min_price_per_hour": None,
            "created_at": "2019-05-23T15:00:42.247090+03:00",
            "modified_at": "2019-05-23T15:00:42.247111+03:00",
            "public": True,
            "name": {
                "fi": "Ala-Malmin puisto",
                "en": "Ala-Malmin puisto park",
                "sv": "Nedre Malms park",
            },
            "description": {"fi": "test fi", "en": "test en", "sv": "test sv"},
            "need_manual_confirmation": False,
            "authentication": "strong",
            "people_capacity": 200,
            "area": 1000,
            "min_period": "01:00:00",
            "max_period": "10:00:00",
            "slot_size": "01:00:00",
            "max_reservations_per_user": 11,
            "reservable": True,
            "reservation_info": None,
            "responsible_contact_info": {"fi": "Yhteissähköposti: ulkoilma@hel.fi"},
            "specific_terms": {"fi": "testi"},
            "min_price": None,
            "max_price": None,
            "price_type": "hourly",
            "generate_access_codes": True,
            "external_reservation_url": "https://tilavaraus.hel.fi/reservation-unit/479",
            "reservation_extra_questions": "",
            "created_by": None,
            "modified_by": 10043,
            "unit": "tprek:59763",
            "attachments": [],
            "location": None,
        },
    ],
}


@pytest.fixture(scope="module", autouse=True)
def mocked_respa_resource_response(module_mocker):
    return module_mocker.patch(
        "ingest.importers.location.request_json",
        return_value=MOCKED_RESPA_RESOURCE_RESPONSE,
    )


@pytest.mark.parametrize(
    "use_fallback_languages,expected_result",
    [
        (
            False,
            {
                "tprek:42086": [
                    Resource(
                        id="axayciqmqfja",
                        name=LanguageString(
                            fi="Tenniskenttä 2 - Ala-Malmi",
                            sv="Tennisplan 2 - Nedre-Malm",
                            en="Tennis court 2 - Ala-Malmi",
                        ),
                        description=LanguageString(
                            fi="Varattavissa kaudelle 2023!",
                            sv="Bokningen för säsongen 2023 är öppen!",
                            en="Reservable for season 2023!",
                        ),
                        type=ResourceType(
                            id="awqjgibywfvq",
                            mainType="space",
                            name=LanguageString(
                                fi="Liikuntapaikka",
                                sv="Idrottsplats",
                                en="Sports field",
                            ),
                        ),
                        userPermissions=ResourceUserPermissions(
                            canMakeReservations=True
                        ),
                        reservable=True,
                        reservationInfo=LanguageString(
                            fi="reservation_info_fi",
                            sv="reservation_info_sv",
                            en="reservation_info_en",
                        ),
                        genericTerms=LanguageString(
                            fi="terms fi", sv="terms sv", en="terms en"
                        ),
                        paymentTerms=LanguageString(
                            fi="payment_terms_fi",
                            sv="payment_terms_sv",
                            en="payment_terms_en",
                        ),
                        specificTerms=LanguageString(
                            fi="specific_terms_fi",
                            sv="specific_terms_sv",
                            en="specific_terms_en",
                        ),
                        responsibleContactInfo=LanguageString(
                            fi="responsible_contact_info_fi",
                            sv="responsible_contact_info_sv",
                            en="responsible_contact_info_en",
                        ),
                        externalReservationUrl=None,
                    ),
                    Resource(
                        id="axaxxck4ub7a",
                        name=LanguageString(
                            fi="Tenniskenttä 3 - Ala-Malmi",
                            sv="Tennisplan 3 - Nedre-Malm",
                            en="Tennis court 3 - Ala-Malmi",
                        ),
                        description=LanguageString(
                            fi="description_fi",
                            sv="description_sv",
                            en="description_en",
                        ),
                        type=ResourceType(
                            id="awqjgibywfvq",
                            mainType="space",
                            name=LanguageString(
                                fi="Liikuntapaikka",
                                sv="Idrottsplats",
                                en="Sports field",
                            ),
                        ),
                        userPermissions=ResourceUserPermissions(
                            canMakeReservations=True
                        ),
                        reservable=True,
                        reservationInfo=LanguageString(
                            fi="reservation_info_fi",
                            sv="reservation_info_sv",
                            en="reservation_info_en",
                        ),
                        genericTerms=LanguageString(
                            fi="generic_terms_fi",
                            sv="generic_terms_sv",
                            en="generic_terms_en",
                        ),
                        paymentTerms=LanguageString(
                            fi="payment_terms_fi",
                            sv="payment_terms_sv",
                            en="payment_terms_en",
                        ),
                        specificTerms=LanguageString(
                            fi="specific_terms_fi",
                            sv="specific_terms_sv",
                            en="specific_terms_en",
                        ),
                        responsibleContactInfo=LanguageString(
                            fi="responsible_contact_info_fi",
                            sv="responsible_contact_info_sv",
                            en="responsible_contact_info_en",
                        ),
                        externalReservationUrl=None,
                    ),
                ],
                "tprek:59763": [
                    Resource(
                        id="aweyzvgot72q",
                        name=LanguageString(
                            fi="Ala-Malmin puisto",
                            sv="Nedre Malms park",
                            en="Ala-Malmin puisto park",
                        ),
                        description=LanguageString(
                            fi="test fi", sv="test sv", en="test en"
                        ),
                        type=ResourceType(
                            id="event_space",
                            mainType="space",
                            name=LanguageString(
                                fi="Tapahtumatila",
                                sv="Evenemangsutrymme",
                                en="Event space",
                            ),
                        ),
                        userPermissions=ResourceUserPermissions(
                            canMakeReservations=True
                        ),
                        reservable=True,
                        reservationInfo=None,
                        genericTerms=LanguageString(
                            fi="info fi", sv="info sv", en="info en"
                        ),
                        paymentTerms=None,
                        specificTerms=LanguageString(fi="testi", sv=None, en=None),
                        responsibleContactInfo=LanguageString(
                            fi="Yhteissähköposti: ulkoilma@hel.fi", sv=None, en=None
                        ),
                        externalReservationUrl="https://tilavaraus.hel.fi/reservation-unit/479",
                    )
                ],
            },
        ),
        (
            True,
            {
                "tprek:42086": [
                    Resource(
                        id="axayciqmqfja",
                        name=LanguageString(
                            fi="Tenniskenttä 2 - Ala-Malmi",
                            sv="Tennisplan 2 - Nedre-Malm",
                            en="Tennis court 2 - Ala-Malmi",
                        ),
                        description=LanguageString(
                            fi="Varattavissa kaudelle 2023!",
                            sv="Bokningen för säsongen 2023 är öppen!",
                            en="Reservable for season 2023!",
                        ),
                        type=ResourceType(
                            id="awqjgibywfvq",
                            mainType="space",
                            name=LanguageString(
                                fi="Liikuntapaikka",
                                sv="Idrottsplats",
                                en="Sports field",
                            ),
                        ),
                        userPermissions=ResourceUserPermissions(
                            canMakeReservations=True
                        ),
                        reservable=True,
                        reservationInfo=LanguageString(
                            fi="reservation_info_fi",
                            sv="reservation_info_sv",
                            en="reservation_info_en",
                        ),
                        genericTerms=LanguageString(
                            fi="terms fi", sv="terms sv", en="terms en"
                        ),
                        paymentTerms=LanguageString(
                            fi="payment_terms_fi",
                            sv="payment_terms_sv",
                            en="payment_terms_en",
                        ),
                        specificTerms=LanguageString(
                            fi="specific_terms_fi",
                            sv="specific_terms_sv",
                            en="specific_terms_en",
                        ),
                        responsibleContactInfo=LanguageString(
                            fi="responsible_contact_info_fi",
                            sv="responsible_contact_info_sv",
                            en="responsible_contact_info_en",
                        ),
                        externalReservationUrl=None,
                    ),
                    Resource(
                        id="axaxxck4ub7a",
                        name=LanguageString(
                            fi="Tenniskenttä 3 - Ala-Malmi",
                            sv="Tennisplan 3 - Nedre-Malm",
                            en="Tennis court 3 - Ala-Malmi",
                        ),
                        description=LanguageString(
                            fi="description_fi",
                            sv="description_sv",
                            en="description_en",
                        ),
                        type=ResourceType(
                            id="awqjgibywfvq",
                            mainType="space",
                            name=LanguageString(
                                fi="Liikuntapaikka",
                                sv="Idrottsplats",
                                en="Sports field",
                            ),
                        ),
                        userPermissions=ResourceUserPermissions(
                            canMakeReservations=True
                        ),
                        reservable=True,
                        reservationInfo=LanguageString(
                            fi="reservation_info_fi",
                            sv="reservation_info_sv",
                            en="reservation_info_en",
                        ),
                        genericTerms=LanguageString(
                            fi="generic_terms_fi",
                            sv="generic_terms_sv",
                            en="generic_terms_en",
                        ),
                        paymentTerms=LanguageString(
                            fi="payment_terms_fi",
                            sv="payment_terms_sv",
                            en="payment_terms_en",
                        ),
                        specificTerms=LanguageString(
                            fi="specific_terms_fi",
                            sv="specific_terms_sv",
                            en="specific_terms_en",
                        ),
                        responsibleContactInfo=LanguageString(
                            fi="responsible_contact_info_fi",
                            sv="responsible_contact_info_sv",
                            en="responsible_contact_info_en",
                        ),
                        externalReservationUrl=None,
                    ),
                ],
                "tprek:59763": [
                    Resource(
                        id="aweyzvgot72q",
                        name=LanguageString(
                            fi="Ala-Malmin puisto",
                            sv="Nedre Malms park",
                            en="Ala-Malmin puisto park",
                        ),
                        description=LanguageString(
                            fi="test fi", sv="test sv", en="test en"
                        ),
                        type=ResourceType(
                            id="event_space",
                            mainType="space",
                            name=LanguageString(
                                fi="Tapahtumatila",
                                sv="Evenemangsutrymme",
                                en="Event space",
                            ),
                        ),
                        userPermissions=ResourceUserPermissions(
                            canMakeReservations=True
                        ),
                        reservable=True,
                        reservationInfo=None,
                        genericTerms=LanguageString(
                            fi="info fi", sv="info sv", en="info en"
                        ),
                        paymentTerms=None,
                        specificTerms=LanguageString(
                            fi="testi", sv="testi", en="testi"
                        ),
                        responsibleContactInfo=LanguageString(
                            fi="Yhteissähköposti: ulkoilma@hel.fi",
                            sv="Yhteissähköposti: ulkoilma@hel.fi",
                            en="Yhteissähköposti: ulkoilma@hel.fi",
                        ),
                        externalReservationUrl="https://tilavaraus.hel.fi/reservation-unit/479",
                    )
                ],
            },
        ),
    ],
)
def test_get_unit_id_to_resources_mapping(use_fallback_languages, expected_result):
    assert get_unit_id_to_resources_mapping(use_fallback_languages) == expected_result

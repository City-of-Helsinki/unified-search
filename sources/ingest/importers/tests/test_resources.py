import pytest

from ingest.importers.location.dataclasses import (
    Resource,
    ResourceType,
    ResourceUserPermissions,
)
from ingest.importers.location.utils import get_unit_id_to_resources_mapping
from ingest.importers.utils.shared import LanguageString

MOCKED_RESPA_RESOURCE_RESPONSE = {
    "count": 3,
    "next": None,
    "previous": None,
    "results": [
        {
            "id": "axayciqmqfja",
            "type": {
                "name": {
                    "fi": "Liikuntapaikka",
                    "en": "Sports field",
                    "sv": "Idrottsplats",
                },
                "main_type": "space",
                "id": "awqjgibywfvq",
            },
            "user_permissions": {
                "can_make_reservations": True,
            },
            "generic_terms": {"fi": "terms fi", "en": "terms en", "sv": "terms sv"},
            "payment_terms": {
                "fi": "payment_terms_fi",
                "en": "payment_terms_en",
                "sv": "payment_terms_sv",
            },
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
            "external_reservation_url": None,
            "unit": "tprek:42086",
        },
        {
            "id": "axaxxck4ub7a",
            "type": {
                "name": {
                    "fi": "Liikuntapaikka",
                    "en": "Sports field",
                    "sv": "Idrottsplats",
                },
                "main_type": "space",
                "id": "awqjgibywfvq",
            },
            "user_permissions": {
                "can_make_reservations": True,
            },
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
            "external_reservation_url": None,
            "unit": "tprek:42086",
        },
        {
            "id": "aweyzvgot72q",
            "type": {
                "name": {
                    "fi": "Tapahtumatila",
                    "en": "Event space",
                    "sv": "Evenemangsutrymme",
                },
                "main_type": "space",
                "id": "event_space",
            },
            "user_permissions": {
                "can_make_reservations": True,
            },
            "generic_terms": {"fi": "info fi", "en": "info en", "sv": "info sv"},
            "payment_terms": "",
            "name": {
                "fi": "Ala-Malmin puisto",
                "en": "Ala-Malmin puisto park",
                "sv": "Nedre Malms park",
            },
            "description": {"fi": "test fi", "en": "test en", "sv": "test sv"},
            "reservable": True,
            "reservation_info": None,
            "responsible_contact_info": {"fi": "Yhteissähköposti: ulkoilma@hel.fi"},
            "specific_terms": {"fi": "testi"},
            "external_reservation_url": "https://tilavaraus.hel.fi/reservation-unit/479",
            "unit": "tprek:59763",
        },
        {
            "id": "axi7463oupta",
            "type": {
                "name": {"fi": "Työpiste", "en": "Workstation", "sv": "Arbetsstation"},
                "main_type": "space",
                "id": "workstation",
            },
            "user_permissions": {
                "can_make_reservations": True,
            },
            "generic_terms": {"fi": "info fi", "en": "info en", "sv": "info sv"},
            "payment_terms": "",
            "name": {"fi": "Ompelukone (Brother RL425)"},
            "description": {"fi": "Ompelukone Brother RL425"},
            "reservable": True,
            "reservation_info": {
                "fi": "Sinulla voi olla yksi voimassa oleva ompelukonevaraus kerrallaan."
            },
            "responsible_contact_info": {"fi": "test@example.org"},
            "specific_terms": None,
            "external_reservation_url": None,
            "unit": "awtrnbtl2wca",
        },
    ],
}


@pytest.fixture(scope="module", autouse=True)
def mocked_respa_resource_response(module_mocker):
    return module_mocker.patch(
        "ingest.importers.location.utils.request_json",
        return_value=MOCKED_RESPA_RESOURCE_RESPONSE,
    )


@pytest.mark.parametrize(
    "use_fallback_languages,expected_result",
    [
        (
            False,
            {
                "42086": [
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
                "59763": [
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
                "awtrnbtl2wca": [
                    Resource(
                        id="axi7463oupta",
                        name=LanguageString(
                            fi="Ompelukone (Brother RL425)", sv=None, en=None
                        ),
                        description=LanguageString(
                            fi="Ompelukone Brother RL425", sv=None, en=None
                        ),
                        type=ResourceType(
                            id="workstation",
                            mainType="space",
                            name=LanguageString(
                                fi="Työpiste", sv="Arbetsstation", en="Workstation"
                            ),
                        ),
                        userPermissions=ResourceUserPermissions(
                            canMakeReservations=True
                        ),
                        reservable=True,
                        reservationInfo=LanguageString(
                            fi="Sinulla voi olla yksi voimassa oleva ompelukonevaraus kerrallaan.",
                            sv=None,
                            en=None,
                        ),
                        genericTerms=LanguageString(
                            fi="info fi", sv="info sv", en="info en"
                        ),
                        paymentTerms=None,
                        specificTerms=None,
                        responsibleContactInfo=LanguageString(
                            fi="test@example.org", sv=None, en=None
                        ),
                        externalReservationUrl=None,
                    )
                ],
            },
        ),
        (
            True,
            {
                "42086": [
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
                "59763": [
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
                "awtrnbtl2wca": [
                    Resource(
                        id="axi7463oupta",
                        name=LanguageString(
                            fi="Ompelukone (Brother RL425)",
                            sv="Ompelukone (Brother RL425)",
                            en="Ompelukone (Brother RL425)",
                        ),
                        description=LanguageString(
                            fi="Ompelukone Brother RL425",
                            sv="Ompelukone Brother RL425",
                            en="Ompelukone Brother RL425",
                        ),
                        type=ResourceType(
                            id="workstation",
                            mainType="space",
                            name=LanguageString(
                                fi="Työpiste", sv="Arbetsstation", en="Workstation"
                            ),
                        ),
                        userPermissions=ResourceUserPermissions(
                            canMakeReservations=True
                        ),
                        reservable=True,
                        reservationInfo=LanguageString(
                            fi="Sinulla voi olla yksi voimassa oleva ompelukonevaraus kerrallaan.",
                            sv="Sinulla voi olla yksi voimassa oleva ompelukonevaraus kerrallaan.",
                            en="Sinulla voi olla yksi voimassa oleva ompelukonevaraus kerrallaan.",
                        ),
                        genericTerms=LanguageString(
                            fi="info fi", sv="info sv", en="info en"
                        ),
                        paymentTerms=None,
                        specificTerms=None,
                        responsibleContactInfo=LanguageString(
                            fi="test@example.org",
                            sv="test@example.org",
                            en="test@example.org",
                        ),
                        externalReservationUrl=None,
                    )
                ],
            },
        ),
    ],
)
def test_get_unit_id_to_resources_mapping(use_fallback_languages, expected_result):
    assert get_unit_id_to_resources_mapping(use_fallback_languages) == expected_result

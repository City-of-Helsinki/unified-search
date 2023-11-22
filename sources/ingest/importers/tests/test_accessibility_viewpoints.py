from typing import Dict, List, Optional

import pytest

from ingest.importers.location.dataclasses import AccessibilityViewpoint
from ingest.importers.location.utils import (
    get_accessibility_viewpoint_id_to_name_mapping,
    get_accessibility_viewpoint_id_to_value_mapping,
    get_enriched_accessibility_viewpoints,
)
from ingest.importers.utils.shared import LanguageString

MOCKED_SERVICE_MAP_ACCESSIBILITY_VIEWPOINT_RESPONSE = [
    {
        "id": "00",
        "name_fi": "Valitse esteettömyysnäkökulma (Testi)",
        "name_sv": "Välj tillgänglighetsperspektiv (Test)",
        "name_en": "Choose accessibility perspective (Test)",
        "values": ["unknown"],
    },
    {
        "id": "11",
        "name_fi": "Olen pyörätuolin käyttäjä",
        "name_sv": "Jag är en rullstolsanvändare",
        "name_en": "I am a wheelchair user",
        "values": ["unknown", "green", "red"],
    },
    {
        "id": "12",
        "name_fi": "Olen pyörätuolin käyttäjä - saavun omalla autolla",
        "name_sv": "Jag är en rullstolsanvändare - kommer med min egen bil",
        "name_en": "I am a wheelchair user - arrive by my car",
        "values": ["unknown", "green", "red"],
    },
    {
        "id": "13",
        "name_fi": "Olen pyörätuolin käyttäjä - saavun saattoliikenteellä",
        "name_sv": "Jag är en rullstolsanvändare - kommer med angöringstrafik",
        "name_en": "I am a wheelchair user - arrive with pick-up and drop-off traffic",
        "values": ["unknown", "green", "red"],
    },
    {
        "id": "21",
        "name_fi": "Olen liikkumisesteinen, mutta kävelen",
        "name_sv": "Jag är rörelsehindrad, men jag går",
        "name_en": "I have reduced mobility, but I walk",
        "values": ["unknown", "green", "red"],
    },
    {
        "id": "22",
        "name_fi": "Olen liikkumisesteinen, mutta kävelen - saavun omalla autolla",
        "name_sv": "Jag är rörelsehindrad, men jag går - kommer med min egen bil",
        "name_en": "I have reduced mobility, but I walk - arrive by my car",
        "values": ["unknown", "green", "red"],
    },
    {
        "id": "23",
        "name_fi": "Olen liikkumisesteinen, mutta kävelen - saavun saattoliikenteellä",
        "name_sv": "Jag är rörelsehindrad, men jag går - kommer med angöringstrafik",
        "name_en": "I have reduced mobility, but I walk - arrive with pick-up and drop-off traffic",
        "values": ["unknown", "green", "red"],
    },
    {
        "id": "31",
        "name_fi": "Olen rollaattorin käyttäjä",
        "name_sv": "Jag är en rollatoranvändare",
        "name_en": "I am a rollator user",
        "values": ["unknown", "green", "red"],
    },
    {
        "id": "32",
        "name_fi": "Olen rollaattorin käyttäjä - saavun omalla autolla",
        "name_sv": "Jag är en rollatoranvändare - kommer med min egen bil",
        "name_en": "I am a rollator user - arrive by my car",
        "values": ["unknown", "green", "red"],
    },
    {
        "id": "33",
        "name_fi": "Olen rollaattorin käyttäjä - saavun saattoliikenteellä",
        "name_sv": "Jag är en rollatoranvändare - kommer med angöringstrafik",
        "name_en": "I am a rollator user - arrive with pick-up and drop-off traffic",
        "values": ["unknown", "green", "red"],
    },
    {
        "id": "41",
        "name_fi": "Minulla on lastenvaunut",
        "name_sv": "Jag är en barnvagnsdragare",
        "name_en": "I am a stroller pusher",
        "values": ["unknown", "green", "red"],
    },
    {
        "id": "51",
        "name_fi": "Olen näkövammainen",
        "name_sv": "Jag är synskadad",
        "name_en": "I am visually impaired",
        "values": ["unknown", "green", "red"],
    },
    {
        "id": "52",
        "name_fi": "Olen näkövammainen - saavun saattoliikenteellä",
        "name_sv": "Jag är synskadad - kommer med angöringstrafik",
        "name_en": "I am visually impaired - arrive with pick-up and drop-off traffic",
        "values": ["unknown", "green", "red"],
    },
    {
        "id": "61",
        "name_fi": "Käytän kuulolaitetta",
        "name_sv": "Jag använder en hörapparat",
        "name_en": "I use a hearing aid",
        "values": ["unknown", "green", "red"],
    },
]


@pytest.fixture(scope="module", autouse=True)
def mocked_service_map_accessibility_viewpoint_response(module_mocker):
    return module_mocker.patch(
        "ingest.importers.location.utils.request_json",
        return_value=MOCKED_SERVICE_MAP_ACCESSIBILITY_VIEWPOINT_RESPONSE,
    )


@pytest.mark.parametrize(
    "accessibility_viewpoints,expected_result",
    [
        (None, {}),
        ("", {}),
        ("23:green", {"23": "green"}),
        ("00:unknown,11:red", {"00": "unknown", "11": "red"}),
        (
            "00:unknown,11:green,12:green,61:red",
            {"00": "unknown", "11": "green", "12": "green", "61": "red"},
        ),
    ],
)
def test_get_accessibility_viewpoint_id_to_value_mapping(
    accessibility_viewpoints: Optional[str],
    expected_result: Dict[str, str],
):
    assert (
        get_accessibility_viewpoint_id_to_value_mapping(accessibility_viewpoints)
        == expected_result
    )


@pytest.mark.parametrize(
    "accessibility_viewpoints,omit_unknowns,expected_result",
    [
        (None, False, []),
        ("", False, []),
        (
            "11:red,21:green,61:unknown",
            True,
            [
                AccessibilityViewpoint(
                    id="11",
                    name=LanguageString(
                        fi="Olen pyörätuolin käyttäjä",
                        sv="Jag är en rullstolsanvändare",
                        en="I am a wheelchair user",
                    ),
                    value="red",
                ),
                AccessibilityViewpoint(
                    id="21",
                    name=LanguageString(
                        fi="Olen liikkumisesteinen, mutta kävelen",
                        sv="Jag är rörelsehindrad, men jag går",
                        en="I have reduced mobility, but I walk",
                    ),
                    value="green",
                ),
            ],
        ),
        (
            "00:unknown,21:green,52:unknown",
            False,
            [
                AccessibilityViewpoint(
                    id="00",
                    name=LanguageString(
                        fi="Valitse esteettömyysnäkökulma (Testi)",
                        sv="Välj tillgänglighetsperspektiv (Test)",
                        en="Choose accessibility perspective (Test)",
                    ),
                    value="unknown",
                ),
                AccessibilityViewpoint(
                    id="21",
                    name=LanguageString(
                        fi="Olen liikkumisesteinen, mutta kävelen",
                        sv="Jag är rörelsehindrad, men jag går",
                        en="I have reduced mobility, but I walk",
                    ),
                    value="green",
                ),
                AccessibilityViewpoint(
                    id="52",
                    name=LanguageString(
                        fi="Olen näkövammainen - saavun saattoliikenteellä",
                        sv="Jag är synskadad - kommer med angöringstrafik",
                        en="I am visually impaired - arrive with pick-up and drop-off traffic",
                    ),
                    value="unknown",
                ),
            ],
        ),
    ],
)
def test_get_enriched_accessibility_viewpoints(
    accessibility_viewpoints: Optional[str],
    omit_unknowns: bool,
    expected_result: List[AccessibilityViewpoint],
):
    assert (
        get_enriched_accessibility_viewpoints(
            accessibility_viewpoints,
            get_accessibility_viewpoint_id_to_name_mapping(use_fallback_languages=True),
            omit_unknowns,
        )
        == expected_result
    )


@pytest.mark.parametrize("use_fallback_languages", [False, True])
def test_get_accessibility_viewpoint_id_to_name_mapping(use_fallback_languages: bool):
    assert get_accessibility_viewpoint_id_to_name_mapping(use_fallback_languages) == {
        "00": LanguageString(
            fi="Valitse esteettömyysnäkökulma (Testi)",
            sv="Välj tillgänglighetsperspektiv (Test)",
            en="Choose accessibility perspective (Test)",
        ),
        "11": LanguageString(
            fi="Olen pyörätuolin käyttäjä",
            sv="Jag är en rullstolsanvändare",
            en="I am a wheelchair user",
        ),
        "12": LanguageString(
            fi="Olen pyörätuolin käyttäjä - saavun omalla autolla",
            sv="Jag är en rullstolsanvändare - kommer med min egen bil",
            en="I am a wheelchair user - arrive by my car",
        ),
        "13": LanguageString(
            fi="Olen pyörätuolin käyttäjä - saavun saattoliikenteellä",
            sv="Jag är en rullstolsanvändare - kommer med angöringstrafik",
            en="I am a wheelchair user - arrive with pick-up and drop-off traffic",
        ),
        "21": LanguageString(
            fi="Olen liikkumisesteinen, mutta kävelen",
            sv="Jag är rörelsehindrad, men jag går",
            en="I have reduced mobility, but I walk",
        ),
        "22": LanguageString(
            fi="Olen liikkumisesteinen, mutta kävelen - saavun omalla autolla",
            sv="Jag är rörelsehindrad, men jag går - kommer med min egen bil",
            en="I have reduced mobility, but I walk - arrive by my car",
        ),
        "23": LanguageString(
            fi="Olen liikkumisesteinen, mutta kävelen - saavun saattoliikenteellä",
            sv="Jag är rörelsehindrad, men jag går - kommer med angöringstrafik",
            en="I have reduced mobility, but I walk - arrive with pick-up and drop-off traffic",
        ),
        "31": LanguageString(
            fi="Olen rollaattorin käyttäjä",
            sv="Jag är en rollatoranvändare",
            en="I am a rollator user",
        ),
        "32": LanguageString(
            fi="Olen rollaattorin käyttäjä - saavun omalla autolla",
            sv="Jag är en rollatoranvändare - kommer med min egen bil",
            en="I am a rollator user - arrive by my car",
        ),
        "33": LanguageString(
            fi="Olen rollaattorin käyttäjä - saavun saattoliikenteellä",
            sv="Jag är en rollatoranvändare - kommer med angöringstrafik",
            en="I am a rollator user - arrive with pick-up and drop-off traffic",
        ),
        "41": LanguageString(
            fi="Minulla on lastenvaunut",
            sv="Jag är en barnvagnsdragare",
            en="I am a stroller pusher",
        ),
        "51": LanguageString(
            fi="Olen näkövammainen", sv="Jag är synskadad", en="I am visually impaired"
        ),
        "52": LanguageString(
            fi="Olen näkövammainen - saavun saattoliikenteellä",
            sv="Jag är synskadad - kommer med angöringstrafik",
            en="I am visually impaired - arrive with pick-up and drop-off traffic",
        ),
        "61": LanguageString(
            fi="Käytän kuulolaitetta",
            sv="Jag använder en hörapparat",
            en="I use a hearing aid",
        ),
    }

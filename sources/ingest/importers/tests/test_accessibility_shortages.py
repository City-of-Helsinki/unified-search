import pytest

from ingest.importers.location.dataclasses import Accessibility, AccessibilityViewpoint
from ingest.importers.location.utils import (
    get_unit_id_to_accessibility_viewpoint_shortages_mapping,
)
from ingest.importers.utils.shared import LanguageString
from ingest.importers.tests.mocks import (
    MOCKED_SERVICE_MAP_ACCESSIBILITY_SHORTAGE_VIEWPOINT_RESPONSE,
)


@pytest.fixture
def mocked_service_map_accessibility_shortage_viewpoint_response(mocker):
    return mocker.patch(
        "ingest.importers.location.utils.request_json",
        return_value=MOCKED_SERVICE_MAP_ACCESSIBILITY_SHORTAGE_VIEWPOINT_RESPONSE,
    )


def test_get_unit_id_to_accessibility_shortcomings_mapping(
    mocked_service_map_accessibility_shortage_viewpoint_response,
):
    assert get_unit_id_to_accessibility_viewpoint_shortages_mapping(
        use_fallback_languages=False
    ) == {
        "16": {
            "33": [
                LanguageString(
                    fi="Toimipisteessä ei ole esteetöntä wc:tä.",
                    sv="Det finns ingen tillgänglig toalett i verksamhetsstället.",
                    en="The facility does not have an accessible toilet.",
                )
            ]
        },
        "2": {
            "21": [
                LanguageString(
                    fi="Ei puutteita.", sv="Inga brister.", en="No shortcomings."
                )
            ],
            "32": [
                LanguageString(
                    fi="Esteettömiä autopaikkoja ei ole.",
                    sv="Inga p-platser för personer med rörelsehinder.",
                    en="No parking places for persons with a disability.",
                ),
                LanguageString(
                    fi="Sisäänkäynnissä on ahdas tuulikaappi.",
                    sv="Det finns ett trångt vindfång vid ingången.",
                    en="The entrance has a cramped foyer.",
                ),
            ],
        },
    }


def test_set_accessibility_shortages(
    mocked_service_map_accessibility_shortage_viewpoint_response,
):
    accessibility = Accessibility(
        email="",
        phone="",
        www="",
        viewpoints=[
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
                id="32",
                name=LanguageString(
                    fi="Olen rollaattorin käyttäjä - saavun omalla autolla",
                    sv="Jag är en rollatoranvändare - kommer med min egen bil",
                    en="I am a rollator user - arrive by my car",
                ),
                value="red",
            ),
        ],
        sentences=[],
        shortcomings=[],
    )
    viewpoint_id_to_shortages = {
        "21": [
            LanguageString(
                fi="Ei puutteita.", sv="Inga brister.", en="No shortcomings."
            )
        ],
        "32": [
            LanguageString(
                fi="Esteettömiä autopaikkoja ei ole.",
                sv="Inga p-platser för personer med rörelsehinder.",
                en="No parking places for persons with a disability.",
            ),
            LanguageString(
                fi="Sisäänkäynnissä on ahdas tuulikaappi.",
                sv="Det finns ett trångt vindfång vid ingången.",
                en="The entrance has a cramped foyer.",
            ),
        ],
    }
    accessibility.set_accessibility_shortages(viewpoint_id_to_shortages)
    assert accessibility.viewpoints[0].shortages == [
        LanguageString(fi="Ei puutteita.", sv="Inga brister.", en="No shortcomings.")
    ]
    assert accessibility.viewpoints[1].shortages == [
        LanguageString(
            fi="Esteettömiä autopaikkoja ei ole.",
            sv="Inga p-platser för personer med rörelsehinder.",
            en="No parking places for persons with a disability.",
        ),
        LanguageString(
            fi="Sisäänkäynnissä on ahdas tuulikaappi.",
            sv="Det finns ett trångt vindfång vid ingången.",
            en="The entrance has a cramped foyer.",
        ),
    ]
    accessibility.set_accessibility_shortages({})
    assert all(not viewpoint.shortages for viewpoint in accessibility.viewpoints)
    accessibility.set_accessibility_shortages(
        {"inexistent_viewpoint_id": [LanguageString(fi="Test", sv="Test", en="Test")]}
    )
    assert all(not viewpoint.shortages for viewpoint in accessibility.viewpoints)

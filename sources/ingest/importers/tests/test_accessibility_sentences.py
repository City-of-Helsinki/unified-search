import pytest

from ..location import (
    AccessibilitySentence,
    get_unit_id_to_accessibility_sentences_mapping,
)
from ..utils import LanguageString

MOCKED_SERVICE_MAP_ACCESSIBILITY_SENTENCE_VIEWPOINT_RESPONSE = [
    {
        "unit_id": 6365,
        "sentence_group_name": "Kulkureitti pääsisäänkäynnille",
        "sentence_group_fi": "Reitti pääsisäänkäynnille",
        "sentence_group_sv": "Rutten till huvudingången",
        "sentence_group_en": "The route to the main entrance",
        "sentence_fi": "Kulkureitti sisäänkäynnille on tasainen ja riittävän leveä sekä valaistu.",
        "sentence_sv": "Rutten till ingången är jämn och tillräckligt bred samt belyst.",
        "sentence_en": "The route to the entrance is smooth and sufficiently wide and illuminated.",
    },
    {
        "unit_id": 6365,
        "sentence_group_name": "Pääsisäänkäynti",
        "sentence_group_fi": "Pääsisäänkäynti",
        "sentence_group_sv": "Huvudingången",
        "sentence_group_en": "The main entrance",
        "sentence_fi": "Sisäänkäynti sijaitsee syvennyksessä ja on valaistu.",
        "sentence_sv": "Ingången är belägen i en nisch och belyst.",
        "sentence_en": "The entrance is located in a recess and is illuminated.",
    },
    {
        "unit_id": 1414,
        "sentence_group_name": "Sisätilat",
        "sentence_group_fi": "Sisätilat",
        "sentence_group_sv": "I lokalen",
        "sentence_fi": "Toimipisteessä on esteetön wc.",
        "sentence_sv": "I verksamhetslokalen finns en tillgänglig toalett.",
    },
]


@pytest.fixture
def mocked_service_map_accessibility_sentence_viewpoint_response(mocker):
    return mocker.patch(
        "ingest.importers.location.request_json",
        return_value=MOCKED_SERVICE_MAP_ACCESSIBILITY_SENTENCE_VIEWPOINT_RESPONSE,
    )


@pytest.mark.parametrize(
    "use_fallback_languages,expected_result",
    [
        (
            False,
            {
                "1414": [
                    AccessibilitySentence(
                        sentenceGroupName="Sisätilat",
                        sentenceGroup=LanguageString(
                            fi="Sisätilat", sv="I lokalen", en=None
                        ),
                        sentence=LanguageString(
                            fi="Toimipisteessä on esteetön wc.",
                            sv="I verksamhetslokalen finns en tillgänglig toalett.",
                            en=None,
                        ),
                    )
                ],
                "6365": [
                    AccessibilitySentence(
                        sentenceGroupName="Kulkureitti pääsisäänkäynnille",
                        sentenceGroup=LanguageString(
                            fi="Reitti pääsisäänkäynnille",
                            sv="Rutten till huvudingången",
                            en="The route to the main entrance",
                        ),
                        sentence=LanguageString(
                            fi="Kulkureitti sisäänkäynnille on tasainen ja riittävän leveä sekä valaistu.",
                            sv="Rutten till ingången är jämn och tillräckligt bred samt belyst.",
                            en="The route to the entrance is smooth and sufficiently wide and illuminated.",
                        ),
                    ),
                    AccessibilitySentence(
                        sentenceGroupName="Pääsisäänkäynti",
                        sentenceGroup=LanguageString(
                            fi="Pääsisäänkäynti",
                            sv="Huvudingången",
                            en="The main entrance",
                        ),
                        sentence=LanguageString(
                            fi="Sisäänkäynti sijaitsee syvennyksessä ja on valaistu.",
                            sv="Ingången är belägen i en nisch och belyst.",
                            en="The entrance is located in a recess and is illuminated.",
                        ),
                    ),
                ],
            },
        ),
        (
            True,
            {
                "1414": [
                    AccessibilitySentence(
                        sentenceGroupName="Sisätilat",
                        sentenceGroup=LanguageString(
                            fi="Sisätilat", sv="I lokalen", en="Sisätilat"
                        ),
                        sentence=LanguageString(
                            fi="Toimipisteessä on esteetön wc.",
                            sv="I verksamhetslokalen finns en tillgänglig toalett.",
                            en="Toimipisteessä on esteetön wc.",
                        ),
                    )
                ],
                "6365": [
                    AccessibilitySentence(
                        sentenceGroupName="Kulkureitti pääsisäänkäynnille",
                        sentenceGroup=LanguageString(
                            fi="Reitti pääsisäänkäynnille",
                            sv="Rutten till huvudingången",
                            en="The route to the main entrance",
                        ),
                        sentence=LanguageString(
                            fi="Kulkureitti sisäänkäynnille on tasainen ja riittävän leveä sekä valaistu.",
                            sv="Rutten till ingången är jämn och tillräckligt bred samt belyst.",
                            en="The route to the entrance is smooth and sufficiently wide and illuminated.",
                        ),
                    ),
                    AccessibilitySentence(
                        sentenceGroupName="Pääsisäänkäynti",
                        sentenceGroup=LanguageString(
                            fi="Pääsisäänkäynti",
                            sv="Huvudingången",
                            en="The main entrance",
                        ),
                        sentence=LanguageString(
                            fi="Sisäänkäynti sijaitsee syvennyksessä ja on valaistu.",
                            sv="Ingången är belägen i en nisch och belyst.",
                            en="The entrance is located in a recess and is illuminated.",
                        ),
                    ),
                ],
            },
        ),
    ],
)
def test_get_unit_id_to_accessibility_shortcomings_mapping(
    mocked_service_map_accessibility_sentence_viewpoint_response,
    use_fallback_languages,
    expected_result,
):
    assert (
        get_unit_id_to_accessibility_sentences_mapping(use_fallback_languages)
        == expected_result
    )

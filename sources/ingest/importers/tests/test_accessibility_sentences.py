import pytest

from ingest.importers.location.dataclasses import AccessibilitySentence
from ingest.importers.location.utils import (
    get_unit_id_to_accessibility_sentences_mapping,
)
from ingest.importers.utils.shared import LanguageString


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

import pytest

from ingest.importers.utils import LanguageString, LanguageStringConverter


@pytest.mark.parametrize(
    "input,field_name,expected_output",
    [
        (
            {"foo_fi": "kissa", "foo_en": "cat", "foo_sv": "katt"},
            "foo",
            LanguageString(fi="kissa", sv="katt", en="cat"),
        ),
        (
            {"foo_fi": "kissa", "foo_en": "cat", "bar_fi": "koira"},
            "foo",
            LanguageString(fi="kissa", sv=None, en="cat"),
        ),
        (
            {"foo_fi": "kissa", "bar_fi": "koira"},
            "foo",
            LanguageString(fi="kissa", sv=None, en=None),
        ),
        (
            {"bar_fi": "koira"},
            "foo",
            None,
        ),
        (
            {"foo_fi": "kissa", "bar": {"fi": "koira", "sv": "hund", "en": "dog"}},
            "bar",
            LanguageString(fi="koira", sv="hund", en="dog"),
        ),
        (
            {"foo_fi": "kissa", "bar": {"fi": "koira"}, "foz": None},
            "foo",
            LanguageString(fi="kissa", sv=None, en=None),
        ),
        (
            {"foo_fi": "kissa", "bar": {"fi": "koira"}, "foz": None},
            "bar",
            LanguageString(fi="koira", sv=None, en=None),
        ),
        ({"foo_fi": "kissa", "bar": {"fi": "koira"}, "foz": None}, "baz", None),
        ({"foo_fi": "kissa", "bar": {"fi": "koira"}, "foz": None}, "foz", None),
    ],
)
def test_get_language_string_without_fallback_languages(
    input, field_name, expected_output
):
    converter1 = LanguageStringConverter(input)
    converter2 = LanguageStringConverter(input, False)
    converter3 = LanguageStringConverter(input, use_fallback_languages=False)

    assert converter1.get_language_string(field_name) == expected_output
    assert converter2.get_language_string(field_name) == expected_output
    assert converter3.get_language_string(field_name) == expected_output


@pytest.mark.parametrize(
    "input,field_name,expected_output",
    [
        (
            {"foo_fi": "kissa", "foo_en": "cat", "foo_sv": "katt"},
            "foo",
            LanguageString(fi="kissa", sv="katt", en="cat"),
        ),
        (
            {"foo_fi": "kissa", "foo_en": "cat", "bar_fi": "koira"},
            "foo",
            LanguageString(fi="kissa", sv="cat", en="cat"),
        ),
        (
            {"foo_fi": "kissa", "bar_fi": "koira"},
            "foo",
            LanguageString(fi="kissa", sv="kissa", en="kissa"),
        ),
        (
            {"bar_fi": "koira"},
            "foo",
            None,
        ),
        (
            {"foo_fi": "kissa", "bar": {"fi": "koira", "sv": "hund", "en": "dog"}},
            "bar",
            LanguageString(fi="koira", sv="hund", en="dog"),
        ),
        (
            {"foo_fi": "kissa", "bar": {"fi": "koira"}, "foz": None},
            "foo",
            LanguageString(fi="kissa", sv="kissa", en="kissa"),
        ),
        (
            {"foo_fi": "kissa", "bar": {"fi": "koira"}, "foz": None},
            "bar",
            LanguageString(fi="koira", sv="koira", en="koira"),
        ),
        ({"foo_fi": "kissa", "bar": {"fi": "koira"}, "foz": None}, "baz", None),
        ({"foo_fi": "kissa", "bar": {"fi": "koira"}, "foz": None}, "foz", None),
        (
            {"foo_fi": "kissa", "foo_en": "cat", "foo_sv": "katt"},
            "foo",
            LanguageString(fi="kissa", sv="katt", en="cat"),
        ),
        (
            {"foo_fi": "kissa"},
            "foo",
            LanguageString(fi="kissa", sv="kissa", en="kissa"),
        ),
        (
            {"foo_en": "cat"},
            "foo",
            LanguageString(fi="cat", sv="cat", en="cat"),
        ),
        (
            {"foo_sv": "katt"},
            "foo",
            LanguageString(fi="katt", sv="katt", en="katt"),
        ),
        (
            {"foo_fi": "kissa", "foo_en": "cat"},
            "foo",
            LanguageString(fi="kissa", sv="cat", en="cat"),
        ),
        (
            {"foo_fi": "kissa", "foo_sv": "katt"},
            "foo",
            LanguageString(fi="kissa", sv="katt", en="kissa"),
        ),
        (
            {"foo_sv": "katt", "foo_en": "cat"},
            "foo",
            LanguageString(fi="cat", sv="katt", en="cat"),
        ),
        (
            {"foo_fi": "kissa", "foo_en": "", "foo_sv": "katt"},
            "foo",
            LanguageString(fi="kissa", sv="katt", en="kissa"),
        ),
        (
            {"foo_fi": "kissa", "foo_en": None, "foo_sv": "katt"},
            "foo",
            LanguageString(fi="kissa", sv="katt", en="kissa"),
        ),
        (
            {"foo_fi": "", "foo_en": "cat", "foo_sv": "katt"},
            "foo",
            LanguageString(fi="cat", sv="katt", en="cat"),
        ),
        (
            {"foo_fi": None, "foo_en": "cat", "foo_sv": "katt"},
            "foo",
            LanguageString(fi="cat", sv="katt", en="cat"),
        ),
        (
            {"foo_fi": "kissa", "foo_en": "cat", "foo_sv": ""},
            "foo",
            LanguageString(fi="kissa", sv="cat", en="cat"),
        ),
        (
            {"foo_fi": "kissa", "foo_en": "cat", "foo_sv": None},
            "foo",
            LanguageString(fi="kissa", sv="cat", en="cat"),
        ),
    ],
)
def test_get_language_string_with_fallback_languages(
    input, field_name, expected_output
):
    converter1 = LanguageStringConverter(input, True)
    converter2 = LanguageStringConverter(input, use_fallback_languages=True)

    assert converter1.get_language_string(field_name) == expected_output
    assert converter2.get_language_string(field_name) == expected_output

from django.test import TestCase

from ingest.importers.utils import LanguageString, LanguageStringConverter


class LanguageTestCase(TestCase):
    def test_postfixed(self):
        """Test postfixed keys"""

        input = {"foo_fi": "kissa", "foo_en": "cat", "foo_sv": "katt"}

        l = LanguageStringConverter(input)
        self.assertEqual(
            l.get_language_string("foo"),
            LanguageString(fi="kissa", sv="katt", en="cat"),
        )

        input = {"foo_fi": "kissa", "foo_en": "cat", "bar_fi": "koira"}

        l = LanguageStringConverter(input)
        self.assertEqual(
            l.get_language_string("foo"), LanguageString(fi="kissa", sv=None, en="cat")
        )

        input = {"foo_fi": "kissa", "bar_fi": "koira"}

        l = LanguageStringConverter(input)
        self.assertEqual(
            l.get_language_string("foo"), LanguageString(fi="kissa", sv=None, en=None)
        )

        input = {"bar_fi": "koira"}

        l = LanguageStringConverter(input)
        self.assertEqual(l.get_language_string("foo"), None)

    def test_sub_fields(self):
        """Test sub fields"""

        input = {"foo_fi": "kissa", "bar": {"fi": "koira", "sv": "hund", "en": "dog"}}

        l = LanguageStringConverter(input)
        self.assertEqual(
            l.get_language_string("bar"),
            LanguageString(fi="koira", sv="hund", en="dog"),
        )

        input = {
            "foo_fi": "kissa",
            "bar": {
                "fi": "koira",
            },
            "foz": None,
        }

        l = LanguageStringConverter(input)
        self.assertEqual(
            l.get_language_string("foo"), LanguageString(fi="kissa", sv=None, en=None)
        )
        self.assertEqual(
            l.get_language_string("bar"), LanguageString(fi="koira", sv=None, en=None)
        )
        self.assertEqual(l.get_language_string("baz"), None)
        self.assertEqual(l.get_language_string("foz"), None)

    def test_language_string_text(self):
        input = {"foo_fi": "kissa", "bar_fi": "koira"}
        l = LanguageStringConverter(input)
        assert l.get_language_string("foo").text == input["foo_fi"]

    def test_language_string_default_language(self):
        input = {"foo_fi": "kissa", "bar_fi": "koira"}
        l = LanguageStringConverter(input)
        assert l.get_language_string("foo").defaultLanguage == "FI"

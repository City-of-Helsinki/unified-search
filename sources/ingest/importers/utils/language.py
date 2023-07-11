from .shared import LanguageString


class LanguageStringConverter:
    """Helper class for creating language strings from various input formats.

    The type used for storing multilanguage fields is following:

        @dataclass
        class LanguageString:
            fi: str
            sv: str
            en: str

    Input may be received in various forms:

    1. Sub fields for language, possibly missing or empty fields

        "location_extra_info": {
            "fi": ""
        },

        "name": {
            "fi": "Maksutonta puistojumppaa Roihuvuoressa"
        },

        "price": {
            "fi": "20/10/5€",
            "en": "20/10/5€"
        }

    2. Flat fields including language in the field name

        "name_fi": "Roihuvuoren liikuntapuisto",
        "name_sv": "Kasbergets idrottspark",
        "name_en": "Roihuvuori sports park",

    """

    LANGUAGES = ("fi", "sv", "en")

    def __init__(self, input: dict, use_fallback_languages: bool = False):
        self.input = input
        self.use_fallback_languages = use_fallback_languages

    def has_postfixed_fields(self):
        expected = [self.field_name + "_" + lang for lang in self.LANGUAGES]
        return any([self.input.get(key, False) for key in expected])

    @staticmethod
    def get_fields_with_fallback_languages(fields: dict) -> dict:
        return {
            lang: (
                fields.get(lang, None)
                or fields.get("fi", None)  # Primary fallback language
                or fields.get("en", None)  # Secondary fallback language
                or fields.get("sv", None)  # Tertiary fallback language
            )
            for lang in fields.keys()
        }

    def get_postfixed_fields(self):
        result = {
            lang: self.input.get(self.field_name + "_" + lang, None)
            for lang in self.LANGUAGES
        }
        return (
            self.get_fields_with_fallback_languages(result)
            if self.use_fallback_languages
            else result
        )

    def get_sub_fields(self):
        result = {
            lang: self.input[self.field_name].get(lang, None) for lang in self.LANGUAGES
        }
        return (
            self.get_fields_with_fallback_languages(result)
            if self.use_fallback_languages
            else result
        )

    def get_language_string(self, field_name: str):
        self.field_name = field_name
        self.output = None

        if self.has_postfixed_fields():
            self.output = LanguageString(**self.get_postfixed_fields())
        elif self.field_name in self.input and self.input[self.field_name]:
            self.output = LanguageString(**self.get_sub_fields())

        return self.output

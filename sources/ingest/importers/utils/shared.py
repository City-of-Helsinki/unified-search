from dataclasses import dataclass
from typing import Union


@dataclass
class LanguageString:
    fi: str = None
    sv: str = None
    en: str = None
    text: str = None
    defaultLanguage: str = "FI"

    def __init__(self, **kwargs):
        self.fi = kwargs["fi"]
        self.sv = kwargs["sv"]
        self.en = kwargs["en"]
        self.text = kwargs[self.defaultLanguage.lower()]


@dataclass
class LinkedData:
    service: str = None
    origin_url: str = None
    raw_data: Union[dict, list] = None

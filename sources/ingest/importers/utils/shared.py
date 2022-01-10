from dataclasses import dataclass
from typing import Union


@dataclass
class LanguageString:
    fi: str = None
    sv: str = None
    en: str = None


@dataclass
class LinkedData:
    service: str = None
    origin_url: str = None
    raw_data: Union[dict, list] = None

from dataclasses import dataclass
from typing import Optional, Union


@dataclass(eq=True)
class LanguageString:
    fi: Optional[str] = None
    sv: Optional[str] = None
    en: Optional[str] = None

    def __hash__(self):
        return hash((self.fi, self.sv, self.en))


@dataclass
class LinkedData:
    service: str = None
    origin_url: str = None
    raw_data: Union[dict, list] = None

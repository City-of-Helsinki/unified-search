from dataclasses import dataclass
from typing import Optional


@dataclass(eq=True)
class LanguageString:
    fi: Optional[str] = None
    sv: Optional[str] = None
    en: Optional[str] = None

    def __hash__(self):
        return hash((self.fi, self.sv, self.en))


@dataclass
class LinkedData:
    service: str | None = None
    origin_url: str | None = None
    raw_data: dict | list | None = None

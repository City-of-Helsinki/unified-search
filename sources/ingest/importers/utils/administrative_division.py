from dataclasses import dataclass
from typing import List, Optional

from django.contrib.gis.geos import Point
from django.core.management import call_command
from django.db import transaction
from munigeo.models import AdministrativeDivision as AdministrativeDivisionModel

from .retry import retry_twice_5s_intervals
from .shared import LanguageString

DIVISION_TYPES = ("neighborhood", "district", "sub_district", "muni")


@dataclass
class AdministrativeDivision:
    id: str
    type: str
    municipality: Optional[str]
    name: LanguageString


def geo_import_finnish_municipalities():
    call_command("geo_import", "finland", "--municipalities")


def geo_import_helsinki_divisions():
    call_command("geo_import", "helsinki", "--divisions")


class AdministrativeDivisionFetcher:
    def __init__(self):
        with transaction.atomic():
            # NOTE: Not sure whether retry really works here, it depends on
            #       whether the command raises an exception that propagates here!
            retry_twice_5s_intervals(geo_import_finnish_municipalities)
            retry_twice_5s_intervals(geo_import_helsinki_divisions)

        self.administrative_divisions_qs = AdministrativeDivisionModel.objects.filter(
            type__type__in=DIVISION_TYPES
        ).prefetch_related("type", "translations")

    def get_all(self) -> List[AdministrativeDivision]:
        return self._get_data(self.administrative_divisions_qs)

    def get_by_coordinates(
        self, longitude: float, latitude: float
    ) -> List[AdministrativeDivision]:
        return self._get_data(
            self.administrative_divisions_qs.filter(
                geometry__boundary__contains=Point(longitude, latitude)
            )
        )

    def _get_data(self, administrative_divisions_qs) -> List[AdministrativeDivision]:
        return [
            AdministrativeDivision(
                id=db_division.ocd_id,
                type=db_division.type.type,
                municipality=db_division.municipality.safe_translation_getter(
                    "name", language_code="fi"
                )
                if db_division.municipality
                else None,
                name=LanguageString(
                    fi=db_division.safe_translation_getter("name", language_code="fi"),
                    sv=db_division.safe_translation_getter("name", language_code="sv"),
                    en=db_division.safe_translation_getter("name", language_code="en"),
                ),
            )
            for db_division in administrative_divisions_qs
        ]

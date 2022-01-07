from .base import Importer
from .utils.administrative_division import (
    AdministrativeDivision,
    AdministrativeDivisionFetcher,
)


class AdministrativeDivisionImporter(Importer[AdministrativeDivision]):
    ALL_DIVISIONS_INDEX = "administrative_division"

    # A certain set of Helsinki's divisions are stored into a separate index. This set
    # is mostly meant to be used to provide division choices for a UI.
    #
    # It is not completely clear whether this kind of set should even be provided by US
    # in the first place, or is storing these in an Elastic Search index the best way to
    # tackle the need, so we might want to change this implementation in the future.
    #
    # Currently includes all neighborhoods and sub districts with duplicates removed.
    HELSINKI_COMMON_DIVISIONS_INDEX = "helsinki_common_administrative_division"

    index_base_names = (
        ALL_DIVISIONS_INDEX,
        HELSINKI_COMMON_DIVISIONS_INDEX,
    )

    def run(self):
        all_administrative_divisions = AdministrativeDivisionFetcher().get_all()
        self.add_data_bulk(all_administrative_divisions, self.ALL_DIVISIONS_INDEX)

        helsinki_common_administrative_divisions = []
        encountered_helsinki_areas = set()

        for division in sorted(
            filter(
                lambda d: d.type in ("neighborhood", "sub_district")
                and d.municipality == "Helsinki",
                all_administrative_divisions,
            ),
            # make sure neighborhoods are processed before sub districts so that
            # duplicates will always be indexed as neighborhoods
            key=lambda d: d.type,
        ):
            cleaned_name = division.name.fi.lower().strip()
            if cleaned_name not in encountered_helsinki_areas:
                helsinki_common_administrative_divisions.append(division)
            encountered_helsinki_areas.add(cleaned_name)

        self.add_data_bulk(
            helsinki_common_administrative_divisions,
            self.HELSINKI_COMMON_DIVISIONS_INDEX,
        )

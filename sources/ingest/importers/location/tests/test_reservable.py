import pytest

from ingest.importers.location.importers import LocationImporter
from ingest.importers.location.utils import (
    find_reservable_connection,
    is_venue_reservable,
)
from ingest.importers.tests.mocks import unit_indoor_arena, unit_swimhall
from ingest.importers.utils.language import LanguageStringConverter


@pytest.mark.parametrize(
    "tpr_unit,is_reservable", [(unit_swimhall, False), (unit_indoor_arena, True)]
)
def test_is_venue_reservable(tpr_unit, is_reservable):
    assert is_venue_reservable(tpr_unit["connections"]) is is_reservable


@pytest.mark.parametrize(
    "tpr_unit,is_reservable", [(unit_swimhall, False), (unit_indoor_arena, True)]
)
def test_find_reservable_connection(tpr_unit, is_reservable):
    if is_reservable:
        assert find_reservable_connection(tpr_unit["connections"]) is not None
    else:
        assert find_reservable_connection(tpr_unit["connections"]) is None


@pytest.mark.parametrize(
    "tpr_unit,is_reservable", [(unit_swimhall, False), (unit_indoor_arena, True)]
)
@pytest.mark.django_db
def test_location_importer_adds_reservable_to_venue(
    tpr_unit,
    is_reservable,
):
    l = LanguageStringConverter(tpr_unit, False)
    e = lambda k: tpr_unit.get(k, None)
    location_importer = LocationImporter(enable_data_fetching=False)
    venue = location_importer._create_venue(
        l=l, e=e, _id=tpr_unit["id"], opening_hours=None, ontology_words=[]
    )
    assert venue.reservation.reservable == is_reservable

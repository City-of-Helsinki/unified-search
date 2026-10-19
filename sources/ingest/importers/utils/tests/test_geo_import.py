import json
from unittest.mock import Mock

import pytest
from django.contrib.gis.gdal import DataSource
from django.core.management import call_command, get_commands
from munigeo.importer.base import get_importers


@pytest.fixture
def helsinki_importer():
    get_importers()
    from ingest.geo_importers import HelsinkiImporter

    return HelsinkiImporter({})


def test_hsy_datasource_has_no_cql_filter_despite_division(helsinki_importer, mocker):
    import_division_type = mocker.patch(
        "munigeo.importer.helsinki.HelsinkiImporter._import_one_division_type"
    )
    division = {
        "wfs_layer": helsinki_importer.hsy_layer,
        "wfs_url": "https://kartta.hsy.fi/geoserver/wfs?CQL_FILTER=kunta%20in%20"
        "(%27091%27,%27092%27,%27049%27,%27235%27)",
        "fields": {"origin_id": "kokotun"},
    }
    municipality = Mock()

    helsinki_importer._import_one_division_type(municipality, division)

    import_division_type.assert_called_once_with(
        municipality,
        {**division, "wfs_url": "https://kartta.hsy.fi/geoserver/wfs"},
    )
    assert "CQL_FILTER" in division["wfs_url"]


def test_hsy_municipality_filter(helsinki_importer, mocker):
    import_division = mocker.patch(
        "munigeo.importer.helsinki.HelsinkiImporter._import_division"
    )
    municipality_codes = ["091", "092", "049", "235", "186", None]
    datasource = DataSource(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {"kunta": code},
                        "geometry": {"type": "Point", "coordinates": [24.9, 60.2]},
                    }
                    for code in municipality_codes
                ],
            }
        )
    )

    for feature in datasource[0]:
        helsinki_importer._import_division(
            None, {"wfs_layer": helsinki_importer.hsy_layer}, None, None, None, feature
        )

    assert [
        call.args[-1]["kunta"].as_string() for call in import_division.call_args_list
    ] == ["091", "092", "049", "235"]


def test_other_divisions_are_unchanged(helsinki_importer, mocker):
    import_division_type = mocker.patch(
        "munigeo.importer.helsinki.HelsinkiImporter._import_one_division_type"
    )
    import_division = mocker.patch(
        "munigeo.importer.helsinki.HelsinkiImporter._import_division"
    )
    division = {
        "wfs_layer": "avoindata:Piirijako_peruspiiri",
        "wfs_url": "https://kartta.hel.fi/ws/geoserver/avoindata/wfs?sortBy=tunnus",
    }
    feature = Mock()

    helsinki_importer._import_one_division_type(None, division)
    helsinki_importer._import_division(None, division, None, None, None, feature)

    import_division_type.assert_called_once_with(None, division)
    import_division.assert_called_once_with(None, division, None, None, None, feature)


def test_geo_import_uses_local_helsinki_importer(helsinki_importer, mocker):
    import_divisions = mocker.patch.object(type(helsinki_importer), "import_divisions")

    assert get_commands()["geo_import"] == "ingest"
    call_command("geo_import", "helsinki", "--divisions")

    import_divisions.assert_called_once_with()


def test_geo_import_still_imports_finland(helsinki_importer, mocker):
    import_municipalities = mocker.patch(
        "munigeo.importer.finland.FinlandImporter.import_municipalities"
    )

    call_command("geo_import", "finland", "--municipalities")

    import_municipalities.assert_called_once_with()

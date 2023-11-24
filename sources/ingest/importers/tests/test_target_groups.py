import pytest

from ingest.importers.location.enums import TargetGroup
from ingest.importers.location.utils import get_unit_id_to_target_groups_mapping


def test_get_unit_id_to_target_groups_mapping(
    mocked_service_registry_description_viewpoint_response,
):
    assert get_unit_id_to_target_groups_mapping() == {
        "1": {
            TargetGroup.CHILDREN_AND_FAMILIES,
            TargetGroup.IMMIGRANTS,
            TargetGroup.INDIVIDUALS,
            TargetGroup.YOUTH,
        },
        "2": {
            TargetGroup.ASSOCIATIONS,
            TargetGroup.CHILDREN_AND_FAMILIES,
            TargetGroup.DISABLED,
            TargetGroup.ELDERLY_PEOPLE,
            TargetGroup.IMMIGRANTS,
            TargetGroup.INDIVIDUALS,
            TargetGroup.YOUTH,
        },
        "3": {
            TargetGroup.CHILDREN_AND_FAMILIES,
            TargetGroup.IMMIGRANTS,
            TargetGroup.INDIVIDUALS,
            TargetGroup.YOUTH,
        },
        "4": {
            TargetGroup.CHILDREN_AND_FAMILIES,
            TargetGroup.INDIVIDUALS,
            TargetGroup.YOUTH,
        },
        "5": {
            TargetGroup.ASSOCIATIONS,
            TargetGroup.CHILDREN_AND_FAMILIES,
            TargetGroup.DISABLED,
            TargetGroup.ELDERLY_PEOPLE,
            TargetGroup.IMMIGRANTS,
            TargetGroup.INDIVIDUALS,
            TargetGroup.YOUTH,
        },
        "13": {TargetGroup.IMMIGRANTS},
        "36": {TargetGroup.IMMIGRANTS},
        "1234": set(),
    }

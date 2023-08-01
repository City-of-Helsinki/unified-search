import pytest

from ..location import get_unit_id_to_target_groups_mapping, TargetGroup

MOCKED_SERVICE_REGISTRY_DESCRIPTION_VIEWPOINT_RESPONSE = [
    {
        "id": 11,
        "target_groups": ["CHILDREN_AND_FAMILIES", "INDIVIDUALS", "YOUTH"],
        "unit_ids": [1, 2, 3, 4, 5],
    },
    {"id": 12, "target_groups": ["IMMIGRANTS"], "unit_ids": [1, 3, 13, 36]},
    {"id": 634, "target_groups": [], "unit_ids": [1234]},
    {
        "id": 634,
        "target_groups": [
            "ASSOCIATIONS",
            "CHILDREN_AND_FAMILIES",
            "DISABLED",
            "ELDERLY_PEOPLE",
            "IMMIGRANTS",
            "INDIVIDUALS",
            "YOUTH",
        ],
        "unit_ids": [2, 5],
    },
]


@pytest.fixture
def mocked_service_registry_description_viewpoint_response(mocker):
    return mocker.patch(
        "ingest.importers.location.request_json",
        return_value=MOCKED_SERVICE_REGISTRY_DESCRIPTION_VIEWPOINT_RESPONSE,
    )


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

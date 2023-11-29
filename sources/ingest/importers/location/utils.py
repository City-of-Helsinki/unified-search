import base64
import functools
from collections import defaultdict
from typing import Dict, List, Optional, Set

from ingest.importers.location.dataclasses import (
    AccessibilitySentence,
    AccessibilityShortcoming,
    AccessibilityViewpoint,
    OntologyObject,
    Resource,
    ResourceType,
    ResourceUserPermissions,
)
from ingest.importers.location.enums import (
    AccessibilityProfile,
    AccessibilityViewpointValue,
    ResourceMainType,
    TargetGroup,
)
from ingest.importers.utils import LanguageString, LanguageStringConverter, request_json


def get_tpr_units():
    # Use newfeatures=yes parameter to get displayed_service_owner_type and
    # displayed_service_owner_(fi|sv|en) fields included, see documentation at
    # https://www.hel.fi/palvelukarttaws/restpages/ver4.html
    url = "https://www.hel.fi/palvelukarttaws/rest/v4/unit/?newfeatures=yes"
    data = request_json(url)
    return data


def prefix_and_mask(prefix, body):
    message = f"{prefix}-{body}"
    message_bytes = message.encode("utf-8")
    base64_bytes = base64.b64encode(message_bytes)

    return base64_bytes.decode("utf-8")


def get_ontologywords_as_ontologies(ontologywords, use_fallback_languages: bool):
    ontologies = []

    for ontologyword in ontologywords:
        l = LanguageStringConverter(ontologyword, use_fallback_languages)

        ontologies.append(
            OntologyObject(
                id=str(ontologyword.get("id")),
                label=l.get_language_string("ontologyword"),
            )
        )

        if (
            "extra_searchwords_fi" in ontologyword
            or "extra_searchwords_sv" in ontologyword
            or "extra_searchwords_en" in ontologyword
        ):
            ontologies.append(
                OntologyObject(
                    # A unique id is not available in the source data. To make the id
                    # more opaque we are encoding it.
                    id=prefix_and_mask("es-", ontologyword.get("id")),
                    label=l.get_language_string("extra_searchwords"),
                )
            )

    return ontologies


def get_ontologytree_as_ontologies(ontologytree, use_fallback_languages: bool):
    ontologies = []

    for ontologybranch in ontologytree:
        l = LanguageStringConverter(ontologybranch, use_fallback_languages)

        ontologies.append(
            OntologyObject(
                id=str(ontologybranch.get("id")), label=l.get_language_string("name")
            )
        )

        if (
            "extra_searchwords_fi" in ontologybranch
            or "extra_searchwords_sv" in ontologybranch
            or "extra_searchwords_en" in ontologybranch
        ):
            ontologies.append(
                OntologyObject(
                    # A unique id is not available in the source data. To make the id
                    # more opaque we are encoding it.
                    id=prefix_and_mask("es-", ontologybranch.get("id")),
                    label=l.get_language_string("extra_searchwords"),
                )
            )

    return ontologies


def get_suggestions_from_ontologies(ontologies: List[OntologyObject]):
    ontologies_grouped_by_language = functools.reduce(
        lambda acc, ontology: {
            "fi": acc.get("fi") + [ontology.label.fi],
            "sv": acc.get("sv") + [ontology.label.sv],
            "en": acc.get("en") + [ontology.label.en],
        },
        ontologies,
        {"fi": [], "sv": [], "en": []},
    )

    # Suggestions are stored in shorthand syntax. If you want to add more
    # specific context or weight, you have to store suggestions on a per
    # suggestion basis (example):
    # [
    #     {
    #         "input": "beach",
    #         "weight": 2,
    #         "contexts": {
    #             "language": "en",
    #             "unit": "liikunta"
    #         }
    #     },
    #     {
    #         "input": "social services",
    #         "weight": 2,
    #         "contexts": {
    #             "language": "en",
    #             "unit": "social work"
    #         }
    #     },
    # ]
    suggest = []
    for [language, suggestions_in_language] in ontologies_grouped_by_language.items():
        suggestions_without_empty = list(
            filter(lambda suggestion: type(suggestion) is str, suggestions_in_language)
        )

        suggest.append(
            {"input": suggestions_without_empty, "contexts": {"language": language}}
        )

    return suggest


def define_language_properties():
    languages = [("fi", "finnish"), ("sv", "swedish"), ("en", "english")]
    language_properties = {}

    for [language, analyzer] in languages:
        language_properties[language] = {
            "type": "text",
            "analyzer": analyzer,
            "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
        }

    return language_properties


def get_respa_resources() -> List[dict]:
    """
    Get all resources from Respa API
    """
    accumulated_results = []
    url = "https://api.hel.fi/respa/v1/resource/?format=json&page_size=500"
    while url:
        respa_resources = request_json(url, timeout_seconds=120)
        accumulated_results += respa_resources["results"]
        url = respa_resources["next"]
    return accumulated_results


def get_unit_ids_and_accessibility_shortcoming_counts() -> List[dict]:
    """
    Get all unit IDs and their accessibility shortcoming counts from new service map API

    :return: A list of dictionaries each containing unit ID ("id") as integer and its
             accessibility shortcoming counts ("accessibility_shortcoming_count") in a
             dictionary.
    """
    accumulated_results = []
    url = "https://api.hel.fi/servicemap/v2/unit/?format=json&only=accessibility_shortcoming_count&page_size=1000"
    while url:
        units = request_json(url)
        accumulated_results += units["results"]
        url = units["next"]
    return accumulated_results


def create_accessibility_shortcomings(
    accessibility_shortcoming_counts: Dict[str, int]
) -> List[AccessibilityShortcoming]:
    """
    Create a list of accessibility shortcomings from a dictionary of accessibility
    shortcoming counts

    :param accessibility_shortcoming_counts: A dictionary of accessibility shortcoming
                                             counts of a unit.
    :return: A list of accessibility shortcomings.
    """
    return sorted(
        (
            AccessibilityShortcoming(
                profile=AccessibilityProfile(accessibility_profile).value,
                count=shortcoming_count,
            )
            for accessibility_profile, shortcoming_count in accessibility_shortcoming_counts.items()
        )
    )


def get_unit_id_to_accessibility_shortcomings_mapping() -> (
    Dict[str, List[AccessibilityShortcoming]]
):
    """
    Get mapping of unit IDs to their accessibility shortcomings from new service map API
    """
    return {
        str(unit["id"]): create_accessibility_shortcomings(
            unit.get("accessibility_shortcoming_count", {})
        )
        for unit in get_unit_ids_and_accessibility_shortcoming_counts()
    }


def get_accessibility_viewpoint_id_to_name_mapping(
    use_fallback_languages: bool,
) -> Dict[str, LanguageString]:
    """
    Get accessibility viewpoint ID to name mapping from service map API.

    Documentation about the service map API's accessibility viewpoint endpoint:
    - https://www.hel.fi/palvelukarttaws/restpages/ver4.html#_accessibility_viewpoint

    :return: Mapping from accessibility viewpoint ID to accessibility viewpoint name.

    Example of a possible return value:
    {
        "11": LanguageString(fi="Olen pyörätuolin käyttäjä",
                             sv="Jag är en rullstolsanvändare",
                             en="I am a wheelchair user")
        },
        "61": LanguageString(fi="Käytän kuulolaitetta",
                             sv="Jag använder en hörapparat",
                             en="I use a hearing aid")
        }
    }
    """
    url = "https://www.hel.fi/palvelukarttaws/rest/v4/accessibility_viewpoint/"
    accessibility_viewpoints = request_json(url)
    return {
        viewpoint["id"]: LanguageStringConverter(
            viewpoint, use_fallback_languages
        ).get_language_string("name")
        for viewpoint in accessibility_viewpoints
    }


def create_accessibility_sentence(
    accessibility_sentence: dict, use_fallback_languages: bool
) -> AccessibilitySentence:
    """
    Create AccessibilitySentence object from a dictionary containing a single
    accessibility sentence from
    https://www.hel.fi/palvelukarttaws/rest/v4/accessibility_sentence/

    Documentation about the endpoint:
    - https://www.hel.fi/palvelukarttaws/restpages/ver4_en.html

    Example of input:
    e.g.
    {
        "unit_id": 6365,
        "sentence_group_name": "Sisätilat",
        "sentence_group_fi": "Sisätilat",
        "sentence_group_sv": "I lokalen",
        "sentence_group_en": "In the facility",
        "sentence_fi": "Asiointipisteen ovet erottuvat selkeästi.",
        "sentence_sv": "Dörrarna vid servicepunkten är lätta att urskilja.",
        "sentence_en": "The doors in the customer service point stand out clearly."
    }

    :return: AccessibilitySentence object containing the given accessibility sentence
    """
    return AccessibilitySentence(
        sentenceGroupName=accessibility_sentence["sentence_group_name"],
        sentenceGroup=LanguageStringConverter(
            accessibility_sentence, use_fallback_languages
        ).get_language_string("sentence_group"),
        sentence=LanguageStringConverter(
            accessibility_sentence, use_fallback_languages
        ).get_language_string("sentence"),
    )


def get_unit_id_to_accessibility_sentences_mapping(
    use_fallback_languages: bool,
) -> Dict[str, List[AccessibilitySentence]]:
    """
    Get a mapping of unit IDs to their accessibility sentences from service map API.
    """
    url = "https://www.hel.fi/palvelukarttaws/rest/v4/accessibility_sentence/"
    accessibility_sentences = request_json(url, timeout_seconds=120)
    result = defaultdict(list)
    for sentence in accessibility_sentences:
        result[str(sentence["unit_id"])].append(
            create_accessibility_sentence(sentence, use_fallback_languages)
        )
    return result


def get_unit_id_to_accessibility_viewpoint_shortages_mapping(
    use_fallback_languages: bool,
) -> Dict[str, Dict[str, List[LanguageString]]]:
    """
    Get a mapping of unit IDs to their accessibility viewpoints' IDs to their
    list of accessibility shortages from service map API.
    """
    url = "https://www.hel.fi/palvelukarttaws/rest/v4/accessibility_shortage/"
    accessibility_shortages = request_json(url, timeout_seconds=120)
    result = defaultdict(lambda: defaultdict(list))
    for shortage in accessibility_shortages:
        unit_id = str(shortage["unit_id"])
        viewpoint_id = str(shortage["viewpoint_id"])
        l = LanguageStringConverter(shortage, use_fallback_languages)
        result[unit_id][viewpoint_id].append(l.get_language_string("shortage"))
    return result


def get_accessibility_viewpoint_id_to_value_mapping(
    accessibility_viewpoints: Optional[str],
) -> Dict[str, str]:
    """
    Converts service map API's unit's accessibility_viewpoints string to a mapping from
    the accessibility viewpoint ID to the unit's accessibility viewpoint value.

    :param accessibility_viewpoints: A string of comma separated pairs of accessibility
                                     viewpoint IDs and their values separated with
                                     colons, e.g. "00:unknown,11:red".
    :return: A dictionary of accessibility viewpoint IDs and their values, e.g.
             {"00": "unknown", "11": "red"}.

    Documentation about accessibility viewpoint endpoint:
    - https://www.hel.fi/palvelukarttaws/restpages/ver4.html#_accessibility_viewpoint

    Accessibility viewpoint values:
    - https://www.hel.fi/palvelukarttaws/rest/v4/accessibility_viewpoint/

    The IDs are the same as in the accessibility viewpoint endpoint, e.g.
    https://www.hel.fi/palvelukarttaws/rest/v4/accessibility_viewpoint/
    ...
    {
        "id": "11",
        "name_fi": "Olen pyörätuolin käyttäjä",
        "name_sv": "Jag är en rullstolsanvändare",
        "name_en": "I am a wheelchair user",
        "values": [
            "unknown",
            "green",
            "red"
        ]
    },
    ...

    All accessibility viewpoints' values are limited to "unknown", "green" and "red".
    """
    return (
        dict(
            accessibility_viewpoint.split(":")
            for accessibility_viewpoint in accessibility_viewpoints.split(",")
        )
        if accessibility_viewpoints
        else {}
    )


def get_enriched_accessibility_viewpoints(
    accessibility_viewpoints: Optional[str],
    accessibility_viewpoint_id_to_name_mapping: Dict[str, LanguageString],
    omit_unknowns: bool,
) -> List[AccessibilityViewpoint]:
    """
    Converts service map API's unit's accessibility_viewpoints string to a list of
    AccessibilityViewpoint objects.

    :param accessibility_viewpoints: A string of comma separated pairs of accessibility
                                     viewpoint IDs and their values separated with
                                     colons, e.g. "00:unknown,11:red".
    :param accessibility_viewpoint_id_to_name_mapping: A dictionary of accessibility
                                                       viewpoint IDs mapped to their
                                                       names.
    :param omit_unknowns: Whether to omit accessibility viewpoints with value "unknown".
    :return: A list of AccessibilityViewpoint objects without viewpoints with value
             "unknown" if omit_unknowns is True, otherwise with all viewpoints.

    Example return value:
        get_enriched_accessibility_viewpoints(
            '11:red,21:green,61:unknown',
            get_accessibility_viewpoint_id_to_name_mapping(use_fallback_languages=True),
            omit_unknowns=True
        ) == [
            AccessibilityViewpoint(
                id='11',
                name=LanguageString(fi='Olen pyörätuolin käyttäjä',
                                    sv='Jag är en rullstolsanvändare',
                                    en='I am a wheelchair user'),
                value='red'
            ),
            AccessibilityViewpoint(
                id='21',
                name=LanguageString(fi='Olen liikkumisesteinen, mutta kävelen',
                                    sv='Jag är rörelsehindrad, men jag går',
                                    en='I have reduced mobility, but I walk'),
                value='green'
            )
        ]
    """
    id_to_value_mapping = get_accessibility_viewpoint_id_to_value_mapping(
        accessibility_viewpoints
    )
    return [
        AccessibilityViewpoint(
            id=viewpoint_id,
            name=accessibility_viewpoint_id_to_name_mapping[viewpoint_id],
            value=AccessibilityViewpointValue(viewpoint_value).value,
        )
        for viewpoint_id, viewpoint_value in id_to_value_mapping.items()
        if (
            not omit_unknowns
            or viewpoint_value != AccessibilityViewpointValue.UNKNOWN.value
        )
    ]


def create_resource_type(
    respa_resource_type: dict, use_fallback_languages: bool
) -> ResourceType:
    """
    Create a ResourceType object from a Respa resource's type.
    """
    l = LanguageStringConverter(respa_resource_type, use_fallback_languages)
    return ResourceType(
        id=respa_resource_type["id"],
        mainType=ResourceMainType(respa_resource_type["main_type"]).value,
        name=l.get_language_string("name"),
    )


def create_resource_user_permissions(
    respa_user_permissions: dict,
) -> ResourceUserPermissions:
    """
    Create a ResourceUserPermissions object from a Respa user permissions
    """
    return ResourceUserPermissions(
        canMakeReservations=respa_user_permissions["can_make_reservations"],
    )


def create_exportable_resource(
    respa_resource: dict, use_fallback_languages: bool
) -> Resource:
    """
    Create a Resource object from a Respa resource.
    """
    l = LanguageStringConverter(respa_resource, use_fallback_languages)
    return Resource(
        id=respa_resource["id"],
        name=l.get_language_string("name"),
        description=l.get_language_string("description"),
        type=create_resource_type(respa_resource["type"], use_fallback_languages),
        userPermissions=create_resource_user_permissions(
            respa_resource["user_permissions"]
        ),
        reservable=respa_resource["reservable"],
        reservationInfo=l.get_language_string("reservation_info"),
        genericTerms=l.get_language_string("generic_terms"),
        paymentTerms=l.get_language_string("payment_terms"),
        specificTerms=l.get_language_string("specific_terms"),
        responsibleContactInfo=l.get_language_string("responsible_contact_info"),
        externalReservationUrl=respa_resource["external_reservation_url"],
    )


def get_unit_id_to_resources_mapping(
    use_fallback_languages: bool,
) -> Dict[str, List[Resource]]:
    """
    Get a mapping of unit IDs to their resources from Respa API.
    """
    result = defaultdict(list)
    for respa_resource in get_respa_resources():
        unit_id = str(respa_resource.get("unit", ""))
        # Remove 'tprek:' prefix from unit IDs (e.g. "tprek:50174" or "axarwdco746q")
        removable_prefix = "tprek:"
        if unit_id.startswith(removable_prefix):
            unit_id = unit_id[len(removable_prefix) :]
        result[unit_id].append(
            create_exportable_resource(respa_resource, use_fallback_languages)
        )
    return result


def get_unit_id_to_target_groups_mapping() -> Dict[str, Set[TargetGroup]]:
    """
    Get a mapping of unit IDs to their target groups from palvelukuvausrekisteri, see
    https://www.hel.fi/palvelukarttaws/restpages/palvelurekisteri.html for documentation
    """
    url = "https://www.hel.fi/palvelukarttaws/rest/vpalvelurekisteri/description/?alldata=yes"
    services = request_json(url, timeout_seconds=120)
    result = defaultdict(set)
    for service in services:
        unit_ids = service.get("unit_ids", [])
        target_groups = service.get("target_groups", [])
        for unit_id in unit_ids:
            result[str(unit_id)] |= set(map(TargetGroup, target_groups))
    return result

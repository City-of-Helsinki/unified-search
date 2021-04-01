from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List
from django.utils import timezone

import json
import requests
import sys

from elasticsearch import Elasticsearch


@dataclass
class NodeMeta:
    id: str
    createdAt: str
    updatedAt: str=None

@dataclass
class LinkedData:
    service: str = None
    origin_url: str = None
    raw_data: dict = None

@dataclass
class LanguageString:
    fi: str
    sv: str
    en: str

@dataclass
class Address:
    postal_code: str
    street_address: LanguageString
    city: LanguageString

@dataclass
class GeoJSONFeature:
    latitude: float
    longitude: float
    northing_etrs_gk25: int
    easting_etrs_gk25: int
    northing_etrs_tm35fin: int
    easting_etrs_tm35fin: int
    manual_coordinates: bool

@dataclass
class Location:
    url: LanguageString
    address: Address = None
    geoLocation: GeoJSONFeature = None

@dataclass
class OpeningHours:
    url: str
    is_open_now_url: str
    hourLines: List[LanguageString] = field(default_factory=list)

@dataclass
class Venue:
    meta: NodeMeta = None
    name: LanguageString = None
    location: Location = None
    description: LanguageString = None
    
    # TODO
    descriptionResources: str = None
    # annotations imported for this
    partOf: Venue = None
    openingHours: OpeningHours = None
    manager: str = None
    reservationPolicy: str = None
    accessibilityProfile: str = None
    arrivalInstructions: str = None
    additionalInfo: str = None
    facilities: str = None

@dataclass
class Root:
    venue: Venue
    links: List[LinkedData] = field(default_factory=list)


def request_json(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
    except Exception as e:
        print(f"Error while requesting {url}: {e}")
    return r.json()


def get_ontologyword_ids(id_list):
    info = []

    for _id in id_list:
        url = f"https://www.hel.fi/palvelukarttaws/rest/v4/ontologyword/{_id}/"
        data = request_json(url)

        # Drop verbose extra parameters
        data.pop("unit_ids", None)
        data.pop("can_add_schoolyear", None)
        data.pop("can_add_clarification", None)
        
        info.append(data)

    return info


def get_tpr_units():
    url = "https://www.hel.fi/palvelukarttaws/rest/v4/unit/"
    data = request_json(url)
    return data


def get_linkedevents_place(id):
    url = f"https://api.hel.fi/linkedevents/v1/place/tprek:{id}/"
    data = request_json(url)

    # Extra information to raw data
    data["origin"] = "linkedevents"

    return url, data


def create_language_string(d, key_prefix):
    return LanguageString(
        fi=d.get(f"{key_prefix}_fi", None),
        sv=d.get(f"{key_prefix}_sv", None),
        en=d.get(f"{key_prefix}_en", None)
        )


def get_opening_hours(d):
    results = []
    if "connections" in d and d["connections"]:
        for section in d["connections"]:
            if section["section_type"] == "OPENING_HOURS":
                results.append(section)
    return results


def fetch():

    try:
        es = Elasticsearch([{"host": "es01", "port": 9200}])
    except ConnectionError as e:
        return "ERROR at {}".format(__name__)

    print("Requesting data at {}".format(__name__))

    tpr_units = get_tpr_units()

    count  = 0
    for tpr_unit in tpr_units:

        e = lambda k: tpr_unit.get(k, None)

        # ID's must be strings to avoid collisions
        tpr_unit["id"] = _id = str(tpr_unit["id"])

        meta = NodeMeta(id=_id, createdAt=timezone.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        location = Location(
            url=create_language_string(tpr_unit, "www"),
            address = Address(
                postal_code=e("address_zip"),
                street_address=create_language_string(tpr_unit, "street_address"),
                city=create_language_string(tpr_unit, "address_city")
                ),
            geoLocation=GeoJSONFeature(
                latitude=e("latitude"),
                longitude=e("longitude"),
                northing_etrs_gk25=e("northing_etrs_gk25"),
                easting_etrs_gk25 = e("easting_etrs_gk25"),
                northing_etrs_tm35fin = e("northing_etrs_tm35fin"),
                easting_etrs_tm35fin = e("easting_etrs_tm35fin"),
                manual_coordinates = e("manual_coordinates")
                ),
            )

        opening_hours = OpeningHours(
            url=f"http://hauki-test.oc.hel.ninja/v1/resource/tprek:{_id}/opening_hours/",
            is_open_now_url=f"http://hauki-test.oc.hel.ninja/v1/resource/tprek:{_id}/is_open_now/")

        # TODO
        o = get_opening_hours(tpr_unit)
        if o:
            print(o)

        venue = Venue(
            name=create_language_string(tpr_unit, "name"),
            description=create_language_string(tpr_unit, "desc"),
            location=location, 
            meta=meta, 
            openingHours=opening_hours)

        #print(tpr_unit)

        place_url, place = get_linkedevents_place(_id)

        place_link = LinkedData(
            service="linkedevents",
            origin_url=place_url,
            raw_data=place)

        root = Root(venue=venue)
        root.links.append(place_link)

        # Extra information to raw data
        tpr_unit["origin"] = "tpr"

        if "ontologyword_ids" in tpr_unit and tpr_unit['ontologyword_ids']:
            # Enrich data from another API
            tpr_unit["ontologyword_ids_enriched"] = get_ontologyword_ids(tpr_unit["ontologyword_ids"])

        link = LinkedData(
            service="tpr",
            origin_url=f"https://www.hel.fi/palvelukarttaws/rest/v4/unit/{_id}/", 
            raw_data=tpr_unit)
        root.links.append(link)

        r = es.index(index="location", doc_type="_doc", body=str(json.dumps(asdict(root))))
        print(count, sep="")
        count = count + 1

    return "Fetch completed by {}".format(__name__)


def delete():
    """ Delete the whole index. """
    try:
        es = Elasticsearch([{"host": "es01", "port": 9200}])
        r = es.indices.delete(index="location")
        print(r)
    except Exception as e:
        return "ERROR at {}".format(__name__)


def set_alias(alias):
    """ Configure alias for index name. """
    try:
        es = Elasticsearch([{"host": "es01", "port": 9200}])
        es.indices.put_alias(index='location', name=alias)
    except ConnectionError as e:
        return "ERROR at {}".format(__name__)

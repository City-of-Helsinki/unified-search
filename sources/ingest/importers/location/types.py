from typing import List, Optional, TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from ingest.importers.location.dataclasses import Connection
    from ingest.importers.location.enums import ProviderType, ServiceOwnerType
    from ingest.importers.utils.shared import LanguageString


class TPRUnitSources(TypedDict):
    id: str
    source: str


class TPRUnitResponse(TypedDict):
    """
    A response type for endpoint in
    https://www.hel.fi/palvelukarttaws/rest/v4/unit/42284?official=yes&format=json&newfeatures=yes.
    """

    id: str
    is_public: Optional[bool]
    arealcity_id: Optional[int]
    org_id: Optional[str]
    dept_id: Optional[str]
    provider_type: "ProviderType"
    displayed_service_owner_type: "ServiceOwnerType"
    displayed_service_owner: "LanguageString"
    data_source_url: str
    name: "LanguageString"
    ontologyword_ids: List[int]
    ontologytree_ids: List[int]
    sources: Optional[List["TPRUnitSources"]]
    provided_languages: Optional[List[str]]
    regions: Optional[List[str]]
    short_desc: Optional["LanguageString"]
    desc: Optional["LanguageString"]
    latitude: Optional[float]
    longitude: Optional[float]
    northing_etrs_gk25: Optional[int]
    easting_etrs_gk25: Optional[int]
    northing_etrs_tm35fin: Optional[int]
    easting_etrs_tm35fin: Optional[int]
    manual_coordinates: Optional[bool]
    street_address: Optional["LanguageString"]
    address_zip: Optional[str]
    address_city: Optional[str]
    vtj_prt: Optional[str]
    vtj_prt_verified: Optional[str]
    phone: Optional[str]
    call_charge_info: Optional["LanguageString"]
    picture_url: Optional[str]
    picture_caption: Optional["LanguageString"]
    accessibility_phone: Optional[str]
    accessibility_email: Optional[str]
    accessibility_www: Optional[str]
    accessibility_viewpoints: Optional[str]
    created_time: str
    modified_time: str
    connections: List["Connection"]

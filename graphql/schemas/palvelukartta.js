const { GraphQLScalarType } = require('graphql');

exports.palvelukarttaSchema = `

type PalvelukarttaUnit {
    """ Raw palvelukartta Unit fields """

    origin: String,

    id: Int,
    org_id: String,
    dept_id: String,
    provider_type: String,
    organizer_type: String,
    organizer_name: String,
    data_source_url: String,
    name_fi: String,
    name_sv: String,
    name_en: String,
    ontologyword_ids: [ Int ],
    ontologytree_ids: [ Int ],
    desc_fi: String,
    desc_sv: String,
    desc_en: String,
    latitude: Float,
    longitude: Float,
    northing_etrs_gk25: Int,
    easting_etrs_gk25: Int,
    northing_etrs_tm35fin: Int,
    easting_etrs_tm35fin: Int,
    manual_coordinates: Boolean
    street_address_fi: String,
    street_address_sv: String,
    street_address_en: String,
    address_zip: String,
    address_city_fi: String,
    address_city_sv: String,
    address_city_en: String,
    phone: String,
    call_charge_info_fi: String,
    call_charge_info_sv: String,
    call_charge_info_en: String,
    www_fi: String,
    www_sv: String,
    www_en: String,
    picture_url: String,
    picture_caption_fi: String,
    picture_caption_sv: String,
    picture_caption_en: String,
    extra_searchwords_en: String,
    accessibility_viewpoints: String,
    created_time: String,
    modified_time: String,

    ontologyword_ids_enriched: [Ontologyword]
}

type Ontologyword {
    id: Int,
    ontologyword_fi: String,
    ontologyword_sv: String,
    ontologyword_en: String,
    can_add_schoolyear: Boolean,
    can_add_clarification: Boolean,
    extra_searchwords_fi: String,
    unit_ids: [Int]
}

`;

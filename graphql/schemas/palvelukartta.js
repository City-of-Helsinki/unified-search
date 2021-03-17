
const { GraphQLScalarType } = require('graphql');


exports.palvelukarttaSchema = `

type PalvelukarttaUnit {
    """ Raw palvelukartta Unit fields """

    id: Int,
    org_id: String,
    dept_id: String,
    provider_type: String,
    data_source_url: String,
    name_fi: String,
    name_en: String,
    ontologyword_ids: [Int],
    ontologytree_ids: [Int],
    desc_fi: String,
    desc_en: String,
    latitude: Float,
    longitude: Float,
    northing_etrs_gk25: Int,
    easting_etrs_gk25: Int,
    northing_etrs_tm35fin: Int,
    easting_etrs_tm35fin: Int,
    manual_coordinates: Boolean,
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
    accessibility_viewpoints: String,
    created_time: String,
    modified_time: String,
}

`;
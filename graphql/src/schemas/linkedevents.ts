import { gql } from 'graphql-tag';
export const linkedeventsSchema = gql`
  type LinkedeventsPlace {
    """
    Raw Linkedevents Place fields
    """
    origin: String

    id: String
    data_source: String
    publisher: String

    divisions: [LinkedeventsPlaceDivision]
    created_time: String
    last_modified_time: String
    custom_data: String
    email: String
    contact_type: String
    address_region: String
    postal_code: String
    post_office_box_num: String
    address_country: String
    deleted: Boolean
    has_upcoming_events: Boolean
    n_events: Int
    image: String
    parent: String
    replaced_by: String
    position: LinkedeventsPlacePosition
    address_locality: LinkedeventsPlaceLocalityString
    info_url: LinkedeventsPlaceLocalityString
    description: LinkedeventsPlaceLocalityString
    telephone: String
    street_address: LinkedeventsPlaceLocalityString
    name: LinkedeventsPlaceLocalityString
    _at_id: String
    _at_context: String
    _at_type: String
  }

  type LinkedeventsPlaceDivision {
    type: String
    ocd_id: String
    municipality: String
    name: LinkedeventsPlaceLocalityString
  }

  type LinkedeventsPlacePosition {
    type: String
    coordinates: [Float]
  }

  type LinkedeventsPlaceLocalityString {
    fi: String
    sv: String
    en: String
  }
`;

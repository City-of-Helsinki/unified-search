exports.locationSchema = `
  """
  A place that forms a unit and can be used for some specific purpose -
  respa unit or resource, service map unit, beta.kultus venue, linked
  events place, Kukkuu venue
  """
  type Venue {
    meta: NodeMeta
    name: LanguageString
    location: LocationDescription
    description: LanguageString
    descriptionResources: DescriptionResources
    partOf: Venue
    openingHours: OpeningHours
    manager: LegalEntity
    contactDetails: ContactInfo
    reservationPolicy: VenueReservationPolicy
    accessibilityProfile: AccessibilityProfile
    arrivalInstructions: String
    additionalInfo: String
    facilities: [VenueFacility!]
  }
  """
  Free-form location, not necessarily at a know venue.
  """
  type LocationDescription {
    url: LanguageString
    geoLocation: GeoJSONFeature
    streetAddress: Address
    explanation: String
	@origin(service: "linked", type: "event", attr: "location_extra_info")
    venue: Venue
  }
  """TODO: take this from service map / TPREK"""
  type AccessibilityProfile {
    meta: NodeMeta
    todo: String
  }
  """TODO: combine beta.kultus Venue stuff with respa equipment type"""
  type VenueFacility {
    meta: NodeMeta
    name: String!
    categories: [Keyword!]
  }
  type OpeningHours {
    url: String
    is_open_now_url: String
  }

`;
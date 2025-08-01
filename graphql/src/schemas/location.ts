import { gql } from 'graphql-tag';
export const locationSchema = gql`
  """
  A place that forms a unit and can be used for some specific purpose -
  respa unit or resource, service map unit, beta.kultus venue, linked
  events place, Kukkuu venue
  """
  type UnifiedSearchVenue {
    meta: NodeMeta
    name: LanguageString
    location: LocationDescription @cacheControl(inheritMaxAge: true)
    description: LanguageString
    serviceOwner: ServiceOwner
    targetGroups: [TargetGroup]
    openingHours: OpeningHours
    reservation: Reservation
    accessibility: Accessibility
    """
    Accessibility shortcoming for a specific accessibility profile.
    """
    accessibilityShortcomingFor(
      profile: AccessibilityProfile
    ): AccessibilityShortcoming
    images: [LocationImage]
    ontologyWords: [OntologyWord]
  }
  type Address {
    postalCode: String
    streetAddress: LanguageString
    city: LanguageString
  }
  """
  Free-form location, not necessarily at a know venue.
  """
  type LocationDescription {
    url: LanguageString
    geoLocation: GeoJSONFeature @cacheControl(inheritMaxAge: true)
    address: Address
    explanation: String
    administrativeDivisions: [AdministrativeDivision]
    venue: UnifiedSearchVenue
  }
  enum TargetGroup {
    ASSOCIATIONS
    CHILDREN_AND_FAMILIES
    DISABLED
    ELDERLY_PEOPLE
    ENTERPRISES
    IMMIGRANTS
    INDIVIDUALS
    YOUTH
  }
  enum ProviderType {
    ASSOCIATION
    CONTRACT_SCHOOL
    MUNICIPALITY
    OTHER_PRODUCTION_METHOD
    PAYMENT_COMMITMENT
    PRIVATE_COMPANY
    PURCHASED_SERVICE
    SELF_PRODUCED
    SUPPORTED_OPERATIONS
    UNKNOWN_PRODUCTION_METHOD
    VOUCHER_SERVICE
  }
  enum ServiceOwnerType {
    MUNICIPAL_SERVICE
    NOT_DISPLAYED
    PRIVATE_CONTRACT_SCHOOL
    PRIVATE_SERVICE
    PURCHASED_SERVICE
    SERVICE_BY_JOINT_MUNICIPAL_AUTHORITY
    SERVICE_BY_MUNICIPALLY_OWNED_COMPANY
    SERVICE_BY_MUNICIPAL_GROUP_ENTITY
    SERVICE_BY_OTHER_MUNICIPALITY
    SERVICE_BY_REGIONAL_COOPERATION_ORGANIZATION
    SERVICE_BY_WELLBEING_AREA
    STATE_CONTRACT_SCHOOL
    STATE_SERVICE
    SUPPORTED_OPERATIONS
    VOUCHER_SERVICE
  }
  type ServiceOwner {
    providerType: ProviderType
    type: ServiceOwnerType
    name: LanguageString
  }
  enum AccessibilityViewpointValue {
    unknown
    red
    green
  }
  type AccessibilityViewpoint {
    id: ID!
    name: LanguageString!
    value: AccessibilityViewpointValue!
    shortages: [LanguageString!]!
  }
  enum AccessibilityProfile {
    hearing_aid
    reduced_mobility
    rollator
    stroller
    visually_impaired
    wheelchair
  }
  type AccessibilityShortcoming {
    profile: AccessibilityProfile!
    count: Int
  }
  type AccessibilitySentence {
    sentenceGroupName: String
    sentenceGroup: LanguageString
    sentence: LanguageString
  }
  type Accessibility {
    email: String
    phone: String
    www: String
    viewpoints: [AccessibilityViewpoint!]!
    sentences: [AccessibilitySentence!]!
    shortcomings: [AccessibilityShortcoming!]!
  }
  type Reservation {
    reservable: Boolean
    externalReservationUrl: LanguageString
  }
  type OpeningHours {
    url: String
    is_open_now_url: String
    today: [OpeningHoursTimes]
    data: [OpeningHoursDay]
  }

  type LocationImage {
    url: String
    caption: LanguageString
  }

  type AdministrativeDivision {
    id: ID
    type: String
    municipality: String
    name: LanguageString
  }

  type OntologyWord {
    id: ID
    label: LanguageString
  }

  type OpeningHoursDay {
    date: String
    times: [OpeningHoursTimes]
  }

  type OpeningHoursTimes {
    startTime: String
    endTime: String
    endTimeOnNextDay: Boolean
    resourceState: String
    fullDay: Boolean
  }
`;

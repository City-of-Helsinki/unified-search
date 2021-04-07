exports.actorSchema = `
  """TODO: take from Profile"""
  type Person {
    meta: NodeMeta
    name: String
    identificationStrength: IdentificationStrength
    contactDetails: ContactInfo
    preferredLanguages: [Language!]
    preferredMedium: ContactMedium
  }
  enum IdentificationStrength {
    "If this person is just a pseudoperson for contacting"
    NONIDENTIFIABLE
    "If the identity of this person is not known at all"
    UNIDENTIFIED
    "If the person has authenticated with at least some method"
    AUTHENTICATED
    "If the person has done some identifiable action such as payment"
    INDIRECT
    "If the person has proved their legal identity"
    LEGALLY_CONNECTED
  }
  """TODO: merge beta.kultus organisation, etc"""
  type Organisation {
    meta: NodeMeta
    contactDetails: ContactInfo
  }
  union LegalEntity = Person | Organisation
  enum ContactMedium {
    SMS
    EMAIL
    SMS_AND_EMAIL
    MOBILE_NOTIFICATION
    ASIOINTI
  }
  """
  Contact details for a person, legal entity, venue or project
  """
  type ContactInfo
    @origin(service: "linked", type: "event", attr: "provider_contact_info")
  {
    contactUrl: String
    phoneNumbers: [PhoneNumber!]!
    emailAddresses: [String!]!
    postalAddresses: [Address!]!
  }
  type PhoneNumber {
    countryCode: String!
    restNumber: String!
  }
  """TODO: give real structure"""
  type Address {
    streetAddress: String!
  }
`;

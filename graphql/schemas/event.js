exports.eventSchema = `
  """
  An organised event - something that happens at a specific time, has a
  specific topic or content, and people can participate.  Examples include
  meetups, concerts, volunteering occasions (or bees), happenings.  This
  corresponds to Linked events/courses event, beta.kultus
  PalvelutarjotinEventNode, Kukkuu event.
  """
  type Event {
    meta: NodeMeta
    name: String!
	@origin(service: "linked", type: "event", attr: "name")
    description: String
	@origin(service: "linked", type: "event", attr: "description")
    shortDescription: String
	@origin(service: "linked", type: "event", attr: "short_description")
    descriptionResources: DescriptionResources
    keywords: [Keyword!]!
	@origin(service: "linked", type: "event", attr: "keywords")
    eventDataSource: String
	@origin(service: "linked", type: "event", attr: "data_source")
    occurrences: [EventOccurrence!]!
    pricing: [EventPricing!]
	@origin(service: "linked", type: "event", attr: "offers")
    organiser: LegalEntity
	@origin(service: "linked", type: "event", attr: "provider")
    publisher: LegalEntity
	@origin(service: "linked", type: "event", attr: "publisher")
    published: DateTime
	@origin(service: "linked", type: "event", attr: "date_published")
    contactPerson: LegalEntity
    eventLanguages: [Language!]!
	@origin(service: "linked", type: "event", attr: "in_language")
    subEvents: [Event!]!
	@origin(service: "linked", type: "event", attr: "sub_events")
    superEvent: Event
	@origin(service: "linked", type: "event", attr: "super_event")
    enrolmentPolicy: EnrolmentPolicy
    targetAudience: [Keyword!]
	@origin(service: "linked", type: "event", attr: "audience")
  }
  """TODO: improve (a lot) over Linked events' offer type"""
  type EventPricing {
    meta: NodeMeta
    todo: String
  }
  type EventOccurrence {
    meta: NodeMeta
    "which event this is an occurrence of"
    ofEvent: Event
    happensAt: TimeDescription
    """
    for information - for example, to guide people who are looking for
    big or small events, or to give city officials a hint on how much
    equipment is needed
    """
    estimatedAttendeeCount: Int
    location: LocationDescription
	@origin(service: "linked", type: "event", attr: "location")
    status: EventOccurrenceStatus
	@origin(service: "linked", type: "event", attr: "event_status")
    enrolments: [Enrolment!]!
    minimumAttendeeCount: Int
	@origin(service: "linked", type: "extension_course", attr: "minimum_attendee_capacity")
    maximumAttendeeCount: Int
	@origin(service: "linked", type: "extension_course", attr: "maximum_attendee_capacity")
    currentlyAvailableParticipantCount: Int
	@origin(service: "linked", type: "extension_course", attr: "remaining_attendee_capacity")
    "for events where equipment is requested from the City of Helsinki"
    cityEquipmentRequests: [EquipmentRequest!]
  }
  enum EventOccurrenceStatus {
    UNPUBLISHED
    PUBLISHED
    CANCELLED
    RESCHEDULED
    POSTPONED
  }
  """
  Rules about who can enroll to an event and how
  """
  type EnrolmentPolicy {
    meta: NodeMeta
    type: [EnrolmentPolicyType!]!
    enrolmentTime: TimeDescription
	@origin(service: "linked", type: "extension_course", attr: "enrolment_start_time")
	@origin(service: "linked", type: "extension_course", attr: "enrolment_end_time")
    allowedParticipantCategories: [Keyword!]!
    participantMinimumAge: Int!
	@origin(service: "linked", type: "event", attr: "audience_min_age")
    participantMaximumAge: Int!
	@origin(service: "linked", type: "event", attr: "audience_max_age")
    "minimum number of people who can enrol together (at the same time)"
    minimumEnrolmentCount: Int
    "maximum number of people who can enrol together (at the same time)"
    maximumEnrolmentCount: Int
  }
  enum EnrolmentPolicyType {
    NO_ENROLMENT_NEEDED
    GROUPS
    GROUPS_WITH_SUPERVISORS
    INDIVIDUALS
  }
  """
  Information about enrolled participant(s) in an event occurrence
  """
  type Enrolment {
    meta: NodeMeta
    event: EventOccurrence
    enroller: Person
    participantCount: Int!
    participants: [Person!]
    participantCategory: Keyword
    overseerCount: Int
    overseers: [Person!]
    requestedMethodOfNotification: ContactMedium
    status: EnrolmentStatus
    extraInformation: String
  }
  enum EnrolmentStatus {
    REQUESTED
    QUEUED
    CONFIRMED
    CANCELLED
    DECLINED
  }
  """
  Request for equipment - if someone needs equipment for a purpose such
  as organising a volunteering event (as is the case in park cleaning
  bees), a specification of what is being requested.
  """
  type EquipmentRequest {
    meta: NodeMeta
    requestedEquipment: String!
    estimatedAmount: Int
    requestedForEvent: Event
    deliveryLocation: LocationDescription
    returnLocation: LocationDescription
    extraInformation: String!
  }
`;
import { describe, it, expect } from 'vitest';

import { AccessibilityProfileType } from '../../datasources/es/types.js';
import type { VenueProps } from '../../types.js';
import { getUnifiedSearchVenueResolvers } from '../getUnifiedSearchVenueResolvers.js';

// A test venue taken partly from real data, but omitting
// and anonymizing some of the data
const testVenue = {
  venue: {
    meta: {
      id: '8740',
      createdAt: '2025-12-03T03:07:29.031297',
      updatedAt: null,
    },
    name: {
      fi: 'Malmitalo',
      sv: 'Malms kulturhus',
      en: 'Cultural Centre Malmitalo',
    },
    location: {
      url: {
        fi: 'http://www.malmitalo.fi/',
        sv: 'https://www.malmitalo.fi/sv/framsidan',
        en: 'https://www.malmitalo.fi/en/frontpage',
      },
      geoLocation: {
        type: 'Point',
        geometry: {
          type: 'Point',
          coordinates: [25.01497, 60.250507],
        },
      },
      address: {
        postalCode: '00700',
        streetAddress: {
          fi: 'Ala-Malmin tori 1',
          sv: 'Nedre Malms torg 1',
          en: 'Ala-Malmin tori 1',
        },
        city: {
          fi: 'Helsinki',
          sv: 'Helsingfors',
          en: 'Helsinki',
        },
      },
      administrativeDivisions: [
        {
          id: 'ocd-division/country:fi/kunta:helsinki/peruspiiri:malmi',
          type: 'district',
          municipality: 'Helsinki',
        },
        {
          id: 'ocd-division/country:fi/kunta:helsinki',
          type: 'muni',
          municipality: null,
        },
        {
          id: 'ocd-division/country:fi/kunta:helsinki/kaupunginosa:malmi',
          type: 'neighborhood',
          municipality: 'Helsinki',
        },
        {
          id: 'ocd-division/country:fi/kunta:helsinki/osa-alue:ala-malmi',
          type: 'sub_district',
          municipality: 'Helsinki',
        },
      ],
    },
    description: {
      fi: 'test-description-fi',
      sv: 'test-description-sv',
      en: 'test-description-en',
    },
    serviceOwner: {
      providerType: 'SELF_PRODUCED',
      type: 'MUNICIPAL_SERVICE',
    },
    targetGroups: [
      'ASSOCIATIONS',
      'CHILDREN_AND_FAMILIES',
      'ENTERPRISES',
      'INDIVIDUALS',
      'YOUTH',
    ],
    openingHours: {
      url: 'https://hauki.api.hel.fi/v1/resource/tprek:8740/opening_hours/',
      is_open_now_url:
        'https://hauki.api.hel.fi/v1/resource/tprek:8740/is_open_now/',
      today: [
        {
          startTime: '08:00:00',
          endTime: '20:00:00',
          endTimeOnNextDay: false,
          resourceState: 'open',
          fullDay: false,
        },
      ],
      data: [
        {
          date: '2025-12-03',
          times: [
            {
              startTime: '08:00:00',
              endTime: '20:00:00',
              endTimeOnNextDay: false,
              resourceState: 'open',
              fullDay: false,
            },
          ],
        },
      ],
    },
    reservation: {
      reservable: false,
      externalReservationUrl: null,
    },
    accessibility: {
      shortcomings: [
        {
          profile: 'hearing_aid',
          count: 11,
        },
        {
          profile: 'reduced_mobility',
          count: 22,
        },
        {
          profile: 'rollator',
          count: 33,
        },
        {
          profile: 'stroller',
          count: 44,
        },
        {
          profile: 'wheelchair',
          count: 66,
        },
      ],
    },
    images: [
      {
        url: 'https://example.org/getPublicFile.do?uuid=123456789',
        caption: null,
      },
    ],
    ontologyWords: [
      {
        id: '138',
        label: {
          fi: 'elokuvateatterit',
          sv: 'biografer',
          en: 'cinemas',
        },
      },
      {
        id: '214',
        label: {
          fi: 'juhlatilat',
          sv: 'festlokaler',
          en: 'banquet facilities',
        },
      },
    ],
    isCultureAndLeisureDivisionVenue: true,
    eventCount: 6196,
  },
} as const satisfies VenueProps;

describe('getUnifiedSearchVenueResolvers', () => {
  it.each([
    { field: 'name', expectedValue: testVenue.venue.name },
    { field: 'description', expectedValue: testVenue.venue.description },
    { field: 'location', expectedValue: testVenue.venue.location },
    { field: 'openingHours', expectedValue: testVenue.venue.openingHours },
    { field: 'images', expectedValue: testVenue.venue.images },
    { field: 'ontologyWords', expectedValue: testVenue.venue.ontologyWords },
    { field: 'serviceOwner', expectedValue: testVenue.venue.serviceOwner },
    { field: 'reservation', expectedValue: testVenue.venue.reservation },
    { field: 'targetGroups', expectedValue: testVenue.venue.targetGroups },
    { field: 'accessibility', expectedValue: testVenue.venue.accessibility },
    { field: 'meta', expectedValue: testVenue.venue.meta },
    {
      field: 'isCultureAndLeisureDivisionVenue',
      expectedValue: testVenue.venue.isCultureAndLeisureDivisionVenue,
    },
    {
      field: 'eventCount',
      expectedValue: testVenue.venue.eventCount,
    },
  ] as const)(
    'should return correct value for field $field',
    ({ field, expectedValue }) => {
      expect(getUnifiedSearchVenueResolvers()[field](testVenue)).toStrictEqual(
        expectedValue
      );
    }
  );

  it.each([
    {
      profile: 'hearing_aid',
      expectedValue: { profile: 'hearing_aid', count: 11 },
    },
    {
      profile: 'reduced_mobility',
      expectedValue: { profile: 'reduced_mobility', count: 22 },
    },
    {
      profile: 'rollator',
      expectedValue: { profile: 'rollator', count: 33 },
    },
    {
      profile: 'stroller',
      expectedValue: { profile: 'stroller', count: 44 },
    },
    {
      profile: 'visually_impaired',
      expectedValue: undefined, // Not present in test data
    },
    {
      profile: 'wheelchair',
      expectedValue: { profile: 'wheelchair', count: 66 },
    },
  ] as const satisfies {
    profile: AccessibilityProfileType;
    expectedValue?: { profile: AccessibilityProfileType; count: number };
  }[])(
    'accessibilityShortcomingFor should work with profile $profile',
    ({ profile, expectedValue }) => {
      expect(
        getUnifiedSearchVenueResolvers()['accessibilityShortcomingFor'](
          testVenue,
          { profile }
        )
      ).toStrictEqual(expectedValue);
    }
  );

  it.each([
    { inputValue: undefined, expectedValue: false },
    { inputValue: null, expectedValue: false },
  ] as const)(
    'fallback value for $inputValue isCultureAndLeisureDivisionVenue should be $expectedValue',
    ({ inputValue, expectedValue }) => {
      const modifiedTestVenue = {
        venue: {
          ...testVenue.venue,
          isCultureAndLeisureDivisionVenue: inputValue,
        },
      } as const satisfies VenueProps;

      expect(
        getUnifiedSearchVenueResolvers()['isCultureAndLeisureDivisionVenue'](
          modifiedTestVenue
        )
      ).toStrictEqual(expectedValue);
    }
  );

  it.each([
    { inputValue: undefined, expectedValue: 0 },
    { inputValue: null, expectedValue: 0 },
  ] as const)(
    'fallback value for $inputValue eventCount should be $expectedValue',
    ({ inputValue, expectedValue }) => {
      const modifiedTestVenue = {
        venue: {
          ...testVenue.venue,
          eventCount: inputValue,
        },
      } as const satisfies VenueProps;

      expect(
        getUnifiedSearchVenueResolvers()['eventCount'](modifiedTestVenue)
      ).toStrictEqual(expectedValue);
    }
  );
});

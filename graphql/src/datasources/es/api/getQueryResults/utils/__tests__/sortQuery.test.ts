import { describe, expect, it } from 'vitest';

import {
  ELASTIC_SEARCH_INDICES,
  ES_LOCATION_INDEX,
} from '../../../../constants.js';
import { sortQuery } from '../sortQuery.js';

describe('sortQuery', () => {
  it.each(
    ELASTIC_SEARCH_INDICES.filter((esIndex) => esIndex != ES_LOCATION_INDEX)
  )('test non-op for index %s', (esIndex) => {
    const origQuery = {
      query: { bool: { someFieldName: 'someFieldValue' } },
    } as const;

    for (const order of ['ASCENDING', 'DESCENDING'] as const) {
      const orderByFields = { orderByName: { order } } as const;

      for (const language of ['fi', 'sv', 'en'] as const) {
        const query = structuredClone(origQuery);
        sortQuery(query, esIndex, language, orderByFields);

        // Expect the input parameter `query` to remain unchanged
        expect(query).toStrictEqual(origQuery);
      }
    }
  });

  it.each(['ASCENDING', 'DESCENDING'] as const)(
    'test location index orderByName with %s order',
    (order) => {
      const origQuery = {
        query: { bool: { someFieldName: 'someFieldValue' } },
      } as const;
      const orderByFields = { orderByName: { order } } as const;
      const expectedOrder = order === 'ASCENDING' ? 'asc' : 'desc';

      for (const language of ['fi', 'sv', 'en'] as const) {
        const query = structuredClone(origQuery);
        sortQuery(query, ES_LOCATION_INDEX, language, orderByFields);

        // Expect to mutate the input parameter `query`
        expect(query).not.toStrictEqual(origQuery);

        expect(query).toStrictEqual({
          query: {
            bool: {
              someFieldName: 'someFieldValue',
            },
          },
          sort: {
            [`venue.name.${language}.keyword`]: {
              missing: '_last',
              order: expectedOrder,
            },
          },
        });
      }
    }
  );

  it.each([
    'hearing_aid',
    'reduced_mobility',
    'rollator',
    'stroller',
    'visually_impaired',
    'wheelchair',
  ] as const)(
    'test location index with orderByAccessibilityProfile %s',
    (orderByAccessibilityProfile) => {
      const origQuery = {
        query: { bool: { someFieldName: 'someFieldValue' } },
      } as const;
      const orderByFields = { orderByAccessibilityProfile } as const;

      for (const language of ['fi', 'sv', 'en'] as const) {
        const query = structuredClone(origQuery);
        sortQuery(query, ES_LOCATION_INDEX, language, orderByFields);

        // Expect to mutate the input parameter `query`
        expect(query).not.toStrictEqual(origQuery);

        expect(query).toStrictEqual({
          query: {
            bool: {
              someFieldName: 'someFieldValue',
            },
          },
          sort: [
            {
              'venue.accessibility.shortcomings.count': {
                missing: '_last',
                nested: {
                  filter: {
                    term: {
                      'venue.accessibility.shortcomings.profile':
                        orderByAccessibilityProfile,
                    },
                  },
                  max_children: 1,
                  path: 'venue.accessibility.shortcomings',
                },
                order: 'asc',
              },
            },
            {
              [`venue.name.${language}.keyword`]: {
                missing: '_last',
                order: 'asc',
              },
            },
          ],
        });
      }
    }
  );

  it.each([
    [-123.45, 42.75, 'ASCENDING'],
    [32.5, -10.1, 'DESCENDING'],
  ] as const)(
    'test location index orderByDistance with latitude %s, longitude %s and %s order',
    (latitude, longitude, order) => {
      const origQuery = {
        query: { bool: { someFieldName: 'someFieldValue' } },
      } as const;
      const orderByFields = {
        orderByDistance: { latitude, longitude, order },
      } as const;
      const expectedOrder = order === 'ASCENDING' ? 'asc' : 'desc';

      for (const language of ['fi', 'sv', 'en'] as const) {
        const query = structuredClone(origQuery);
        sortQuery(query, ES_LOCATION_INDEX, language, orderByFields);

        // Expect to mutate the input parameter `query`
        expect(query).not.toStrictEqual(origQuery);

        expect(query).toStrictEqual({
          query: {
            bool: {
              someFieldName: 'someFieldValue',
            },
          },
          sort: {
            _geo_distance: {
              ignore_unmapped: true,
              location: {
                lat: latitude,
                lon: longitude,
              },
              order: expectedOrder,
            },
          },
        });
      }
    }
  );
});

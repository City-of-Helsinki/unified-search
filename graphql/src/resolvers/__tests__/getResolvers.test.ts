import { describe, it, expect } from 'vitest';

import { getResolvers } from '../getResolvers.js';

describe('getResolvers', () => {
  /**
   * This test ensures that any changes to the available resolvers through
   * the GraphQL API are intentional.
   *
   * If you add or remove a resolver, please update this test accordingly!
   */
  it('should contain only the known fields and nothing else', async () => {
    const result = getResolvers();
    expect(result).toStrictEqual({
      GeoJSONCRSProperties: {
        __resolveType: expect.any(Function),
      },
      GeoJSONFeature: {
        geometry: expect.any(Function),
        type: expect.any(Function),
      },
      GeoJSONGeometryInterface: {
        __resolveType: expect.any(Function),
      },
      GeoJSONInterface: {
        __resolveType: expect.any(Function),
      },
      GeoJSONPoint: {
        coordinates: expect.any(Function),
        type: expect.any(Function),
      },
      OpeningHours: {
        today: expect.any(Function),
      },
      Query: {
        administrativeDivisions: expect.any(Function),
        ontologyTree: expect.any(Function),
        ontologyWords: expect.any(Function),
        unifiedSearch: expect.any(Function),
        unifiedSearchCompletionSuggestions: expect.any(Function),
      },
      RawJSON: {
        data: expect.any(Function),
      },
      SearchResultConnection: {
        count: expect.any(Function),
        edges: expect.any(Function),
        es_results: expect.any(Function),
        max_score: expect.any(Function),
        pageInfo: expect.any(Function),
      },
      UnifiedSearchVenue: {
        accessibility: expect.any(Function),
        accessibilityShortcomingFor: expect.any(Function),
        description: expect.any(Function),
        images: expect.any(Function),
        location: expect.any(Function),
        meta: expect.any(Function),
        name: expect.any(Function),
        ontologyWords: expect.any(Function),
        openingHours: expect.any(Function),
        reservation: expect.any(Function),
        serviceOwner: expect.any(Function),
        targetGroups: expect.any(Function),
        isCultureAndLeisureDivisionVenue: expect.any(Function),
      },
    });
  });
});

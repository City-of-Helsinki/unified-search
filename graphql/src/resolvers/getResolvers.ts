import { getOpeningHoursResolvers } from './getOpeningHoursResolvers.js';
import { getSearchResultConnectionResolvers } from './getSearchResultConnectionResolvers.js';
import { getTopLevelGeoJSONResolvers } from './getTopLevelGeoJSONResolvers.js';
import { getUnifiedSearchVenueResolvers } from './getUnifiedSearchVenueResolvers.js';
import { getQueryResolvers } from './query/getQueryResolvers.js';
import { RawJSONResolver } from './RawJSONResolver.js';

/**
 * Get all resolvers for the GraphQL server.
 */
export function getResolvers() {
  return {
    Query: { ...getQueryResolvers() },
    SearchResultConnection: { ...getSearchResultConnectionResolvers() },
    UnifiedSearchVenue: { ...getUnifiedSearchVenueResolvers() },
    OpeningHours: { ...getOpeningHoursResolvers() },
    RawJSON: RawJSONResolver(),
    ...getTopLevelGeoJSONResolvers(),
  };
}

import { GeoJSONResolvers } from './GeoJSONResolvers.js';
import { OpeningHoursResolver } from './OpeningHoursResolver.js';
import { administrativeDivisionsResolver } from './query/administrativeDivisionsResolver.js';
import { ontologyTreeResolver } from './query/ontologyTreeResolver.js';
import { ontologyWordsResolver } from './query/ontologyWordsResolver.js';
import { unifiedSearchCompletionSuggestionsResolver } from './query/unifiedSearchCompletionSuggestionsResolver.js';
import { unifiedSearchResolver } from './query/unifiedSearchResolver.js';
import { RawJSONResolver } from './RawJSONResolver.js';
import { SearchResultConnectionResolver } from './SearchResultConnectionResolver.js';
import { UnifiedSearchVenueResolver } from './UnifiedSearchVenueResolver.js';

/**
 * Get all resolvers for the GraphQL server.
 */
export function getResolvers() {
  return {
    Query: {
      unifiedSearch: unifiedSearchResolver,
      unifiedSearchCompletionSuggestions:
        unifiedSearchCompletionSuggestionsResolver,
      administrativeDivisions: administrativeDivisionsResolver,
      ontologyTree: ontologyTreeResolver,
      ontologyWords: ontologyWordsResolver,
    },
    SearchResultConnection: SearchResultConnectionResolver(),
    UnifiedSearchVenue: UnifiedSearchVenueResolver(),
    OpeningHours: OpeningHoursResolver(),
    RawJSON: RawJSONResolver(),
    ...GeoJSONResolvers(),
  };
}

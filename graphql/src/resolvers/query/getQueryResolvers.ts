import { administrativeDivisionsResolver } from './administrativeDivisionsResolver.js';
import { ontologyTreeResolver } from './ontologyTreeResolver.js';
import { ontologyWordsResolver } from './ontologyWordsResolver.js';
import { unifiedSearchCompletionSuggestionsResolver } from './unifiedSearchCompletionSuggestionsResolver.js';
import { unifiedSearchResolver } from './unifiedSearchResolver.js';

/**
 * Get all Query resolvers for the GraphQL server.
 */
export function getQueryResolvers() {
  return {
    unifiedSearch: unifiedSearchResolver,
    unifiedSearchCompletionSuggestions:
      unifiedSearchCompletionSuggestionsResolver,
    administrativeDivisions: administrativeDivisionsResolver,
    ontologyTree: ontologyTreeResolver,
    ontologyWords: ontologyWordsResolver,
  };
}

import type {
  QueryContext,
  SuggestionsParams,
} from '../../datasources/es/types.js';
import { elasticLanguageFromGraphqlLanguage } from '../../utils.js';

export async function unifiedSearchCompletionSuggestionsResolver(
  _source: unknown,
  { prefix, languages, index, size }: SuggestionsParams,
  { dataSources }: QueryContext
) {
  const res = await dataSources.elasticSearchAPI.getSuggestions({
    prefix,
    languages: elasticLanguageFromGraphqlLanguage(languages),
    size,
    index,
  });

  return {
    suggestions: res.suggest.suggestions[0].options.map((option) => ({
      label: option.text,
    })),
  };
}

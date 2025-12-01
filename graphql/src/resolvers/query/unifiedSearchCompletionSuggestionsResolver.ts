import type { QueryContext } from '../../datasources/es/index.js';
import type { SuggestionsParams } from '../../datasources/es/types.js';
import type { EsResults } from '../../types.js';
import { elasticLanguageFromGraphqlLanguage } from '../../utils.js';

export async function unifiedSearchCompletionSuggestionsResolver(
  _source: unknown,
  { prefix, languages, index, size }: SuggestionsParams,
  { dataSources }: QueryContext
) {
  const res: EsResults = await dataSources.elasticSearchAPI.getSuggestions({
    prefix,
    languages: elasticLanguageFromGraphqlLanguage(languages),
    size,
    index,
  });

  const options = res.suggest.suggestions[0].options;
  const optionsArray = Array.isArray(options) ? options : [options];

  return {
    suggestions: optionsArray.map((option) => ({
      label: option.text,
    })),
  };
}

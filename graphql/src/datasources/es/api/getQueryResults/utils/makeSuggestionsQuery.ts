import type { SuggestionsParams } from '../../../types.js';

export function makeSuggestionsQuery({
  prefix,
  languages,
  size,
}: Pick<SuggestionsParams, 'prefix' | 'languages' | 'size'>) {
  // Uses completion suggester to provide a prefix based auto-complete feature, see
  // https://www.elastic.co/guide/en/elasticsearch/reference/current/search-suggesters-completion.html
  return {
    // Hide all source fields to decrease network load
    _source: '',
    // "suggest" here is an Elasticsearch's keyword to enable suggest feature:
    suggest: {
      // "suggestions" here is an arbitrary name (i.e. changeable):
      suggestions: {
        prefix,
        completion: {
          // "suggest" here is an arbitrary field name defined in data importers:
          field: 'suggest',
          skip_duplicates: true,
          size, // The number of suggestions to return
          contexts: {
            language: languages,
          },
        },
      },
    },
  };
}

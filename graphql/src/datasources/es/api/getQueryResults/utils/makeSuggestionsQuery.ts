import type { SuggestionsParams } from '../../../types.js';

export function makeSuggestionsQuery({
  prefix,
  languages,
  size,
}: Pick<SuggestionsParams, 'prefix' | 'languages' | 'size'>) {
  return {
    // Hide all source fields to decrease network load
    _source: '',
    suggest: {
      suggestions: {
        prefix,
        completion: {
          field: 'suggest',
          skip_duplicates: true,
          size,
          contexts: {
            language: languages,
          },
        },
      },
    },
  };
}

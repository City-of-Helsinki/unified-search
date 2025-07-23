import { type ElasticLanguage } from '../../../types.js';
import { ES_DEFAULT_INDEX } from '../constants.js';
import { type ElasticSearchAPI } from '../index.js';
import type { ElasticSearchIndex } from '../types.js';

export type GetSuggestionProps = {
  prefix: string;
  languages: ElasticLanguage[];
  size: number;
  index: ElasticSearchIndex;
};

export default async function getSuggestions(
  request: ElasticSearchAPI['post'],
  { prefix, languages, size, index = ES_DEFAULT_INDEX }: GetSuggestionProps
) {
  const query = {
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

  return await request(`${index}/_search`, {
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(query),
  });
}

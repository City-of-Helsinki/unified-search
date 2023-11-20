import { type ElasticSearchAPI } from '..';
import { type ElasticLanguage } from '../../../types';
import { ES_DEFAULT_INDEX } from '../constants';
import type { ElasticSearchIndex } from '../types';

export type getSuggestionProps = {
  prefix: string;
  languages: ElasticLanguage[];
  size: number;
  index: ElasticSearchIndex;
};

export default async function getSuggestions(
  request: ElasticSearchAPI['post'],
  { prefix, languages, size, index = ES_DEFAULT_INDEX }: getSuggestionProps
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

  return await request(`${index}/_search`, undefined, {
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(query),
  });
}

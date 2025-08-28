import { ES_DEFAULT_INDEX } from '../constants.js';
import type { ElasticSearchAPI } from '../index.js';
import type { SuggestionsParams } from '../types.js';
import { makeSuggestionsQuery } from './getQueryResults/utils/makeSuggestionsQuery.js';

export default async function getSuggestions(
  request: ElasticSearchAPI['post'],
  { prefix, languages, size, index = ES_DEFAULT_INDEX }: SuggestionsParams
) {
  const query = makeSuggestionsQuery({ prefix, languages, size });

  return await request(`${index}/_search`, {
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(query),
  });
}

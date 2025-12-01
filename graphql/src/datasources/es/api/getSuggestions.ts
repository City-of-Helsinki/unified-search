import type { Client } from '@elastic/elasticsearch';

import { ES_DEFAULT_INDEX } from '../constants.js';
import type { SuggestionsParams } from '../types.js';
import { makeSuggestionsQuery } from './getQueryResults/utils/makeSuggestionsQuery.js';

export default async function getSuggestions(
  esClient: Client,
  { prefix, languages, size, index = ES_DEFAULT_INDEX }: SuggestionsParams
) {
  const query = makeSuggestionsQuery({ prefix, languages, size });

  return await esClient.search({
    index,
    ...query,
  });
}

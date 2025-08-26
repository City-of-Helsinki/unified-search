import type { GetQueryResultsProps } from './types.js';
import { ES_DEFAULT_INDEX } from '../../constants.js';
import { type ElasticSearchAPI } from '../../index.js';
import { queryBuilder } from './utils/queryBuilder.js';

export default async function getQueryResults(
  request: ElasticSearchAPI['post'],
  { index = ES_DEFAULT_INDEX, ...queryProps }: GetQueryResultsProps
) {
  const query = queryBuilder({ index, ...queryProps });

  return await request(`${index}/_search`, {
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(query),
  });
}

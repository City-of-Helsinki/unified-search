import { Client } from '@elastic/elasticsearch';

import type { GetQueryResultsProps } from './types.js';
import { ES_DEFAULT_INDEX } from '../../constants.js';
import { queryBuilder } from './utils/queryBuilder.js';
import type { EsHitSource } from '../../../../types.js';

export default async function getQueryResults(
  esClient: Client,
  { index = ES_DEFAULT_INDEX, ...queryProps }: GetQueryResultsProps
) {
  const query = queryBuilder({ index, ...queryProps });

  return await esClient.search<EsHitSource>({
    index: index,
    ...query,
  });
}

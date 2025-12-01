import type { estypes } from '@elastic/elasticsearch';

import type { QueryContext } from '../../datasources/es/index.js';
import type { AdministrativeDivisionParams } from '../../datasources/es/types.js';
import type { EsHitSource, EsResults } from '../../types.js';

export async function administrativeDivisionsResolver(
  _,
  args: AdministrativeDivisionParams,
  { dataSources }: QueryContext
) {
  const res: EsResults =
    await dataSources.elasticSearchAPI.getAdministrativeDivisions(args);
  return res.hits.hits.map((hit: estypes.SearchHit<EsHitSource>) => ({
    id: hit._id,
    ...hit._source,
  }));
}

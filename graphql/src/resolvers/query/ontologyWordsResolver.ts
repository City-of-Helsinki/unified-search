import type { estypes } from '@elastic/elasticsearch';

import type { QueryContext } from '../../datasources/es/index.js';
import type { OntologyWordParams } from '../../datasources/es/types.js';
import type { EsHitSource, EsResults } from '../../types.js';

export async function ontologyWordsResolver(
  _,
  args: OntologyWordParams,
  { dataSources }: QueryContext
) {
  const res: EsResults =
    await dataSources.elasticSearchAPI.getOntologyWords(args);

  return res.hits.hits.map((hit: estypes.SearchHit<EsHitSource>) => ({
    id: hit._id,
    ...hit._source,
    label: hit._source?.name,
  }));
}

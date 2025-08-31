import type { QueryContext } from '../../datasources/es/index.js';
import type { OntologyTreeParams } from '../../datasources/es/types.js';
import type { EsHit, EsResults } from '../../types.js';

export async function ontologyTreeResolver(
  _,
  args: OntologyTreeParams,
  { dataSources }: QueryContext
) {
  const res: EsResults =
    await dataSources.elasticSearchAPI.getOntologyTree(args);
  return res.hits.hits.map((hit: EsHit) => ({
    id: hit._id,
    ...hit._source,
  }));
}

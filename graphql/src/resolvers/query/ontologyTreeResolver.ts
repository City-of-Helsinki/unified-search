import type {
  OntologyTreeParams,
  QueryContext,
} from '../../datasources/es/types.js';
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

import type {
  OntologyWordParams,
  QueryContext,
} from '../../datasources/es/types.js';
import type { EsHit, EsResults } from '../../types.js';

export async function ontologyWordsResolver(
  _,
  args: OntologyWordParams,
  { dataSources }: QueryContext
) {
  const res: EsResults =
    await dataSources.elasticSearchAPI.getOntologyWords(args);

  return res.hits.hits.map((hit: EsHit) => ({
    id: hit._id,
    ...hit._source,
    label: hit._source.name,
  }));
}

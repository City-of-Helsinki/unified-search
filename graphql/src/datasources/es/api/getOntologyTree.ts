import { ES_ONTOLOGY_TREE_INDEX } from '../constants.js';
import { type ElasticSearchAPI } from '../index.js';
import type {
  OntologyTreeParams,
  OntologyTreeQuery,
  OntologyTreeQueryBool,
} from '../types.js';

export default async function getOntologyTree(
  request: ElasticSearchAPI['post'],
  { rootId, leavesOnly }: OntologyTreeParams
) {
  const bool: OntologyTreeQueryBool = {
    ...(rootId && {
      filter: {
        bool: {
          should: [
            { term: { ancestorIds: rootId } },
            { term: { _id: rootId } },
          ],
        },
      },
    }),
    ...(leavesOnly && {
      must_not: { exists: { field: 'childIds' } },
    }),
  };
  const query: OntologyTreeQuery = {
    size: 10000,
    ...(bool && { query: { bool } }),
  };

  return await request(`${ES_ONTOLOGY_TREE_INDEX}/_search`, {
    body: JSON.stringify(query),
    headers: { 'Content-Type': 'application/json' },
  });
}

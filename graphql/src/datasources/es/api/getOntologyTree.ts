import { type ElasticSearchAPI } from '..';
import { ES_ONTOLOGY_TREE_INDEX } from '../constants';
import type {
  OntologyTreeParams,
  OntologyTreeQuery,
  OntologyTreeQueryBool,
} from '../types';

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

  return await request(
    `${ES_ONTOLOGY_TREE_INDEX}/_search`,
    JSON.stringify(query),
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );
}

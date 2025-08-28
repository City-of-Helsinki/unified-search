import type {
  OntologyTreeParams,
  OntologyTreeQuery,
  OntologyTreeQueryBool,
} from '../../../types.js';

export function makeOntologyTreeQuery({
  rootId,
  leavesOnly,
}: OntologyTreeParams): OntologyTreeQuery {
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
  return {
    size: 10000,
    ...(bool && { query: { bool } }),
  };
}

import {
  OntologyTreeLeavesOnlyFilter,
  OntologyTreeParams,
  OntologyTreeQuery,
  OntologyTreeRootIdFilter,
} from '../../../types.js';

const makeRootIdFilter = (
  rootId: OntologyTreeParams['rootId']
): OntologyTreeRootIdFilter => ({
  filter: {
    bool: {
      should: [
        // Either is a descendant of the rootId or is the rootId itself:
        { term: { ancestorIds: rootId } },
        { term: { _id: rootId } },
      ],
    },
  },
});

const makeLeavesOnlyFilter = (): OntologyTreeLeavesOnlyFilter => ({
  // Leaves have no children:
  must_not: {
    exists: {
      field: 'childIds',
    },
  },
});

export const makeOntologyTreeQuery = ({
  rootId,
  leavesOnly,
}: OntologyTreeParams): OntologyTreeQuery => ({
  size: 10000,
  query: {
    bool: {
      ...(rootId && makeRootIdFilter(rootId)),
      ...(leavesOnly && makeLeavesOnlyFilter()),
    },
  },
});

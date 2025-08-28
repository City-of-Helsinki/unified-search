import { describe, expect, it } from 'vitest';

import { makeOntologyTreeQuery } from '../makeOntologyTreeQuery.js';

const EXPECTED_ONTOLOGY_TREE_QUERY_SIZE = 10000;
const ROOT_IDS_TO_TEST = ['123', 'testingId'] as const;

describe('makeOntologyTreeQuery', () => {
  it('test with undefined params', () => {
    const result = makeOntologyTreeQuery({});
    expect(result).toStrictEqual({
      query: {
        bool: {},
      },
      size: EXPECTED_ONTOLOGY_TREE_QUERY_SIZE,
    });
  });

  it.each(ROOT_IDS_TO_TEST)('test with rootId %j only', (rootId) => {
    const result = makeOntologyTreeQuery({ rootId });
    expect(result).toStrictEqual({
      query: {
        bool: {
          filter: {
            bool: {
              should: [
                {
                  term: {
                    ancestorIds: rootId,
                  },
                },
                {
                  term: {
                    _id: rootId,
                  },
                },
              ],
            },
          },
        },
      },
      size: EXPECTED_ONTOLOGY_TREE_QUERY_SIZE,
    });
  });

  it('test with leavesOnly only', () => {
    const result = makeOntologyTreeQuery({ leavesOnly: true });
    expect(result).toStrictEqual({
      query: {
        bool: {
          must_not: {
            exists: {
              field: 'childIds',
            },
          },
        },
      },
      size: EXPECTED_ONTOLOGY_TREE_QUERY_SIZE,
    });
  });

  it.each(ROOT_IDS_TO_TEST)('test with rootId %j and leavesOnly', (rootId) => {
    const result = makeOntologyTreeQuery({ rootId, leavesOnly: true });
    expect(result).toStrictEqual({
      query: {
        bool: {
          filter: {
            bool: {
              should: [
                {
                  term: {
                    ancestorIds: rootId,
                  },
                },
                {
                  term: {
                    _id: rootId,
                  },
                },
              ],
            },
          },
          must_not: {
            exists: {
              field: 'childIds',
            },
          },
        },
      },
      size: EXPECTED_ONTOLOGY_TREE_QUERY_SIZE,
    });
  });
});

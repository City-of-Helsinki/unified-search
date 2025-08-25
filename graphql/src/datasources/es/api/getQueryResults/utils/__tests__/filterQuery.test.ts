import { describe, expect, it } from 'vitest';

import { filterQuery } from '../filterQuery.js';

describe('filterQuery', () => {
  it('test query mutation with all filters', () => {
    const origQuery = { query: { bool: { someFieldName: 'someFieldValue' } } };
    const query = structuredClone(origQuery);
    const filterProps = {
      administrativeDivisionIds: ['adminDivId1', 'adminDivId2'],
      ontologyTreeIdOrSets: [['treeId1'], ['treeId2', 'treeId3']],
      ontologyWordIdOrSets: [['wordId1', 'wordId2'], ['wordId3']],
      providerTypes: ['ASSOCIATION', 'SELF_PRODUCED'],
      serviceOwnerTypes: ['MUNICIPAL_SERVICE', 'PRIVATE_SERVICE'],
      targetGroups: ['CHILDREN_AND_FAMILIES', 'YOUTH'],
      mustHaveReservableResource: true,
      openAt: '2025-06-25T12:34:45.123+06:00',
    };
    filterQuery(query, filterProps);

    // Expect to mutate the input parameter `query`
    expect(query).not.toEqual(origQuery);

    // Check the overall structure of the generated query
    expect(Object.keys(query)).toStrictEqual(['query']);
    expect(Object.keys(query.query)).toStrictEqual(['bool']);
    expect(query.query.bool).toHaveProperty('minimum_should_match', 1);
    expect(query.query.bool).toHaveProperty('someFieldName', 'someFieldValue');
    expect(query.query.bool).toHaveProperty('filter');
    expect(Object.keys(query.query.bool)).toHaveLength(3);

    // Check the generated filters
    //
    // @ts-expect-error 'filter' does exist as expected above
    expect(query.query.bool.filter).toMatchSnapshot();
  });

  it('test non-op without filters', () => {
    const origQuery = {
      query: { bool: { someFieldName: 'someFieldValue' } },
    } as const;
    const query = structuredClone(origQuery);
    const filterProps = {};
    filterQuery(query, filterProps);

    // Expect the input parameter `query` to remain unchanged
    expect(query).toStrictEqual(origQuery);
  });
});

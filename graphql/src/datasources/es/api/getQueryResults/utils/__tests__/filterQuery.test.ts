import { describe, expect, it } from 'vitest';

import { filterQuery } from '../filterQuery.js';

describe('filterQuery', () => {
  it('test query mutation with given filters', () => {
    const query = { query: { bool: { someFieldName: 'someFieldValue' } } };
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
    expect(query).toMatchSnapshot();
  });
});

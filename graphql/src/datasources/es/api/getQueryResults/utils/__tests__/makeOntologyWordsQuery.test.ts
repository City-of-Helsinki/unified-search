import { describe, expect, it } from 'vitest';

import { makeOntologyWordsQuery } from '../makeOntologyWordsQuery.js';

describe('makeOntologyWordsQuery', () => {
  it('test with undefined ids', () => {
    const result = makeOntologyWordsQuery({ ids: undefined });
    expect(result).toStrictEqual({});
  });

  it.each([{ ids: [] }, { ids: ['singleId'] }, { ids: ['id1', 'id2', 'id3'] }])(
    'test with defined ids %j',
    (params) => {
      const result = makeOntologyWordsQuery(params);
      expect(result).toStrictEqual({
        query: {
          terms: {
            _id: params.ids,
          },
        },
      });
    }
  );
});

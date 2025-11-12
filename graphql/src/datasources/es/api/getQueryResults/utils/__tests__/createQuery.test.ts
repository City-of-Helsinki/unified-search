import { describe, expect, it } from 'vitest';

import { LANGUAGES } from '../../../../../../constants.js';
import {
  ELASTIC_SEARCH_INDICES,
  SEARCH_ALL_SPECIAL_CHAR,
} from '../../../../constants.js';
import { createQuery } from '../createQuery.js';
import { getDefaultBoolQuery } from '../getDefaultBoolQuery.js';

describe('createQuery', () => {
  it.each(ELASTIC_SEARCH_INDICES)('test search all with index %s', (index) => {
    const query = createQuery({ index, text: SEARCH_ALL_SPECIAL_CHAR });

    expect(query).toStrictEqual({
      query: {
        bool: {
          should: [{ query_string: { query: '*' } }],
        },
      },
    });
  });

  it('test result corresponds to getDefaultBoolQuery', () => {
    for (const index of ELASTIC_SEARCH_INDICES) {
      for (const readonlyLanguages of [['fi'], LANGUAGES] as const) {
        for (const text of ['testing', 'Kamppi 00100'] as const) {
          const languages = [...readonlyLanguages];
          const query = createQuery({ index, languages, text });
          const expectedQuery = getDefaultBoolQuery({ index, languages, text });
          expect(query).toStrictEqual(expectedQuery);
        }
      }
    }
  });
});

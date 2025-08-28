import { describe, expect, it } from 'vitest';

import { makeSuggestionsQuery } from '../makeSuggestionsQuery.js';

describe('makeSuggestionsQuery', () => {
  it.each([
    { prefix: '', languages: [], size: 0 }, // edge case, but let's check it doesn't throw
    { prefix: 'aik', languages: ['fi' as const], size: 5 },
    { prefix: 'la', languages: ['sv' as const], size: 10 },
    {
      prefix: 'senio',
      languages: ['fi' as const, 'sv' as const, 'en' as const],
      size: 100,
    },
  ])('test with parameters %j', (params) => {
    const result = makeSuggestionsQuery(params);
    expect(result).toStrictEqual({
      _source: '',
      suggest: {
        suggestions: {
          completion: {
            contexts: {
              language: params.languages,
            },
            field: 'suggest',
            size: params.size,
            skip_duplicates: true,
          },
          prefix: params.prefix,
        },
      },
    });
  });
});

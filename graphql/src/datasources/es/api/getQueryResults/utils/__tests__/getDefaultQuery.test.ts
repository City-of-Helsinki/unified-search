import { describe, expect, it } from 'vitest';

import { getDefaultBoolQuery } from '../getDefaultBoolQuery.js';

describe('getDefaultBoolQuery', () => {
  it.each([
    { text: 'testing' as const },
    {
      index: 'location' as const,
      languages: ['fi' as const, 'sv' as const],
      text: 'kamppi',
    },
  ])(
    'test output using given parameters %j',
    (parameters: Parameters<typeof getDefaultBoolQuery>[0]) => {
      const result = getDefaultBoolQuery(parameters);
      expect(result).toMatchSnapshot();
    }
  );
});

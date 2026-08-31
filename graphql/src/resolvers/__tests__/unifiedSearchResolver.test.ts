import type { GraphQLResolveInfoWithCacheControl } from '@apollo/cache-control-types';
import { afterEach, describe, expect, it, vi } from 'vitest';

import type { QueryContext } from '../../datasources/es/index.js';
import { unifiedSearchResolver } from '../query/unifiedSearchResolver.js';

vi.mock('../../utils.js', () => ({
  createCursor: vi.fn(),
  edgesFromEsResults: vi.fn(() => []),
  elasticLanguageFromGraphqlLanguage: vi.fn(),
  getEsOffsetPaginationQuery: vi.fn(() => ({ from: 0, size: 10 })),
  validateOrderByArguments: vi.fn(),
}));

const ORIGINAL_CACHE_MAX_AGE = process.env.CACHE_MAX_AGE;

const makeSearchResult = () => ({
  hits: {
    hits: Array.from({ length: 1000 }, () => ({})),
    total: { value: 1000 },
  },
});

describe('unifiedSearchResolver', () => {
  afterEach(() => {
    if (ORIGINAL_CACHE_MAX_AGE === undefined) {
      delete process.env.CACHE_MAX_AGE;
    } else {
      process.env.CACHE_MAX_AGE = ORIGINAL_CACHE_MAX_AGE;
    }
  });

  it.each([
    { cacheMaxAge: '7200', expectedMaxAge: 7200, scenario: 'configured' },
    { cacheMaxAge: undefined, expectedMaxAge: 3600, scenario: 'default' },
  ])(
    'uses the $scenario cache max age for large result sets',
    async ({ cacheMaxAge, expectedMaxAge }) => {
      if (cacheMaxAge === undefined) {
        delete process.env.CACHE_MAX_AGE;
      } else {
        process.env.CACHE_MAX_AGE = cacheMaxAge;
      }

      const getQueryResults = vi.fn().mockResolvedValue(makeSearchResult());
      const setCacheHint = vi.fn();
      const context = {
        dataSources: { elasticSearchAPI: { getQueryResults } },
      } as unknown as QueryContext;
      const info = {
        cacheControl: { setCacheHint },
      } as unknown as GraphQLResolveInfoWithCacheControl;

      await unifiedSearchResolver(undefined, {}, context, info);

      expect(setCacheHint).toHaveBeenCalledWith({ maxAge: expectedMaxAge });
    }
  );
});

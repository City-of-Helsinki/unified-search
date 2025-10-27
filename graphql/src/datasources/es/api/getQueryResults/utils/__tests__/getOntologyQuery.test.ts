import { describe, expect, it } from 'vitest';

import type { ElasticLanguage } from '../../../../../../types.js';
import { getOntologyMatchers, getOntologyQuery } from '../getOntologyQuery.js';

describe('getOntologyQuery', () => {
  it.each([
    { languages: [] as const satisfies ElasticLanguage[] },
    { ontology: 'test-ontology123' as const },
    {
      index: 'location' as const,
      languages: ['fi' as const, 'sv' as const],
      ontology: 'vesijumppa',
    },
  ])(
    'test output using given parameters %j',
    (parameters: Parameters<typeof getOntologyQuery>[0]) => {
      const result = getOntologyQuery(parameters);
      expect(result).toMatchSnapshot();
    }
  );
});

describe('getOntologyMatchers', () => {
  it.each([
    { query: 'test-query', languages: [] as const satisfies ElasticLanguage[] },
    { query: 'yso:1234' as const },
    {
      index: 'location' as const,
      languages: ['fi' as const, 'sv' as const],
      query: 'yso:999',
    },
  ])(
    'test output using given parameters %j',
    (parameters: Parameters<typeof getOntologyMatchers>[0]) => {
      const result = getOntologyMatchers(parameters);
      expect(result).toMatchSnapshot();
    }
  );
});

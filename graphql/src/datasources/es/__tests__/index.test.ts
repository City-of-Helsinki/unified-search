import { afterEach, describe, expect, it, vi } from 'vitest';

import { ElasticSearchAPI } from '../index.js';

const validEsUris = [
  'http://elasticsearch-node1:9200/',
  'http://example.com:1212/',
  'http://test.example.org/',
  'https://a.b.c.com:9200/test/a/3/?a1=b&p2=3%40#section',
  'https://elasticsearch.example.com:9200/some/path',
  'https://example.com/',
  'https://example.com:1234/',
  'https://localhost:9200/',
  'https://localhost:9200/elasticsearch/',
] as const;

const invalidEsUris = [
  '',
  '/path/to/elasticsearch',
  'not-a-valid-url',
] as const;

const esUrisWithCredentials = [
  'gopher://user:pass@example.com:443/',
  'https://:password@localhost:9200/',
  'https://user:password@localhost:9200/',
  'https://user@localhost:9200/',
] as const;

const noAuthHeaderExpected = [
  { username: undefined, password: undefined },
  { username: undefined, password: '' },
  { username: '', password: undefined },
  { username: '', password: '' },
  { username: '', password: 'somepassword' },
  { username: undefined, password: 'somepassword' },
] as const;

const authHeaderExpected = [
  { username: 'username', password: undefined },
  { username: 'username', password: '' },
  { username: 'username', password: 'password' },
  { username: 'User!@Name#123', password: 'p@Ss:w:Rd!42' },
] as const;

describe('ElasticSearchAPI', () => {
  const ORIGINAL_PROCESS_ENV = { ...process.env };

  afterEach(() => {
    process.env = { ...ORIGINAL_PROCESS_ENV };
    vi.restoreAllMocks();
  });

  describe('constructor', () => {
    it.each(validEsUris)('should set baseURL with ES_URI %s', (esUri) => {
      process.env.ES_URI = esUri;
      const api = new ElasticSearchAPI();
      expect(api.baseURL).toStrictEqual(esUri);
    });

    it.each(invalidEsUris)(
      'should throw error with invalid ES_URI %s',
      (esUri) => {
        process.env.ES_URI = esUri;
        expect(() => new ElasticSearchAPI()).toThrowError('Invalid URL');
      }
    );

    it.each(esUrisWithCredentials)(
      'should throw error with ES_URI %s because of embedded credentials',
      (esUri) => {
        process.env.ES_URI = esUri;
        expect(() => new ElasticSearchAPI()).toThrowError(
          'Elasticsearch URI must not contain credentials'
        );
      }
    );
  });

  describe('willSendRequest', () => {
    it.each(authHeaderExpected)(
      'should add correct authorization header to requests with ' +
        'ES_USERNAME $username and ES_PASSWORD $password',
      ({ username, password }) => {
        process.env.ES_URI = validEsUris[0];
        process.env.ES_USERNAME = username;
        process.env.ES_PASSWORD = password;
        const api = new ElasticSearchAPI();
        const mockRequest = { headers: {}, params: new URLSearchParams() };

        api.willSendRequest('test/path', mockRequest);

        const authHeader = mockRequest.headers['authorization'];
        const credentials = `${username}:${password ?? ''}`;
        const expectedPrefix = 'Basic ' as const;

        expect(authHeader.slice(0, expectedPrefix.length)).toStrictEqual(
          expectedPrefix
        );
        expect(atob(authHeader.slice(expectedPrefix.length))).toStrictEqual(
          credentials
        );
      }
    );

    it.each(noAuthHeaderExpected)(
      'should not add authorization header to requests with ' +
        'ES_USERNAME $username and ES_PASSWORD $password',
      ({ username, password }) => {
        process.env.ES_URI = validEsUris[0];
        process.env.ES_USERNAME = username;
        process.env.ES_PASSWORD = password;
        const api = new ElasticSearchAPI();
        const mockRequest = { headers: {}, params: new URLSearchParams() };

        api.willSendRequest('test/path', mockRequest);

        expect(mockRequest.headers['authorization']).toBeUndefined();
      }
    );
  });
});

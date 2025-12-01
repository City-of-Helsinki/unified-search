import { afterEach, describe, expect, it, vi } from 'vitest';

import { ElasticSearchAPI } from '../index.js';

const validEsUri = 'http://elasticsearch-node1:9200/';

const validEsUriMappings = [
  {
    esUri: validEsUri,
    expectedResult: [validEsUri],
  },
  {
    esUri: 'https://example.com:1212/',
    expectedResult: ['https://example.com:1212/'],
  },
  {
    esUri: 'http://elastic-test-uri:9200',
    expectedResult: ['http://elastic-test-uri:9200/'],
  },
  {
    esUri: 'https://localhost:9200/',
    expectedResult: ['https://localhost:9200/'],
  },
  {
    // Handles multiple URIs separated by commas
    esUri:
      'http://elasticsearch-node1:9200/,https://example.com:1212/,http://elastic-test-uri:9200',
    expectedResult: [
      'http://elasticsearch-node1:9200/',
      'https://example.com:1212/',
      'http://elastic-test-uri:9200/',
    ],
  },
  {
    // Handles whitespaces around URIs and omits default ports (80 for HTTP and 443 for HTTPS)
    esUri:
      ' http://elasticsearch-node1:80/ ,\thttps://example.com:443,\nhttp://elastic-test-uri:9200\r\n',
    expectedResult: [
      'http://elasticsearch-node1/',
      'https://example.com/',
      'http://elastic-test-uri:9200/',
    ],
  },
] as const;

const invalidEsUris = [
  '',
  '/path/to/elasticsearch',
  'not-a-valid-url',
  // Path, query and fragment parts are not allowed:
  'https://a.b.c.com:9200/test/a/3/?a1=b&p2=3%40#section',
  'https://elasticsearch.example.com:9200/some/path',
  'https://localhost:9200/elasticsearch/',
] as const;

const esUrisWithCredentials = [
  'gopher://user:pass@example.com:443/',
  'https://:password@localhost:9200/',
  'https://user:password@localhost:9200/',
  'https://user@localhost:9200/',
  // Handles multiple URIs
  'http://elasticsearch-node1:9200/,https://user@localhost:9200/',
  // Handles whitespaces around URIs
  ' http://test-node1:80/ ,\thttps://a.com:443,\nhttp://user:pass@test-uri:9200\r\n',
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
    it.each(validEsUriMappings)(
      "should set Elasticsearch client's connection URLs correctly with ES_URI $esUri",
      ({ esUri, expectedResult }) => {
        process.env.ES_URI = esUri;
        const api = new ElasticSearchAPI();
        expect(api.esClient.connectionPool.connections).toHaveLength(
          expectedResult.length
        );
        for (const [index, expectedUrl] of expectedResult.entries()) {
          expect(
            api.esClient.connectionPool.connections[index].url.toString()
          ).toStrictEqual(expectedUrl);
        }
      }
    );

    it.each(invalidEsUris)(
      'should throw error with invalid ES_URI %s',
      (esUri) => {
        process.env.ES_URI = esUri;
        expect(() => new ElasticSearchAPI()).toThrowError(/invalid URL/i);
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

  describe('Elasticsearch client auth', () => {
    it.each(authHeaderExpected)(
      'should add correct authorization header to requests with ' +
        'ES_USERNAME $username and ES_PASSWORD $password',
      ({ username, password }) => {
        process.env.ES_URI = validEsUri;
        process.env.ES_USERNAME = username;
        process.env.ES_PASSWORD = password;
        const api = new ElasticSearchAPI();

        expect(api.esClient.connectionPool.auth).toStrictEqual({
          username,
          password: password ?? '',
        });
      }
    );

    it.each(noAuthHeaderExpected)(
      'should not add authorization header to requests with ' +
        'ES_USERNAME $username and ES_PASSWORD $password',
      ({ username, password }) => {
        process.env.ES_URI = validEsUri;
        process.env.ES_USERNAME = username;
        process.env.ES_PASSWORD = password;
        const api = new ElasticSearchAPI();

        expect(api.esClient.connectionPool.auth).toBeUndefined();
      }
    );
  });
});

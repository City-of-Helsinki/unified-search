import { afterEach, describe, expect, it, vi } from 'vitest';

import { ElasticSearchAPI } from '../index.js';

const nonNullAuthHeaderTestParams = [
  {
    description: 'username and password',
    uri: 'https://username:password@localhost:9200/',
    expectedUsername: 'username',
    expectedPassword: 'password',
    expectedResult: {
      baseURL: 'https://localhost:9200/',
      authHeader: 'Basic dXNlcm5hbWU6cGFzc3dvcmQ=',
    },
  },
  {
    description: 'special chars in username',
    uri: 'https://user%40name:password@localhost:9200/',
    expectedUsername: 'user@name',
    expectedPassword: 'password',
    expectedResult: {
      baseURL: 'https://localhost:9200/',
      authHeader: 'Basic dXNlckBuYW1lOnBhc3N3b3Jk',
    },
  },
  {
    description: 'special chars in password',
    uri: 'https://username:p%40ssw%3Ard%21@localhost:9200/',
    expectedUsername: 'username',
    expectedPassword: 'p@ssw:rd!',
    expectedResult: {
      baseURL: 'https://localhost:9200/',
      authHeader: 'Basic dXNlcm5hbWU6cEBzc3c6cmQh',
    },
  },
  {
    description: 'special chars in username & password',
    uri: 'https://user%40name:p%40ss%3Aw%3Ard%21@localhost:9200/',
    expectedUsername: 'user@name',
    expectedPassword: 'p@ss:w:rd!',
    expectedResult: {
      baseURL: 'https://localhost:9200/',
      authHeader: 'Basic dXNlckBuYW1lOnBAc3M6dzpyZCE=',
    },
  },
  {
    description: 'complex credentials and path',
    uri: 'https://elastic:changeme@elasticsearch.example.com:9200/some/path',
    expectedUsername: 'elastic',
    expectedPassword: 'changeme',
    expectedResult: {
      baseURL: 'https://elasticsearch.example.com:9200/some/path',
      authHeader: 'Basic ZWxhc3RpYzpjaGFuZ2VtZQ==',
    },
  },
  {
    description: 'HTTP protocol',
    uri: 'http://admin:secret@elasticsearch-node1:9200',
    expectedUsername: 'admin',
    expectedPassword: 'secret',
    expectedResult: {
      baseURL: 'http://elasticsearch-node1:9200/',
      authHeader: 'Basic YWRtaW46c2VjcmV0',
    },
  },
  {
    description: 'default port for HTTPS',
    uri: 'https://user:pass@example.com:443/',
    expectedUsername: 'user',
    expectedPassword: 'pass',
    expectedResult: {
      // Port is omitted because 443 is default for HTTPS
      baseURL: 'https://example.com/',
      authHeader: 'Basic dXNlcjpwYXNz',
    },
  },
  {
    description: 'default port for HTTP',
    uri: 'http://user123:pass123@test.example.org:80/',
    expectedUsername: 'user123',
    expectedPassword: 'pass123',
    expectedResult: {
      // Port is omitted because 80 is default for HTTP
      baseURL: 'http://test.example.org/',
      authHeader: 'Basic dXNlcjEyMzpwYXNzMTIz',
    },
  },
  {
    description: 'non-default port for HTTPS',
    uri: 'https://user:pass@example.com:1234/',
    expectedUsername: 'user',
    expectedPassword: 'pass',
    expectedResult: {
      baseURL: 'https://example.com:1234/',
      authHeader: 'Basic dXNlcjpwYXNz',
    },
  },
  {
    description: 'non-default port for HTTP',
    uri: 'http://user:pass@example.com:1212/',
    expectedUsername: 'user',
    expectedPassword: 'pass',
    expectedResult: {
      baseURL: 'http://example.com:1212/',
      authHeader: 'Basic dXNlcjpwYXNz',
    },
  },
  {
    description: 'query parameters and fragment',
    uri: 'https://user:pass@a.b.c.com:9200/test/a/3/?a1=b&p2=3%40#section',
    expectedUsername: 'user',
    expectedPassword: 'pass',
    expectedResult: {
      baseURL: 'https://a.b.c.com:9200/test/a/3/?a1=b&p2=3%40#section',
      authHeader: 'Basic dXNlcjpwYXNz',
    },
  },
  {
    description: 'trailing path segments',
    uri: 'https://user:pass@localhost:9200/elasticsearch/',
    expectedUsername: 'user',
    expectedPassword: 'pass',
    expectedResult: {
      baseURL: 'https://localhost:9200/elasticsearch/',
      authHeader: 'Basic dXNlcjpwYXNz',
    },
  },
  {
    description: 'username, empty password, no path',
    uri: 'https://username:@localhost:9200/',
    expectedUsername: 'username',
    expectedPassword: '',
    expectedResult: {
      baseURL: 'https://localhost:9200/',
      authHeader: 'Basic dXNlcm5hbWU6',
    },
  },
  {
    description: 'username, no path',
    uri: 'https://username@localhost:9200/',
    expectedUsername: 'username',
    expectedPassword: '',
    expectedResult: {
      baseURL: 'https://localhost:9200/',
      authHeader: 'Basic dXNlcm5hbWU6',
    },
  },
] as const;

const nullAuthHeaderTestParams = [
  {
    description: 'no credentials, no path',
    uri: 'https://localhost:9200/',
    expectedBaseURL: 'https://localhost:9200/',
  },
  {
    description: 'no credentials but path',
    uri: 'https://elasticsearch.example.com:9200/some/path',
    expectedBaseURL: 'https://elasticsearch.example.com:9200/some/path',
  },
  {
    description: 'no credentials but query params',
    uri: 'https://localhost:9200/?timeout=30',
    expectedBaseURL: 'https://localhost:9200/?timeout=30',
  },
] as const;

const errorTestParams = [
  {
    description: 'invalid URL format',
    uri: 'not-a-valid-url',
    expectedError: 'Failed to parse Elasticsearch URI',
  },
  {
    description: 'empty string',
    uri: '',
    expectedError: 'Failed to parse Elasticsearch URI',
  },
  {
    description: 'relative path',
    uri: '/path/to/elasticsearch',
    expectedError: 'Failed to parse Elasticsearch URI',
  },
  {
    description: 'missing protocol',
    uri: 'localhost:9200',
    expectedError: 'Unacceptable protocol localhost: in Elasticsearch URI',
  },
  {
    description: 'unacceptable protocol (gopher)',
    uri: 'gopher://user:pass@example.com:443/',
    expectedError: 'Unacceptable protocol gopher: in Elasticsearch URI',
  },
] as const;

const allUsedNonErrorTestURIs = [
  ...nonNullAuthHeaderTestParams.map((param) => param.uri),
  ...nullAuthHeaderTestParams.map((param) => param.uri),
];

describe('ElasticSearchAPI', () => {
  const ORIGINAL_ES_URI = process.env.ES_URI;

  afterEach(() => {
    process.env.ES_URI = ORIGINAL_ES_URI;
    vi.restoreAllMocks();
  });

  describe('constructor', () => {
    it.each(allUsedNonErrorTestURIs)(
      'should set baseURL and authHeader using parseElasticSearchURI("%s")',
      (uri) => {
        process.env.ES_URI = uri;

        const { baseURL: expectedBaseURL, authHeader: expectedAuthHeader } =
          ElasticSearchAPI.prototype.parseElasticSearchURI(uri);

        const spy = vi.spyOn(
          ElasticSearchAPI.prototype,
          'parseElasticSearchURI'
        );

        const api = new ElasticSearchAPI();

        expect(spy).toHaveBeenCalledExactlyOnceWith(uri);
        expect(api.baseURL).toStrictEqual(expectedBaseURL);
        expect(api.authHeader).toStrictEqual(expectedAuthHeader);
      }
    );
  });

  describe('willSendRequest', () => {
    it.each(nonNullAuthHeaderTestParams)(
      'should add authorization header to requests with ES_URI $uri',
      ({ uri }) => {
        process.env.ES_URI = uri;
        const api = new ElasticSearchAPI();
        const mockRequest = { headers: {}, params: new URLSearchParams() };

        api.willSendRequest('test/path', mockRequest);

        expect(mockRequest.headers['authorization']).toStrictEqual(
          api.authHeader
        );
      }
    );

    it.each(nullAuthHeaderTestParams)(
      'should not add authorization header to requests with ES_URI $uri',
      ({ uri }) => {
        process.env.ES_URI = uri;
        const api = new ElasticSearchAPI();
        const mockRequest = { headers: {}, params: new URLSearchParams() };

        api.willSendRequest('test/path', mockRequest);

        expect(mockRequest.headers['authorization']).toBeUndefined();
      }
    );
  });

  describe('parseElasticSearchURI', () => {
    describe('should move credentials from URI to authHeader', () => {
      it.each(nonNullAuthHeaderTestParams)(
        'with $description',
        ({ uri, expectedUsername, expectedPassword, expectedResult }) => {
          const result = ElasticSearchAPI.prototype.parseElasticSearchURI(uri);

          expect(result).toStrictEqual(expectedResult);

          // Verify that the base64-decoded authHeader matches the expected credentials
          const decodedCredentials = Buffer.from(
            result.authHeader.replace('Basic ', ''),
            'base64'
          ).toString('utf-8');
          expect(decodedCredentials).toStrictEqual(
            `${expectedUsername}:${expectedPassword}`
          );
        }
      );
    });

    describe('should remove any credentials from URIs w/o proper ones', () => {
      it.each(nullAuthHeaderTestParams)(
        '$description',
        ({ uri, expectedBaseURL }) => {
          const result = ElasticSearchAPI.prototype.parseElasticSearchURI(uri);

          expect(result).toStrictEqual({
            baseURL: expectedBaseURL,
            authHeader: null,
          });
        }
      );
    });

    describe('should throw error', () => {
      it.each(errorTestParams)(
        'with $description',
        ({ uri, expectedError }) => {
          expect(() =>
            ElasticSearchAPI.prototype.parseElasticSearchURI(uri)
          ).toThrow(expectedError);
        }
      );
    });
  });
});

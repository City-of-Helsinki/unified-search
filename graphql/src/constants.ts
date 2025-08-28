import type { CorsOptions } from 'cors';

export const GraphQlToElasticLanguageMap = {
  FINNISH: 'fi',
  SWEDISH: 'sv',
  ENGLISH: 'en',
} as const;

/**
 * The reserved special characters in Elastic Search are:
 * `+ - = && || > < ! ( ) { } [ ] ^ " ~ * ? : \ /`.
 * Reference: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#_reserved_characters
 */
export const elasticSearchQueryStringSpecialCharsRegExpPattern =
  /(\+|-|=|&&|\|\||>|<|!|\(|\)|\{|\}|\[|\]|\^|"|~|\*|\?|:|\\|\/)/gi;

/**
 * CORS (Cross-Origin Resource Sharing) configuration for the GraphQL server.
 *
 * Configuration options documented at:
 * https://github.com/expressjs/cors/tree/v2.8.5?tab=readme-ov-file#configuration-options
 */
export const corsConfig = {
  // Allow all origins because:
  // 1. This is a public API
  // 2. No authentication is used
  // 3. No authorization is used
  origin: '*',
  // Don't allow credentials to be sent with requests
  // because this a public API and no authentication is used.
  // https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Access-Control-Allow-Credentials
  credentials: false,
  // Allow methods:
  // - OPTIONS for preflight requests
  // - POST for GraphQL queries and mutations
  methods: ['OPTIONS', 'POST'],
  // Allow CORS-safelisted request headers
  // Accept, Accept-Language, Content-Language, Content-Type and Range
  // that are always allowed and bypass the restrictions on Content-Type header
  // to allow application/json content type.
  //
  // https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Access-Control-Allow-Headers
  // https://developer.mozilla.org/en-US/docs/Glossary/CORS-safelisted_request_header
  allowedHeaders: ['Content-Type'],
} as const satisfies CorsOptions;

// Content Security Policy (CSP) keywords
// See https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP
export const CSP = {
  none: "'none'",
  reportSample: "'report-sample'",
  self: "'self'",
  strictDynamic: "'strict-dynamic'",
  unsafeAllowRedirects: "'unsafe-allow-redirects'",
  unsafeEval: "'unsafe-eval'",
  unsafeHashes: "'unsafe-hashes'",
  unsafeInline: "'unsafe-inline'",
} as const;

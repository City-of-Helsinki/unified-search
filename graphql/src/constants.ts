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

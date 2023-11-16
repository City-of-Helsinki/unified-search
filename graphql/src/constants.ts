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

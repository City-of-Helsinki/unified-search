export const ES_ADMINISTRATIVE_DIVISION_INDEX =
  'administrative_division' as const;
export const ES_HELSINKI_COMMON_ADMINISTRATIVE_DIVISION_INDEX =
  'helsinki_common_administrative_division' as const;
export const ES_ONTOLOGY_TREE_INDEX = 'ontology_tree' as const;
export const ES_ONTOLOGY_WORD_INDEX = 'ontology_word' as const;
export const ES_LOCATION_INDEX = 'location' as const;
export const ES_DEFAULT_INDEX = ES_LOCATION_INDEX;

export const ELASTIC_SEARCH_INDICES = [
  ES_ADMINISTRATIVE_DIVISION_INDEX,
  ES_HELSINKI_COMMON_ADMINISTRATIVE_DIVISION_INDEX,
  ES_ONTOLOGY_TREE_INDEX,
  ES_ONTOLOGY_WORD_INDEX,
  ES_LOCATION_INDEX,
] as const;

export const VENUE_SEARCH_RESULT_FIELD = 'venue' as const;
export const SEARCH_RESULT_FIELDS = [VENUE_SEARCH_RESULT_FIELD] as const;

export const ELASTIC_SEARCH_URI: string = process.env.ES_URI;
export const DEFAULT_TIME_ZONE = 'Europe/Helsinki' as const;
// The default page size when the first argument is not given.
// This is the default page size set by OpenSearch / ElasticSearch
export const ES_DEFAULT_PAGE_SIZE = 10 as const;

/**
 * @deprecated Used by the clients to fetch any results, since response is empty for the empty string.
 *
 * The asterisk ('*') is an operational character in the ElasticSearch,
 * but all the operational cahracters are escaped by `/src/constants/elasticSearchQueryStringSpecialCharsRegExpPattern`.
 *
 * This is deprecated, because we have had no actual need to separate empty string and asterisk queries --
 * The empty query string could do what the asterisk query now does.
 */
export const SEARCH_ALL_SPECIAL_CHAR = '*';

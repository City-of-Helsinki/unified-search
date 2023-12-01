import { GraphQlToElasticLanguageMap } from '../../../../../constants';
import type { ElasticLanguage, TranslatableField } from '../../../../../types';
import { escapeQuery } from '../../../../../utils';
import { ES_DEFAULT_INDEX, SEARCH_ALL_SPECIAL_CHAR } from '../../../constants';
import { searchFieldsBoostMapping } from '../constants';
import type { GetQueryResultsProps, QueryFilterClauses } from '../types';

const getQueryString = (text?: string) =>
  text && text !== SEARCH_ALL_SPECIAL_CHAR
    ? escapeQuery(text)
    : SEARCH_ALL_SPECIAL_CHAR;

type DefaultBoolQueryClausesType =
  | {
      match_bool_prefix: {
        [key in TranslatableField]?: QueryFilterClauses;
      };
    }
  | {
      match_phrase: {
        [key in TranslatableField]?: QueryFilterClauses;
      };
    };

type DefaultQueryStringQueryClausesType = {
  query_string: QueryFilterClauses & { fields: TranslatableField[] };
};

type DefaultBoolQueryClausesAccumulatorType = {
  [key in ElasticLanguage]?: DefaultBoolQueryClausesType;
};

type DefaultQueryStringQueryClausesAccumulatorType = {
  [key in ElasticLanguage]?: DefaultQueryStringQueryClausesType;
};

/**
 * @returns An ElasticSearch query object. Example:
 * ```
 * { "query": {"bool": { "should": [
 *  {
 *    "match_bool_prefix": {
 *      "venue.description.fi": {
 *        "query": "Itäkeskuksen uimahalli / Kuntosali",
 *        "operator": "or",
 *        "fuzziness": "AUTO",
 *        "boost": "1"
 *      }
 *    }
 *  },
 *  {
 *    "match_bool_prefix": {
 *      "venue.name.fi": {
 *        "query": "Itäkeskuksen uimahalli / Kuntosali",
 *        "operator": "or",
 *        "fuzziness": "AUTO",
 *        "boost": "3"
 *      }
 *    }
 *  },
 *  {
 *    "match_phrase": {
 *      "venue.description.fi": {
 *        "query": "Itäkeskuksen uimahalli / Kuntosali",
 *        "boost": 2
 *      }
 *    }
 *  },
 *  {
 *    "match_phrase": {
 *      "venue.name.fi": {
 *        "query": "Itäkeskuksen uimahalli / Kuntosali",
 *        "boost": 6
 *      }
 *    }
 *  }
 * ]}}}
 * ```
 * */
export function getDefaultBoolQuery({
  index = ES_DEFAULT_INDEX,
  languages = Object.values(GraphQlToElasticLanguageMap),
  text,
}: Pick<GetQueryResultsProps, 'index' | 'languages' | 'text'>) {
  const should = Object.values(
    languages.reduce(
      (acc: DefaultBoolQueryClausesAccumulatorType, language) => ({
        ...acc,
        [language]: [
          ...Object.entries(searchFieldsBoostMapping).map(
            ([boost, searchFields]) => ({
              match_bool_prefix: {
                ...searchFields(language, index).reduce<{
                  [key in TranslatableField]?: QueryFilterClauses;
                }>(
                  (queries, queryField) => ({
                    ...queries,
                    [queryField]: {
                      query: text,
                      operator: 'or',
                      fuzziness: 'AUTO',
                      boost,
                    },
                  }),
                  {}
                ),
              },
            })
          ),
          ...Object.entries(searchFieldsBoostMapping).map(
            ([boost, searchFields]) => ({
              match_phrase: {
                ...searchFields(language, index).reduce<{
                  [key in TranslatableField]?: QueryFilterClauses;
                }>(
                  (queries, queryField) => ({
                    ...queries,
                    [queryField]: {
                      query: text,
                      boost: parseInt(boost) * 2,
                    },
                  }),
                  {}
                ),
              },
            })
          ),
        ],
      }),
      {}
    )
  ).flat();
  return {
    query: {
      bool: {
        should,
      },
    },
  };
}

/**
 * @deprecated Use getDefaultBoolQuery instead.
 * @returns An ElasticSearch query object. Example:
 * ```
 * { "query": { "bool": { "should": [
 *   {
 *     "query_string": {
 *       "query": "Itäkeskuksen uimahalli \\\\/ Kuntosali",
 *       "type": "bool_prefix",
 *       "boost": "1",
 *       "fields": ["venue.description.fi"]
 *     }
 *   },
 *   {
 *     "query_string": {
 *       "query": "Itäkeskuksen uimahalli \\\\/ Kuntosali",
 *       "type": "bool_prefix",
 *       "boost": "3",
 *       "fields": ["venue.name.fi"]
 *     }
 *   }
 * ]}}}
 * ```
 */
export function getDefaultQueryStringQuery({
  index = ES_DEFAULT_INDEX,
  languages = Object.values(GraphQlToElasticLanguageMap),
  text,
}: Pick<GetQueryResultsProps, 'index' | 'languages' | 'text'>) {
  const should = Object.values(
    languages.reduce(
      (acc: DefaultQueryStringQueryClausesAccumulatorType, language) => ({
        ...acc,
        [language]: Object.entries(searchFieldsBoostMapping)
          // Don't map empty field sets to query
          .filter(([, searchFields]) => searchFields(language, index).length)
          .map(([boost, searchFields]) => ({
            // You can use the `query_string` query to create a complex search
            // that includes wildcard characters,
            // searches across multiple fields, and more.
            // While versatile, the query is strict and
            // returns an error if the query string includes any invalid syntax.
            // See: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html.
            query_string: {
              // Escape the query string so the special chars are not acting as operators.
              query: getQueryString(text),
              // Creates a match_bool_prefix query on each field and combines the _score from each field.
              // See: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-multi-match-query.html#type-bool-prefix.
              type: 'bool_prefix',
              boost,
              fields: searchFields(language, index),
            },
          })),
      }),
      {}
    )
  ).flat();
  return {
    query: {
      bool: {
        should,
      },
    },
  };
}

export enum QueryType {
  MatchBoolPrefix = 'match_bool_prefix',
  QueryString = 'query_string',
}

const defaultQueryForType: Record<
  QueryType,
  ({
    index,
    languages,
    text,
  }: Pick<GetQueryResultsProps, 'index' | 'languages' | 'text'>) => any
> = {
  [QueryType.MatchBoolPrefix]: getDefaultBoolQuery,
  [QueryType.QueryString]: getDefaultQueryStringQuery,
};

export function getDefaultQueryForQueryType(type: QueryType) {
  return defaultQueryForType[type];
}

import { GraphQlToElasticLanguageMap } from '../../../../../constants';
import type { ElasticLanguage, TranslatableField } from '../../../../../types';
import { ES_DEFAULT_INDEX } from '../../../constants';
import { searchFieldsBoostMapping } from '../constants';
import type { GetQueryResultsProps, QueryFilterClauses } from '../types';

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

type DefaultBoolQueryClausesAccumulatorType = {
  [key in ElasticLanguage]?: DefaultBoolQueryClausesType;
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

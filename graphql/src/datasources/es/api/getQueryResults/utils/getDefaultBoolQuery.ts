import { GraphQlToElasticLanguageMap } from '../../../../../constants.js';
import type {
  ElasticLanguage,
  TranslatableField,
} from '../../../../../types.js';
import { ES_DEFAULT_INDEX } from '../../../constants.js';
import { searchFieldsBoostMapping } from '../constants.js';
import type { GetQueryResultsProps, QueryFilterClauses } from '../types.js';
import { getOntologyMatchers } from './getOntologyQuery.js';

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
 * Search from names and titles, etc, using `match_bool_prefix`.
 */
const searchWithBoolPrefix = ({
  language,
  index,
  text,
}: Pick<GetQueryResultsProps, 'index' | 'text'> & {
  language: ElasticLanguage;
}) => {
  return Object.entries(searchFieldsBoostMapping).map(
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
  );
};

/**
 * Search from the ontology fields using `multi_match`.
 */
const searchWithOntology = ({
  language,
  index,
  text,
}: Pick<GetQueryResultsProps, 'index' | 'text'> & {
  language: ElasticLanguage;
}) => {
  return getOntologyMatchers({
    languages: [language],
    index,
    query: text,
  })[language];
};

/**
 * Search from names and titles, etc, using `match_phrase`.
 * When searching with a phrase and boosting the score result for them,
 * the exact results will be higher in the relevance.
 */
const searchWithPhrase = ({
  language,
  index,
  text,
}: Pick<GetQueryResultsProps, 'index' | 'text'> & {
  language: ElasticLanguage;
}) => {
  return Object.entries(searchFieldsBoostMapping).map(
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
  );
};

/**
 * @returns An ElasticSearch query object. Example:
 * ```
 * { "query": {"bool": { "should": [
 *   {
 *     "match_bool_prefix": {
 *       "venue.description.fi": {
 *         "query": "*",
 *         "operator": "or",
 *         "fuzziness": "AUTO",
 *         "boost": "1"
 *       }
 *     }
 *   },
 *   {
 *     "match_bool_prefix": {
 *       "venue.name.fi": {
 *         "query": "*",
 *         "operator": "or",
 *         "fuzziness": "AUTO",
 *         "boost": "3"
 *       }
 *     }
 *   },
 *   {
 *     "match_phrase": {
 *       "venue.description.fi": { "query": "*", "boost": 2 }
 *     }
 *   },
 *   {
 *     "match_phrase": {
 *       "venue.name.fi": { "query": "*", "boost": 6 }
 *     }
 *   },
 *   {
 *     "multi_match": {
 *       "query": "*",
 *       "fields": [
 *         "links.raw_data.ontologyword_ids_enriched.extra_searchwords_fi",
 *         "links.raw_data.ontologyword_ids_enriched.ontologyword_fi",
 *         "links.raw_data.ontologytree_ids_enriched.name_fi",
 *         "links.raw_data.ontologytree_ids_enriched.extra_searchwords_fi"
 *       ]
 *     }
 *   }
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
          ...searchWithBoolPrefix({ index, language, text }),
          ...searchWithPhrase({ index, language, text }),
          searchWithOntology({ index, language, text }),
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

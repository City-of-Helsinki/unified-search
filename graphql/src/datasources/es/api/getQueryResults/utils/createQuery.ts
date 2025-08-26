import { getDefaultBoolQuery } from './getDefaultBoolQuery.js';
import { getOntologyQuery } from './getOntologyQuery.js';
import { GraphQlToElasticLanguageMap } from '../../../../../constants.js';
import {
  ES_DEFAULT_INDEX,
  SEARCH_ALL_SPECIAL_CHAR,
} from '../../../constants.js';
import type { GetQueryResultsProps } from '../types.js';

export function createQuery({
  index = ES_DEFAULT_INDEX,
  languages = Object.values(GraphQlToElasticLanguageMap),
  text,
  ontology,
}: Pick<GetQueryResultsProps, 'index' | 'languages' | 'text' | 'ontology'>) {
  if (text === SEARCH_ALL_SPECIAL_CHAR) {
    return {
      query: {
        bool: {
          should: [{ query_string: { query: SEARCH_ALL_SPECIAL_CHAR } }],
        },
      },
    };
  }

  if (ontology) {
    // Resolve ontology
    // NOTE: This query has not been in use anymore in the events-helsinki-monorepo.
    //       It was earlier used with auto suggest menu.
    return getOntologyQuery({ index, languages, ontology });
  }
  return getDefaultBoolQuery({ index, languages, text });
}

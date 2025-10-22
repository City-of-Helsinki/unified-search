import { GraphQlToElasticLanguageMap } from '../../../../../constants.js';
import type { ElasticLanguage } from '../../../../../types.js';
import { ES_DEFAULT_INDEX } from '../../../constants.js';
import {
  MATCH_PHRASE_BOOST_MULTIPLIER,
  searchFieldsBoostMapping,
} from '../constants.js';
import type {
  GetQueryResultsProps,
  MatchBoolPrefixClause,
  MatchPhraseClause,
} from '../types.js';
import { getOntologyMatchers } from './getOntologyQuery.js';

export type SearchProps = Pick<GetQueryResultsProps, 'index' | 'text'> & {
  language: ElasticLanguage;
};

/**
 * Search from names and titles, etc, using `match_bool_prefix`.
 */
const searchWithBoolPrefix = (props: SearchProps): MatchBoolPrefixClause[] => {
  const { language, index, text } = props;
  return Object.entries(searchFieldsBoostMapping).map(
    ([boost, searchFields]) => ({
      match_bool_prefix: Object.fromEntries(
        searchFields(language, index).map((queryField) => [
          queryField,
          {
            query: text,
            operator: 'or',
            fuzziness: 'AUTO',
            // Need to convert boost back to float as records' keys are always strings:
            boost: Number.parseFloat(boost),
          },
        ])
      ),
    })
  );
};

/**
 * Search from the ontology fields using `multi_match`.
 */
const searchWithOntology = ({ language, index, text }: SearchProps) =>
  getOntologyMatchers({ languages: [language], index, query: text })[language];

/**
 * Search from names and titles, etc, using `match_phrase`.
 * When searching with a phrase and boosting the score result for them,
 * the exact results will be higher in the relevance.
 */
const searchWithPhrase = (props: SearchProps): MatchPhraseClause[] => {
  const { language, index, text } = props;
  return Object.entries(searchFieldsBoostMapping).map(
    ([boost, searchFields]) => ({
      match_phrase: Object.fromEntries(
        searchFields(language, index).map((queryField) => [
          queryField,
          {
            query: text,
            boost: Number.parseFloat(boost) * MATCH_PHRASE_BOOST_MULTIPLIER,
          },
        ])
      ),
    })
  );
};

/**
 * Get default boolean query for searching text across multiple fields and languages.
 * See related tests for example outputs.
 */
export function getDefaultBoolQuery({
  index = ES_DEFAULT_INDEX,
  languages = Object.values(GraphQlToElasticLanguageMap),
  text,
}: Pick<GetQueryResultsProps, 'index' | 'languages' | 'text'>) {
  const should = languages.flatMap((language) => [
    ...searchWithBoolPrefix({ index, language, text }),
    ...searchWithPhrase({ index, language, text }),
    searchWithOntology({ index, language, text }),
  ]);

  return {
    query: {
      bool: {
        should,
      },
    },
  };
}

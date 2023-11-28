import { GraphQlToElasticLanguageMap } from '../../../../../constants';
import { escapeQuery } from '../../../../../utils';
import { ES_DEFAULT_INDEX, SEARCH_ALL_SPECIAL_CHAR } from '../../../constants';
import { searchFieldsBoostMapping } from '../constants';
import type { GetQueryResultsProps } from '../types';

const getQueryString = (text?: string) =>
  text && text !== SEARCH_ALL_SPECIAL_CHAR
    ? escapeQuery(text)
    : SEARCH_ALL_SPECIAL_CHAR;

export function getDefaultQuery({
  index = ES_DEFAULT_INDEX,
  languages = Object.values(GraphQlToElasticLanguageMap),
  text,
}: Pick<GetQueryResultsProps, 'index' | 'languages' | 'text'>) {
  // Default query is to search the same thing in every language
  return languages.reduce(
    (acc, language) => ({
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
  );
}
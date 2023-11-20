import { escapeQuery } from '../../../../../utils';
import { searchFieldsBoostMapping } from '../constants';
import type { getQueryResultsProps } from '../types';

export function getDefaultQuery({
  index,
  languages,
  text,
}: Pick<getQueryResultsProps, 'index' | 'languages' | 'text'>) {
  // Default query is to search the same thing in every language
  const defaultQuery = languages.reduce(
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
            query: escapeQuery(text),
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
  return defaultQuery;
}

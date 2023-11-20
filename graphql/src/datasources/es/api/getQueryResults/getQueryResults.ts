import { DEFAULT_ELASTIC_LANGUAGE } from '../../../../types';
import { ES_DEFAULT_INDEX } from '../../constants';
import { type ElasticSearchAPI } from '../..';
import type { getQueryResultsProps } from './types';
import {
  getDefaultQuery,
  getOntologyFields,
  getFilters,
  sortQuery,
} from './utils';

function getQuery({
  index,
  languages,
  text,
  ontology,
  from,
  size,
  administrativeDivisionIds,
  ontologyTreeIdOrSets,
  ontologyWordIdOrSets,
  providerTypes,
  serviceOwnerTypes,
  targetGroups,
  mustHaveReservableResource,
  openAt,
  orderByAccessibilityProfile,
  orderByDistance,
  orderByName,
}: getQueryResultsProps) {
  const defaultQuery = getDefaultQuery({ index, languages, text });

  // Resolve query
  let query: any = {
    query: {
      bool: {
        should: Object.values(defaultQuery).flat(),
      },
    },
  };

  // Resolve ontology
  if (ontology) {
    const ontologyMatchers = languages.reduce(
      (acc, language) => ({
        ...acc,
        [language]: {
          multi_match: {
            query: ontology,
            fields: getOntologyFields(language, index),
          },
        },
      }),
      {}
    );

    query = {
      query: {
        bool: {
          should: languages.map((language) => ({
            bool: {
              must: [defaultQuery[language], ontologyMatchers[language]],
            },
          })),
        },
      },
    };
  }

  const filters = getFilters({
    administrativeDivisionIds,
    ontologyTreeIdOrSets,
    ontologyWordIdOrSets,
    providerTypes,
    serviceOwnerTypes,
    targetGroups,
    mustHaveReservableResource,
    openAt,
  });

  if (filters.length > 0) {
    query.query.bool.minimum_should_match = 1;
    query.query.bool.filter = filters;
  }

  const language = languages[0] ?? DEFAULT_ELASTIC_LANGUAGE;

  sortQuery(query, index, language, {
    orderByAccessibilityProfile,
    orderByDistance,
    orderByName,
  });

  // Resolve pagination
  return {
    from,
    size,
    ...query,
  };
}

export default async function getQueryResults(
  request: ElasticSearchAPI['post'],
  { index = ES_DEFAULT_INDEX, ...queryProps }: getQueryResultsProps
) {
  const query = getQuery({ index, ...queryProps });

  return await request(`${index}/_search`, undefined, {
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(query),
  });
}

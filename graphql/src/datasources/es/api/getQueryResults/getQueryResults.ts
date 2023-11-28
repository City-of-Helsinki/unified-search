import { DEFAULT_ELASTIC_LANGUAGE } from '../../../../types';
import { ES_DEFAULT_INDEX } from '../../constants';
import { type ElasticSearchAPI } from '../..';
import type { GetQueryResultsProps } from './types';
import { getDefaultQuery, getOntologyFields, sortQuery } from './utils';
import { filterQuery } from './utils/filterQuery';
import { GraphQlToElasticLanguageMap } from '../../../../constants';

function createQuery({
  index = ES_DEFAULT_INDEX,
  languages = Object.values(GraphQlToElasticLanguageMap),
  text,
  ontology,
}: Pick<GetQueryResultsProps, 'index' | 'languages' | 'text' | 'ontology'>) {
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
  return query;
}

function queryBuilder({
  index = ES_DEFAULT_INDEX,
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
}: GetQueryResultsProps) {
  const query = createQuery({ index, languages, text, ontology });

  filterQuery(query, {
    administrativeDivisionIds,
    ontologyTreeIdOrSets,
    ontologyWordIdOrSets,
    providerTypes,
    serviceOwnerTypes,
    targetGroups,
    mustHaveReservableResource,
    openAt,
  });

  const language = languages?.[0] ?? DEFAULT_ELASTIC_LANGUAGE;

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
  { index = ES_DEFAULT_INDEX, ...queryProps }: GetQueryResultsProps
) {
  const query = queryBuilder({ index, ...queryProps });

  return await request(`${index}/_search`, undefined, {
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(query),
  });
}
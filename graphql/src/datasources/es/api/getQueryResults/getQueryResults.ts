import { DEFAULT_ELASTIC_LANGUAGE } from '../../../../types';
import { ES_DEFAULT_INDEX, SEARCH_ALL_SPECIAL_CHAR } from '../../constants';
import { type ElasticSearchAPI } from '../..';
import type { GetQueryResultsProps } from './types';
import { getDefaultBoolQuery, sortQuery } from './utils';
import { filterQuery } from './utils/filterQuery';
import { GraphQlToElasticLanguageMap } from '../../../../constants';
import { getOntologyQuery } from './utils/getOntologyQuery';

function createQuery({
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
    // NOTE: This query has not been in use anymore in the events-helsinki-monorepo. It was earlier used with auto suggest menu.
    return getOntologyQuery({ index, languages, ontology });
  }
  return getDefaultBoolQuery({ index, languages, text });
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

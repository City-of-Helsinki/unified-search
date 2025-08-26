import { createQuery } from './createQuery.js';
import { filterQuery } from './filterQuery.js';
import { sortQuery } from './sortQuery.js';
import { DEFAULT_ELASTIC_LANGUAGE } from '../../../../../types.js';
import { ES_DEFAULT_INDEX } from '../../../constants.js';
import type { GetQueryResultsProps } from '../types.js';

export function queryBuilder({
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

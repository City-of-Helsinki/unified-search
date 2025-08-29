import { GraphQLResolveInfoWithCacheControl } from '@apollo/cache-control-types';

import type {
  AccessibilityProfileType,
  ElasticSearchIndex,
  OrderByDistanceParams,
  OrderByNameParams,
  QueryContext,
} from '../../datasources/es/types.js';
import type {
  ConnectionArguments,
  ConnectionCursorObject,
} from '../../types.js';
import {
  createCursor,
  edgesFromEsResults,
  elasticLanguageFromGraphqlLanguage,
  getEsOffsetPaginationQuery,
  getHits,
  validateOrderByArguments,
} from '../../utils.js';

type UnifiedSearchQuery = {
  text?: string;
  ontology?: string;
  administrativeDivisionIds?: string[];
  ontologyTreeIdOrSets?: string[][];
  ontologyWordIdOrSets?: string[][];
  providerTypes?: string[];
  serviceOwnerTypes?: string[];
  targetGroups?: string[];
  mustHaveReservableResource?: boolean;
  index?: ElasticSearchIndex;
  languages?: string[];
  openAt?: string;
  orderByDistance?: OrderByDistanceParams;
  orderByName?: OrderByNameParams;
  orderByAccessibilityProfile?: AccessibilityProfileType;
} & ConnectionArguments;

export async function unifiedSearchResolver(
  _source: unknown,
  {
    text,
    ontology,
    administrativeDivisionIds,
    ontologyTreeIdOrSets,
    ontologyWordIdOrSets,
    providerTypes,
    serviceOwnerTypes,
    targetGroups,
    mustHaveReservableResource,
    index,
    after,
    first,
    languages,
    openAt,
    orderByDistance,
    orderByName,
    orderByAccessibilityProfile,
  }: UnifiedSearchQuery,
  { dataSources }: QueryContext,
  info: GraphQLResolveInfoWithCacheControl
) {
  const connectionArguments = { after, first };
  const { from, size } = getEsOffsetPaginationQuery(connectionArguments);

  validateOrderByArguments(
    orderByDistance,
    orderByName,
    orderByAccessibilityProfile
  );

  const result = await dataSources.elasticSearchAPI.getQueryResults({
    text,
    ontology,
    administrativeDivisionIds,
    ontologyTreeIdOrSets,
    ontologyWordIdOrSets,
    providerTypes,
    serviceOwnerTypes,
    targetGroups,
    mustHaveReservableResource,
    index,
    from,
    size,
    languages: elasticLanguageFromGraphqlLanguage(languages),
    openAt,
    orderByDistance,
    orderByName,
    orderByAccessibilityProfile,
  });

  const getCursor = (offset: number) =>
    createCursor<ConnectionCursorObject>({
      offset: from + offset,
    });

  // Find shared data
  const edges = edgesFromEsResults(result, getCursor);
  const hits = getHits(result);

  if (result.hits.hits.length >= 1000) {
    info.cacheControl.setCacheHint({
      maxAge: parseInt(process.env.CACHE_MAX_AGE ?? '3600', 10),
    });
  }

  return { es_results: [result], edges, hits, connectionArguments };
}

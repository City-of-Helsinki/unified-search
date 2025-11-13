import type { ElasticLanguage } from '../../../../../types.js';
import { isDefined } from '../../../../../utils.js';
import { ES_LOCATION_INDEX } from '../../../constants.js';
import type {
  OrderByFields,
  GetQueryResultsProps,
  BoolQuery,
} from '../types.js';

export function sortQuery(
  query: BoolQuery,
  es_index: GetQueryResultsProps['index'],
  language: ElasticLanguage,
  {
    orderByDistance,
    orderByName,
    orderByAccessibilityProfile,
    showCultureAndLeisureDivisionFirst,
  }: OrderByFields
) {
  if (es_index === ES_LOCATION_INDEX) {
    query.sort = [];

    // Optionally sort first by Culture and Leisure Division
    if (showCultureAndLeisureDivisionFirst) {
      const orderByCultureAndLeisureDivisionClause = {
        'venue.isCultureAndLeisureDivisionVenue': {
          order: 'desc',
          missing: '_last',
        },
      } as const;

      query.sort.push(orderByCultureAndLeisureDivisionClause);
    }

    if (isDefined(orderByDistance)) {
      const orderByDistanceClause = {
        _geo_distance: {
          location: {
            lat: orderByDistance.latitude,
            lon: orderByDistance.longitude,
          },
          order: orderByDistance.order === 'DESCENDING' ? 'desc' : 'asc',
          ignore_unmapped: true,
        },
      } as const;

      query.sort.push(orderByDistanceClause);
    } else if (isDefined(orderByName)) {
      const orderByNameClause = {
        [`venue.name.${language}.keyword`]: {
          order: orderByName.order === 'DESCENDING' ? 'desc' : 'asc',
          missing: '_last',
        },
      } as const;

      query.sort.push(orderByNameClause);
    } else if (isDefined(orderByAccessibilityProfile)) {
      const orderByProfileShortcomingCountClause = {
        'venue.accessibility.shortcomings.count': {
          order: 'asc',
          nested: {
            path: 'venue.accessibility.shortcomings',
            filter: {
              term: {
                'venue.accessibility.shortcomings.profile':
                  orderByAccessibilityProfile,
              },
            },
            max_children: 1,
          },
          missing: '_last',
        },
      } as const;

      const orderByNameClause = {
        [`venue.name.${language}.keyword`]: {
          order: 'asc',
          missing: '_last',
        },
      } as const;

      query.sort.push(
        // Primary sort field (chosen accessibility profile's shortcoming count)
        orderByProfileShortcomingCountClause,
        // Secondary sort field (venue's name)
        orderByNameClause
      );
    } else {
      const orderByDescScoreClause = {
        _score: {
          order: 'desc',
        },
      };
      const orderByAscNameClause = {
        [`venue.name.${language}.keyword`]: {
          order: 'asc',
          missing: '_last',
        },
      } as const;

      // If none of the orderBy* parameters are used, sort by descending score
      // and ascending name to ensure consistent ordering of results.
      //
      // This prioritizes relevance first (by score), and then alphabetically
      // by name, if multiple results have the same score. This latter case
      // happens e.g. when searching without a search text.
      query.sort.push(orderByDescScoreClause, orderByAscNameClause);
    }
  }
}

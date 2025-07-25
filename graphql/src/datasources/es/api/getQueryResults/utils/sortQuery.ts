import type { ElasticLanguage } from '../../../../../types.js';
import { isDefined } from '../../../../../utils.js';
import {
  ES_LOCATION_INDEX,
  VENUE_SEARCH_RESULT_FIELD,
} from '../../../constants.js';
import type { ElasticSearchIndex, SearchResultField } from '../../../types.js';
import type {
  OrderByFields,
  GetQueryResultsProps,
  BoolQuery,
} from '../types.js';

const ElasticSearchIndexToSearchResultField: Record<
  Extract<ElasticSearchIndex, typeof ES_LOCATION_INDEX>,
  SearchResultField
> = {
  [ES_LOCATION_INDEX]: VENUE_SEARCH_RESULT_FIELD,
};

export function sortQuery(
  query: BoolQuery,
  es_index: GetQueryResultsProps['index'],
  language: ElasticLanguage,
  { orderByDistance, orderByName, orderByAccessibilityProfile }: OrderByFields
) {
  if (es_index === ES_LOCATION_INDEX) {
    const searchResultField = ElasticSearchIndexToSearchResultField[es_index];

    if (isDefined(orderByDistance)) {
      query.sort = {
        _geo_distance: {
          location: {
            lat: orderByDistance.latitude,
            lon: orderByDistance.longitude,
          },
          order: orderByDistance.order === 'DESCENDING' ? 'desc' : 'asc',
          ignore_unmapped: true,
        },
      };
    } else if (isDefined(orderByName)) {
      query.sort = {
        [`${searchResultField}.name.${language}.keyword`]: {
          order: orderByName.order === 'DESCENDING' ? 'desc' : 'asc',
          missing: '_last',
        },
      };
    } else if (
      isDefined(orderByAccessibilityProfile) &&
      searchResultField === VENUE_SEARCH_RESULT_FIELD
    ) {
      query.sort = [
        // Primary sort field (chosen accessibility profile's shortcoming count)
        {
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
        },
        // Secondary sort field (venue's name)
        {
          [`${searchResultField}.name.${language}.keyword`]: {
            order: 'asc',
            missing: '_last',
          },
        },
      ];
    }
  }
}

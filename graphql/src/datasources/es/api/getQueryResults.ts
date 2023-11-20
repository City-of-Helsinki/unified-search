import { DateTime } from 'luxon';
import { DEFAULT_ELASTIC_LANGUAGE, type ElasticLanguage } from '../../../types';
import { escapeQuery, isDefined } from '../../../utils';
import {
  DEFAULT_TIME_ZONE,
  ES_DEFAULT_INDEX,
  ES_EVENT_INDEX,
  ES_LOCATION_INDEX,
  EVENT_SEARCH_RESULT_FIELD,
  VENUE_SEARCH_RESULT_FIELD,
} from '../constants';
import type {
  ElasticSearchIndex,
  ArrayFilter,
  MustHaveReservableResourceFilter,
  OrderByDistanceParams,
  OrderByNameParams,
  AccessibilityProfileType,
  OpenAtFilter,
  SearchResultField,
} from '../types';
import { buildArrayFilter } from '../utils';
import { type ElasticSearchAPI } from '..';

const ElasticSearchIndexToSearchResultField: Record<
  Extract<ElasticSearchIndex, typeof ES_EVENT_INDEX | typeof ES_LOCATION_INDEX>,
  SearchResultField
> = {
  [ES_EVENT_INDEX]: EVENT_SEARCH_RESULT_FIELD,
  [ES_LOCATION_INDEX]: VENUE_SEARCH_RESULT_FIELD,
};

const buildMustHaveReservableResourceFilter =
  (): MustHaveReservableResourceFilter => ({
    bool: {
      should: [
        // i.e. OR
        {
          term: {
            'venue.resources.reservable': true,
          },
        },
        {
          exists: {
            field: 'venue.resources.externalReservationUrl',
          },
        },
      ],
    },
  });

export type getQueryResultsProps = {
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
  from?: number;
  size?: number;
  languages?: ElasticLanguage[];
  openAt?: string;
  orderByDistance?: OrderByDistanceParams;
  orderByName?: OrderByNameParams;
  orderByAccessibilityProfile?: AccessibilityProfileType;
};

export default async function getQueryResults(
  request: ElasticSearchAPI['post'],
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
    from,
    size,
    languages,
    openAt,
    orderByDistance,
    orderByName,
    orderByAccessibilityProfile,
  }: getQueryResultsProps
) {
  const es_index = index || ES_DEFAULT_INDEX;

  // Some fields should be boosted / weighted to get more relevant result set
  const searchFieldsBoostMapping = {
    // Normally weighted search fields for different indexes
    1: (lang: ElasticLanguage, index: ElasticSearchIndex) => {
      return (
        {
          [ES_LOCATION_INDEX]: [`venue.description.${lang}`],
          [ES_EVENT_INDEX]: [`event.name.${lang}`, `event.description.${lang}`],
        }[index] ?? []
      );
    },
    3: (lang: ElasticLanguage, index: ElasticSearchIndex) => {
      return (
        {
          [ES_LOCATION_INDEX]: [`venue.name.${lang}`],
        }[index] ?? []
      );
    },
  };

  // Ontology fields for different indexes
  const ontologyFields = (lang: ElasticLanguage, index: ElasticSearchIndex) => {
    if (index === ES_LOCATION_INDEX) {
      return [
        `links.raw_data.ontologyword_ids_enriched.extra_searchwords_${lang}`,
        `links.raw_data.ontologyword_ids_enriched.ontologyword_${lang}`,
        `links.raw_data.ontologytree_ids_enriched.name_${lang}`,
        `links.raw_data.ontologytree_ids_enriched.extra_searchwords_${lang}`,
      ];
    } else if (index === ES_EVENT_INDEX) {
      return [`ontology.${lang}`, 'ontology.alt'];
    }
    return [];
  };

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
            fields: ontologyFields(language, index),
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

  // Assume time zone DEFAULT_TIME_ZONE when there is no time zone offset provided by the client.
  const openAtDateTime = DateTime.fromISO(openAt, {
    zone: DEFAULT_TIME_ZONE,
  });
  const finalOpenAt = openAtDateTime.isValid ? openAtDateTime.toISO() : openAt;

  const filters: Array<
    ArrayFilter | OpenAtFilter | MustHaveReservableResourceFilter
  > = [
    ...buildArrayFilter(
      'venue.location.administrativeDivisions.id.keyword',
      administrativeDivisionIds ?? []
    ),
    ...(ontologyTreeIdOrSets ?? []).flatMap((ontologyTreeIdOrSet) =>
      buildArrayFilter(
        'links.raw_data.ontologytree_ids_enriched.id',
        ontologyTreeIdOrSet ?? []
      )
    ),
    ...(ontologyWordIdOrSets ?? []).flatMap((ontologyWordIdOrSet) =>
      buildArrayFilter(
        'links.raw_data.ontologyword_ids_enriched.id',
        ontologyWordIdOrSet ?? []
      )
    ),
    ...buildArrayFilter(
      'venue.serviceOwner.providerType.keyword',
      providerTypes ?? []
    ),
    ...buildArrayFilter(
      'venue.serviceOwner.type.keyword',
      serviceOwnerTypes ?? []
    ),
    ...buildArrayFilter('venue.targetGroups.keyword', targetGroups ?? []),
    ...(mustHaveReservableResource
      ? [buildMustHaveReservableResourceFilter()]
      : []),
    ...(finalOpenAt
      ? [
          {
            term: {
              'venue.openingHours.openRanges': finalOpenAt,
            },
          },
        ]
      : []),
  ];

  if (filters.length > 0) {
    query.query.bool.minimum_should_match = 1;
    query.query.bool.filter = filters;
  }

  if (es_index === ES_EVENT_INDEX || es_index === ES_LOCATION_INDEX) {
    const searchResultField = ElasticSearchIndexToSearchResultField[es_index];
    const language = languages[0] ?? DEFAULT_ELASTIC_LANGUAGE;

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

  // Resolve pagination
  query = {
    from,
    size,
    ...query,
  };

  return await request(`${es_index}/_search`, undefined, {
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(query),
  });
}

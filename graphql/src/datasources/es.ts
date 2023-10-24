import { DateTime } from 'luxon';
import { DEFAULT_ELASTIC_LANGUAGE, ElasticLanguage } from '../types';
import { isDefined } from '../utils';

const { RESTDataSource } = require('apollo-datasource-rest');

const ES_ADMINISTRATIVE_DIVISION_INDEX = 'administrative_division' as const;
const ES_HELSINKI_COMMON_ADMINISTRATIVE_DIVISION_INDEX =
  'helsinki_common_administrative_division' as const;
const ES_ONTOLOGY_TREE_INDEX = 'ontology_tree' as const;
const ES_ONTOLOGY_WORD_INDEX = 'ontology_word' as const;
const ES_EVENT_INDEX = 'event' as const;
const ES_LOCATION_INDEX = 'location' as const;
const ES_DEFAULT_INDEX = ES_LOCATION_INDEX;

const ELASTIC_SEARCH_INDICES = [
  ES_ADMINISTRATIVE_DIVISION_INDEX,
  ES_HELSINKI_COMMON_ADMINISTRATIVE_DIVISION_INDEX,
  ES_ONTOLOGY_TREE_INDEX,
  ES_ONTOLOGY_WORD_INDEX,
  ES_EVENT_INDEX,
  ES_LOCATION_INDEX,
] as const;

export type ElasticSearchIndex = typeof ELASTIC_SEARCH_INDICES[number];

const EVENT_SEARCH_RESULT_FIELD = 'event' as const;
const VENUE_SEARCH_RESULT_FIELD = 'venue' as const;

const SEARCH_RESULT_FIELDS = [
  EVENT_SEARCH_RESULT_FIELD,
  VENUE_SEARCH_RESULT_FIELD,
] as const;

type SearchResultField = typeof SEARCH_RESULT_FIELDS[number];

const ElasticSearchIndexToSearchResultField: Record<
  Extract<ElasticSearchIndex, typeof ES_EVENT_INDEX | typeof ES_LOCATION_INDEX>,
  SearchResultField
> = {
  [ES_EVENT_INDEX]: EVENT_SEARCH_RESULT_FIELD,
  [ES_LOCATION_INDEX]: VENUE_SEARCH_RESULT_FIELD,
};

const ELASTIC_SEARCH_URI: string = process.env.ES_URI;
const DEFAULT_TIME_ZONE = 'Europe/Helsinki' as const;
// The default page size when the first argument is not given.
// This is the default page size set by OpenSearch / ElasticSearch
const ES_DEFAULT_PAGE_SIZE = 10 as const;

type OntologyTreeParams = {
  rootId?: string;
  leavesOnly?: boolean;
};

type OntologyWordParams = {
  ids?: string[];
};

type OntologyTreeQuery = {
  size: number;
  query?: {
    bool: OntologyTreeQueryBool;
  };
};

type OntologyTreeQueryBool = {
  filter?: {
    bool: {
      should: [
        {
          term: {
            ancestorIds: string;
          };
        },
        {
          term: {
            _id: string;
          };
        }
      ];
    };
  };
  must_not?: {
    exists: {
      field: 'childIds';
    };
  };
};

type AdministrativeDivisionParams = {
  helsinkiCommonOnly?: boolean;
};

type OrderingDirection = 'ASCENDING' | 'DESCENDING';

export type OrderByDistanceParams = {
  latitude: number;
  longitude: number;
  order: OrderingDirection;
};

export type OrderByNameParams = {
  order: OrderingDirection;
};

type OpenAtFilter = {
  term: {
    'venue.openingHours.openRanges': string;
  };
};

export type AccessibilityProfileType =
  | 'hearing_aid'
  | 'reduced_mobility'
  | 'rollator'
  | 'stroller'
  | 'visually_impaired'
  | 'wheelchair';

type TermField =
  | 'venue.location.administrativeDivisions.id.keyword'
  | 'links.raw_data.ontologytree_ids_enriched.id'
  | 'links.raw_data.ontologyword_ids_enriched.id'
  | 'venue.serviceOwner.providerType.keyword'
  | 'venue.serviceOwner.type.keyword'
  | 'venue.targetGroups.keyword';

type BooleanQueryOccurrenceType = 'filter' | 'must' | 'must_not' | 'should';

type ArrayFilter = {
  bool: {
    [key in BooleanQueryOccurrenceType]?: Array<{
      term: {
        [key: string]: string;
      };
    }>;
  };
};

function buildArrayFilter(
  field: TermField,
  values: string[] = []
): ArrayFilter[] {
  if (values.length === 0) {
    return [];
  }

  return [
    {
      bool: {
        should: values.map((value) => ({
          term: {
            [field]: value,
          },
        })),
      },
    },
  ];
}

type MustHaveReservableResourceFilter = {
  bool: {
    should: [
      {
        term: {
          [key: string]: boolean;
        };
      },
      {
        exists: {
          field: string;
        };
      }
    ];
  };
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

class ElasticSearchAPI extends RESTDataSource {
  constructor() {
    super();
    this.baseURL = ELASTIC_SEARCH_URI;
  }

  async getQueryResults(
    text?: string,
    ontology?: string,
    administrativeDivisionIds?: string[],
    ontologyTreeIdOrSets?: string[][],
    ontologyWordIdOrSets?: string[][],
    providerTypes?: string[],
    serviceOwnerTypes?: string[],
    targetGroups?: string[],
    mustHaveReservableResource?: boolean,
    index?: ElasticSearchIndex,
    from?: number,
    size?: number,
    languages?: ElasticLanguage[],
    openAt?: string,
    orderByDistance?: OrderByDistanceParams,
    orderByName?: OrderByNameParams,
    orderByAccessibilityProfile?: AccessibilityProfileType
  ) {
    const es_index = index || ES_DEFAULT_INDEX;

    // Some fields should be boosted / weighted to get more relevant result set
    const searchFieldsBoostMapping = {
      // Normally weighted search fields for different indexes
      1: (lang: ElasticLanguage, index: ElasticSearchIndex) => {
        return (
          {
            [ES_LOCATION_INDEX]: [`venue.description.${lang}`],
            [ES_EVENT_INDEX]: [
              `event.name.${lang}`,
              `event.description.${lang}`,
            ],
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
    const ontologyFields = (
      lang: ElasticLanguage,
      index: ElasticSearchIndex
    ) => {
      if (index === ES_LOCATION_INDEX) {
        return [
          `links.raw_data.ontologyword_ids_enriched.extra_searchwords_${lang}`,
          `links.raw_data.ontologyword_ids_enriched.ontologyword_${lang}`,
          `links.raw_data.ontologytree_ids_enriched.name_${lang}`,
          `links.raw_data.ontologytree_ids_enriched.extra_searchwords_${lang}`,
        ];
      } else if (index === ES_EVENT_INDEX) {
        return [`ontology.${lang}`, `ontology.alt`];
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
            query_string: {
              query: text,
              boost: boost,
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
    const finalOpenAt = openAtDateTime.isValid
      ? openAtDateTime.toISO()
      : openAt;

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

    if (filters.length) {
      query.query.bool.minimum_should_match = 1;
      query.query.bool.filter = filters;
    }

    if (es_index == ES_EVENT_INDEX || es_index == ES_LOCATION_INDEX) {
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

    return this.post(`${es_index}/_search`, undefined, {
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(query),
    });
  }

  async getSuggestions(
    prefix: string,
    languages: ElasticLanguage[],
    size: number,
    index: ElasticSearchIndex = ES_DEFAULT_INDEX
  ) {
    const query = {
      // Hide all source fields to decrease network load
      _source: '',
      suggest: {
        suggestions: {
          prefix,
          completion: {
            field: 'suggest',
            skip_duplicates: true,
            size,
            contexts: {
              language: languages,
            },
          },
        },
      },
    };

    return this.post(`${index}/_search`, undefined, {
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(query),
    });
  }

  async getAdministrativeDivisions({
    helsinkiCommonOnly,
  }: AdministrativeDivisionParams) {
    const index = helsinkiCommonOnly
      ? ES_HELSINKI_COMMON_ADMINISTRATIVE_DIVISION_INDEX
      : ES_ADMINISTRATIVE_DIVISION_INDEX;
    return this.get(
      `${index}/_search`,
      { size: 10000 },
      {
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }

  async getOntologyTree({ rootId, leavesOnly }: OntologyTreeParams) {
    const bool: OntologyTreeQueryBool = {
      ...(rootId && {
        filter: {
          bool: {
            should: [
              { term: { ancestorIds: rootId } },
              { term: { _id: rootId } },
            ],
          },
        },
      }),
      ...(leavesOnly && {
        must_not: { exists: { field: 'childIds' } },
      }),
    };
    const query: OntologyTreeQuery = {
      size: 10000,
      ...(bool && { query: { bool } }),
    };

    return this.post(
      `${ES_ONTOLOGY_TREE_INDEX}/_search`,
      JSON.stringify(query),
      {
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }

  async getOntologyWords({ ids }: OntologyWordParams) {
    const query = ids
      ? {
          query: {
            terms: {
              _id: ids,
            },
          },
        }
      : {};
    return this.post(
      `${ES_ONTOLOGY_WORD_INDEX}/_search`,
      JSON.stringify({ size: 10000, ...query }),
      {
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }
}

export { ElasticSearchAPI, ES_DEFAULT_PAGE_SIZE };

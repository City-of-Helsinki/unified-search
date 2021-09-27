import { DateTime } from 'luxon';
import { ElasticLanguage } from '../types';

const { RESTDataSource } = require('apollo-datasource-rest');

const ELASTIC_SEARCH_URI: string = process.env.ES_URI;
const ES_ADMINISTRATIVE_DIVISION_INDEX = 'administrative_division';
const ES_ONTOLOGY_TREE_INDEX = 'ontology_tree';
const DEFAULT_TIME_ZONE = 'Europe/Helsinki';

type OntologyTreeParams = {
  rootId?: string;
  leavesOnly?: boolean;
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

export type OrderByDistanceParams = {
  latitude: number;
  longitude: number;
  order: 'ASCENDING' | 'DESCENDING';
};

type OpenAtFilter = {
  term: {
    'venue.openingHours.openRanges': string;
  };
};

type TermField =
  | 'venue.location.administrativeDivisions.id.keyword'
  | 'links.raw_data.ontologytree_ids_enriched.id'
  | 'links.raw_data.ontologyword_ids_enriched.id';

type ArrayFilter = {
  bool: {
    should: Array<{
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

class ElasticSearchAPI extends RESTDataSource {
  constructor() {
    super();
    this.baseURL = ELASTIC_SEARCH_URI;
    this.defaultIndex = 'location';
  }

  async getQueryResults(
    q?: string,
    ontology?: string,
    administrativeDivisionId?: string,
    administrativeDivisionIds?: string[],
    ontologyTreeId?: string,
    ontologyTreeIds?: string[],
    ontologyWordIds?: string[],
    index?: string,
    from?: number,
    size?: number,
    languages?: ElasticLanguage[],
    openAt?: string,
    orderByDistance?: OrderByDistanceParams
  ) {
    const es_index = index ? index : this.defaultIndex;

    const searchFields = (lang: string, index: string) => {
      if (index === 'location') {
        return [
          `venue.name.${lang}`,
          `venue.description.${lang}`,
          `links.raw_data.short_desc_${lang}`,
        ];
      } else if (index === 'event') {
        return [`event.name.${lang}`, `event.description.${lang}`];
      }
      return [];
    };

    const ontologyFields = (lang: string, index: string) => {
      if (index === 'location') {
        return [
          `links.raw_data.ontologyword_ids_enriched.extra_searchwords_${lang}`,
          `links.raw_data.ontologyword_ids_enriched.ontologyword_${lang}`,
          `links.raw_data.ontologytree_ids_enriched.name_${lang}`,
          `links.raw_data.ontologytree_ids_enriched.extra_searchwords_${lang}`,
        ];
      } else if (index === 'event') {
        return [`ontology.${lang}`, `ontology.alt`];
      }
      return [];
    };

    const defaultQuery = languages.reduce(
      (acc, language) => ({
        ...acc,
        [language]: {
          query_string: {
            query: q,
            fields: searchFields(language, index),
          },
        },
      }),
      {}
    );

    // Resolve query
    let query: any = {
      query: {
        bool: {
          should: Object.values(defaultQuery),
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

    let divisionIds = administrativeDivisionIds ?? [];
    if (administrativeDivisionId) {
      divisionIds.push(administrativeDivisionId);
    }
    let ontologyIds = ontologyTreeIds ?? [];
    if (ontologyTreeId) {
      ontologyIds.push(ontologyTreeId);
    }

    // Assume time zone DEFAULT_TIME_ZONE when there is no time zone offset provided by the client.
    const openAtDateTime = DateTime.fromISO(openAt, {
      zone: DEFAULT_TIME_ZONE,
    });
    const finalOpenAt = openAtDateTime.isValid
      ? openAtDateTime.toISO()
      : openAt;

    const filters: Array<ArrayFilter | OpenAtFilter> = [
      ...buildArrayFilter(
        'venue.location.administrativeDivisions.id.keyword',
        divisionIds
      ),
      ...buildArrayFilter(
        'links.raw_data.ontologytree_ids_enriched.id',
        ontologyIds
      ),
      ...buildArrayFilter(
        'links.raw_data.ontologyword_ids_enriched.id',
        ontologyWordIds
      ),
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

    if (typeof orderByDistance !== 'undefined') {
      query.sort = {
        _geo_distance: {
          location: [orderByDistance.latitude, orderByDistance.longitude],
          order: orderByDistance.order === 'DESCENDING' ? 'desc' : 'asc',
          ignore_unmapped: true,
        },
      };
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
    index: string = this.defaultIndex,
    size: number
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

  async getAdministrativeDivisions() {
    return this.get(
      `${ES_ADMINISTRATIVE_DIVISION_INDEX}/_search`,
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

  async getMapping(q) {
    const data = await this.get(`test-index/_mapping`);
    return data;
  }
}

export { ElasticSearchAPI };

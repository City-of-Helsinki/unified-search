import {
  type ELASTIC_SEARCH_INDICES,
  type SEARCH_RESULT_FIELDS,
} from './constants';

export type ElasticSearchIndex = (typeof ELASTIC_SEARCH_INDICES)[number];

export type SearchResultField = (typeof SEARCH_RESULT_FIELDS)[number];

export interface OntologyTreeParams {
  rootId?: string;
  leavesOnly?: boolean;
}

export interface OntologyWordParams {
  ids?: string[];
}

export interface OntologyTreeQuery {
  size: number;
  query?: {
    bool: OntologyTreeQueryBool;
  };
}

export interface OntologyTreeQueryBool {
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
        },
      ];
    };
  };
  must_not?: {
    exists: {
      field: 'childIds';
    };
  };
}

export interface AdministrativeDivisionParams {
  helsinkiCommonOnly?: boolean;
}

export type OrderingDirection = 'ASCENDING' | 'DESCENDING';

export interface OrderByDistanceParams {
  latitude: number;
  longitude: number;
  order: OrderingDirection;
}

export interface OrderByNameParams {
  order: OrderingDirection;
}

export interface OpenAtFilter {
  term: {
    'venue.openingHours.openRanges': string;
  };
}

export type AccessibilityProfileType =
  | 'hearing_aid'
  | 'reduced_mobility'
  | 'rollator'
  | 'stroller'
  | 'visually_impaired'
  | 'wheelchair';

export type TermField =
  | 'venue.location.administrativeDivisions.id.keyword'
  | 'links.raw_data.ontologytree_ids_enriched.id'
  | 'links.raw_data.ontologyword_ids_enriched.id'
  | 'venue.serviceOwner.providerType.keyword'
  | 'venue.serviceOwner.type.keyword'
  | 'venue.targetGroups.keyword';

export type BooleanQueryOccurrenceType =
  | 'filter'
  | 'must'
  | 'must_not'
  | 'should';

export interface ArrayFilter {
  bool: {
    [key in BooleanQueryOccurrenceType]?: Array<{
      term: Record<string, string>;
    }>;
  };
}

export interface MustHaveReservableResourceFilter {
  bool: {
    should: [
      {
        term: Record<string, boolean>;
      },
      {
        exists: {
          field: string;
        };
      },
    ];
  };
}

import {
  type ELASTIC_SEARCH_INDICES,
  type SEARCH_RESULT_FIELDS,
} from './constants';

export type ElasticSearchIndex = (typeof ELASTIC_SEARCH_INDICES)[number];

export type SearchResultField = (typeof SEARCH_RESULT_FIELDS)[number];

export type OntologyTreeParams = {
  rootId?: string;
  leavesOnly?: boolean;
};

export type OntologyWordParams = {
  ids?: string[];
};

export type OntologyTreeQuery = {
  size: number;
  query?: {
    bool: OntologyTreeQueryBool;
  };
};

export type OntologyTreeQueryBool = {
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
};

export type AdministrativeDivisionParams = {
  helsinkiCommonOnly?: boolean;
};

export type OrderingDirection = 'ASCENDING' | 'DESCENDING';

export type OrderByDistanceParams = {
  latitude: number;
  longitude: number;
  order: OrderingDirection;
};

export type OrderByNameParams = {
  order: OrderingDirection;
};

export type OpenAtFilter = {
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

export type ArrayFilter = {
  bool: {
    [key in BooleanQueryOccurrenceType]?: Array<{
      term: Record<string, string>;
    }>;
  };
};

export type MustHaveReservableResourceFilter = {
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
};

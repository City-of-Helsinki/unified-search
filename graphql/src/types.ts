import type { estypes } from '@elastic/elasticsearch';

import type { GraphQlToElasticLanguageMap } from './constants.js';

// A type representing an object with no properties
export type EmptyObject = Record<never, never>;

export type ConnectionCursor = string;

export type ConnectionCursorObject = {
  offset: number;
};

export type ConnectionArguments = {
  after?: ConnectionCursor | null;
  first?: number | null;
};

export type ElasticSearchPagination = {
  from?: number;
  size?: number;
};

export type ElasticLanguage =
  (typeof GraphQlToElasticLanguageMap)[keyof typeof GraphQlToElasticLanguageMap];

export type SearchableFields = 'venue.name' | 'venue.description';

export type TranslatableField<T extends string = SearchableFields> =
  `${T}.${ElasticLanguage}`;

// FIXME: Generate this from GraphQL type UnifiedSearchVenue
//
// This type is mostly unspecified, simply made to have some
// kind of a structure for the data that's being handled.
// By generating this from the GraphQL type, this could be
// more strictly typed.
export type Venue = {
  accessibility?: {
    shortcomings: Array<{ profile: string; count?: number }>;
  };
  description?: unknown;
  images?: unknown;
  location?: unknown;
  meta?: unknown;
  name?: unknown;
  ontologyWords?: unknown;
  openingHours?: unknown;
  reservation?: unknown;
  serviceOwner?: unknown;
  targetGroups?: unknown;
  isCultureAndLeisureDivisionVenue?: boolean;
  eventCount?: number;
};

export type VenueProps = {
  venue: Venue;
};

// FIXME: Combine TypeScript types and GraphQL types
export type EsHitSource = {
  name?: unknown;
  venue?: Venue;
};

// FIXME: Combine TypeScript types and GraphQL types
export type EsResults = estypes.SearchResponse<
  EsHitSource,
  Record<string, estypes.AggregationsAggregate>
>;

export type Edge = {
  cursor: string;
  node: Record<string, unknown>;
};

export type GetCursor = (index: number) => string;

export type LongitudeLatitude = [longitude: number, latitude: number];

export type PageInfoProps = {
  edges: Edge[];
  hits: number;
  connectionArguments: ConnectionArguments;
};

export type GeoJSONPointInput = {
  geometry?: {
    coordinates?: {
      longitude?: number;
      latitude?: number;
    };
  };
  longitude?: number;
  latitude?: number;
};

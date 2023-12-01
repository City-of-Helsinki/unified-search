import { type GraphQlToElasticLanguageMap } from './constants';

export type ConnectionCursor = string;

export type ConnectionCursorObject = {
  offset: number;
};

export type PageInfo = {
  startCursor: ConnectionCursor | null;
  endCursor: ConnectionCursor | null;
  hasPreviousPage: boolean;
  hasNextPage: boolean;
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

export const DEFAULT_ELASTIC_LANGUAGE: ElasticLanguage = 'fi';

export type SearchableFields =
  | 'venue.name'
  | 'venue.description'
  | 'event.name'
  | 'event.description';

export type TranslatableField<T extends string = SearchableFields> =
  `${T}.${ElasticLanguage}`;

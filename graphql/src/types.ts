import { type GraphQlToElasticLanguageMap } from './constants';

export type ConnectionCursor = string;

export interface ConnectionCursorObject {
  offset: number;
}

export interface PageInfo {
  startCursor: ConnectionCursor | null;
  endCursor: ConnectionCursor | null;
  hasPreviousPage: boolean;
  hasNextPage: boolean;
}

export interface ConnectionArguments {
  after?: ConnectionCursor | null;
  first?: number | null;
}

export interface ElasticSearchPagination {
  from?: number;
  size?: number;
}

export type ElasticLanguage =
  (typeof GraphQlToElasticLanguageMap)[keyof typeof GraphQlToElasticLanguageMap];

export const DEFAULT_ELASTIC_LANGUAGE: ElasticLanguage = 'fi';

import type { ElasticLanguage, TranslatableField } from '../../../../types';
import type {
  AccessibilityProfileType,
  ElasticSearchIndex,
  OrderByDistanceParams,
  OrderByNameParams,
} from '../../types';

export type OrderByFields = {
  orderByDistance?: OrderByDistanceParams;
  orderByName?: OrderByNameParams;
  orderByAccessibilityProfile?: AccessibilityProfileType;
};

export type GetQueryResultsProps = {
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
} & OrderByFields;

export type QueryResultFilterProps = Pick<
  GetQueryResultsProps,
  | 'administrativeDivisionIds'
  | 'ontologyTreeIdOrSets'
  | 'ontologyWordIdOrSets'
  | 'providerTypes'
  | 'serviceOwnerTypes'
  | 'targetGroups'
  | 'mustHaveReservableResource'
  | 'openAt'
>;

export type QueryFilterClauses = {
  [key in TranslatableField]?: {
    query: string;
  } & Partial<{
    boost?: number | string;
    type?: string;
    operator?: string;
    fuzziness?: string;
  }>;
};

import type { ElasticLanguage } from '../../../../types';
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
} & OrderByFields;

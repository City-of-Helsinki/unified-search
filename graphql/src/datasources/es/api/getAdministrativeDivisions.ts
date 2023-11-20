import { type ElasticSearchAPI } from '..';
import {
  ES_ADMINISTRATIVE_DIVISION_INDEX,
  ES_HELSINKI_COMMON_ADMINISTRATIVE_DIVISION_INDEX,
} from '../constants';
import type { AdministrativeDivisionParams } from '../types';

export default async function getAdministrativeDivisions(
  request: ElasticSearchAPI['get'],
  { helsinkiCommonOnly }: AdministrativeDivisionParams
) {
  const index = helsinkiCommonOnly
    ? ES_HELSINKI_COMMON_ADMINISTRATIVE_DIVISION_INDEX
    : ES_ADMINISTRATIVE_DIVISION_INDEX;
  return await request(
    `${index}/_search`,
    { size: 10000 },
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );
}

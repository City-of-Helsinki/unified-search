import {
  ES_ADMINISTRATIVE_DIVISION_INDEX,
  ES_HELSINKI_COMMON_ADMINISTRATIVE_DIVISION_INDEX,
} from '../constants.js';
import { type ElasticSearchAPI } from '../index.js';
import type { AdministrativeDivisionParams } from '../types.js';

export default async function getAdministrativeDivisions(
  request: ElasticSearchAPI['get'],
  { helsinkiCommonOnly }: AdministrativeDivisionParams
) {
  const index = helsinkiCommonOnly
    ? ES_HELSINKI_COMMON_ADMINISTRATIVE_DIVISION_INDEX
    : ES_ADMINISTRATIVE_DIVISION_INDEX;
  return await request(`${index}/_search`, {
    params: { size: '10000' },
    headers: { 'Content-Type': 'application/json' },
  });
}

import type { Client } from '@elastic/elasticsearch';

import type { EsHitSource } from '../../../types.js';
import {
  ES_ADMINISTRATIVE_DIVISION_INDEX,
  ES_HELSINKI_COMMON_ADMINISTRATIVE_DIVISION_INDEX,
} from '../constants.js';
import type { AdministrativeDivisionParams } from '../types.js';

export default async function getAdministrativeDivisions(
  esClient: Client,
  { helsinkiCommonOnly }: AdministrativeDivisionParams
) {
  const index = helsinkiCommonOnly
    ? ES_HELSINKI_COMMON_ADMINISTRATIVE_DIVISION_INDEX
    : ES_ADMINISTRATIVE_DIVISION_INDEX;

  return await esClient.search<EsHitSource>({
    index,
    size: 10000,
  });
}

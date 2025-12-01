import type { Client } from '@elastic/elasticsearch';

import { ES_ONTOLOGY_WORD_INDEX } from '../constants.js';
import type { OntologyWordParams } from '../types.js';
import { makeOntologyWordsQuery } from './getQueryResults/utils/makeOntologyWordsQuery.js';
import type { EsHitSource } from '../../../types.js';

export default async function getOntologyWords(
  esClient: Client,
  ontologyWordParams: OntologyWordParams
) {
  const query = makeOntologyWordsQuery(ontologyWordParams);

  return await esClient.search<EsHitSource>({
    index: ES_ONTOLOGY_WORD_INDEX,
    size: 10000,
    ...query,
  });
}

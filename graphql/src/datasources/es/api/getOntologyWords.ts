import { ES_ONTOLOGY_WORD_INDEX } from '../constants.js';
import { type ElasticSearchAPI } from '../index.js';
import type { OntologyWordParams } from '../types.js';
import { makeOntologyWordsQuery } from './getQueryResults/utils/makeOntologyWordsQuery.js';

export default async function getOntologyWords(
  request: ElasticSearchAPI['post'],
  ontologyWordParams: OntologyWordParams
) {
  const query = makeOntologyWordsQuery(ontologyWordParams);

  return await request(`${ES_ONTOLOGY_WORD_INDEX}/_search`, {
    body: JSON.stringify({ size: 10000, ...query }),
    headers: { 'Content-Type': 'application/json' },
  });
}

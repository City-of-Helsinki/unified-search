import { type ElasticSearchAPI } from '..';
import { ES_ONTOLOGY_WORD_INDEX } from '../constants';
import type { OntologyWordParams } from '../types';

export default async function getOntologyWords(
  request: ElasticSearchAPI['post'],
  { ids }: OntologyWordParams
) {
  const query = ids
    ? {
        query: {
          terms: {
            _id: ids,
          },
        },
      }
    : {};
  return await request(
    `${ES_ONTOLOGY_WORD_INDEX}/_search`,
    JSON.stringify({ size: 10000, ...query }),
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );
}

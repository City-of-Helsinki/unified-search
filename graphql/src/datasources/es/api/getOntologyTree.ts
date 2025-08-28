import { ES_ONTOLOGY_TREE_INDEX } from '../constants.js';
import { type ElasticSearchAPI } from '../index.js';
import type { OntologyTreeParams } from '../types.js';
import { makeOntologyTreeQuery } from './getQueryResults/utils/makeOntologyTreeQuery.js';

export default async function getOntologyTree(
  request: ElasticSearchAPI['post'],
  ontologyTreeParams: OntologyTreeParams
) {
  const query = makeOntologyTreeQuery(ontologyTreeParams);

  return await request(`${ES_ONTOLOGY_TREE_INDEX}/_search`, {
    body: JSON.stringify(query),
    headers: { 'Content-Type': 'application/json' },
  });
}

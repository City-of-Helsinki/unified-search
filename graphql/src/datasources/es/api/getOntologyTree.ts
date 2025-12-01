import type { Client } from '@elastic/elasticsearch';

import { ES_ONTOLOGY_TREE_INDEX } from '../constants.js';
import type { OntologyTreeParams } from '../types.js';
import { makeOntologyTreeQuery } from './getQueryResults/utils/makeOntologyTreeQuery.js';
import type { EsHitSource } from '../../../types.js';

export default async function getOntologyTree(
  esClient: Client,
  ontologyTreeParams: OntologyTreeParams
) {
  const query = makeOntologyTreeQuery(ontologyTreeParams);

  return await esClient.search<EsHitSource>({
    index: ES_ONTOLOGY_TREE_INDEX,
    ...query,
  });
}

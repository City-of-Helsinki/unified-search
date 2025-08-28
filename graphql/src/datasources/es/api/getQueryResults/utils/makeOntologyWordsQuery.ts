import type { OntologyWordParams, OntologyWordsQuery } from '../../../types.js';

export function makeOntologyWordsQuery({
  ids,
}: OntologyWordParams): OntologyWordsQuery {
  return ids
    ? {
        query: {
          terms: {
            _id: ids,
          },
        },
      }
    : {};
}

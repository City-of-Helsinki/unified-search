import type { PageInfoProps } from '../types.js';
import { pageInfoResolver } from './pageInfoResolver.js';

export function getSearchResultConnectionResolvers() {
  return {
    count({ hits }: PageInfoProps) {
      return hits;
    },
    max_score({ es_results }: unknown) {
      return es_results[0].hits.max_score;
    },
    async pageInfo({ edges, hits, connectionArguments }: PageInfoProps) {
      return await pageInfoResolver(edges, hits, connectionArguments);
    },
    edges({ edges }: PageInfoProps) {
      return edges;
    },
    es_results({ es_results }: unknown) {
      return es_results;
    },
  };
}

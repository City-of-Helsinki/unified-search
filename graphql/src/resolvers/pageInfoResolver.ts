import { ES_DEFAULT_PAGE_SIZE } from '../datasources/es/index.js';
import {
  type ConnectionArguments,
  type ConnectionCursorObject,
} from '../types.js';
import { readCursor } from '../utils.js';

export type Edge = {
  cursor: string;
  node: Record<string, unknown>;
};

export async function pageInfoResolver(
  edges: Edge[],
  totalHits: number,
  connectionArguments: ConnectionArguments
) {
  if (edges.length === 0) {
    return {
      hasNextPage: false,
      hasPreviousPage: false,
      startCursor: null,
      endCursor: null,
    };
  }

  const [firstEdge] = edges;
  const [lastEdge] = edges.slice(-1);
  const pageStart =
    readCursor<ConnectionCursorObject | null>(connectionArguments.after)
      ?.offset ?? 0;
  const pageLength = connectionArguments.first ?? ES_DEFAULT_PAGE_SIZE;

  return {
    hasNextPage: pageStart + pageLength < totalHits,
    hasPreviousPage: pageStart > 0 && totalHits > 0,
    startCursor: firstEdge?.cursor,
    endCursor: lastEdge?.cursor,
  };
}

export default pageInfoResolver;

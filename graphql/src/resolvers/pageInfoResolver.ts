import { ES_DEFAULT_PAGE_SIZE } from '../datasources/es';
import { SupportedConnectionArguments, ConnectionCursorObject } from '../types';
import { readCursor } from '../utils';

type Edge = {
  cursor: string;
  node: Record<string, unknown>;
};

export async function pageInfoResolver(
  edges: Edge[],
  totalHits: number,
  connectionArguments: SupportedConnectionArguments
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
  // TODO: pageLength could support the last -argument, but it's an excluded in SupportedConnectionArguments.
  const pageLength = connectionArguments.first ?? ES_DEFAULT_PAGE_SIZE;

  return {
    hasNextPage: pageStart + pageLength < totalHits,
    hasPreviousPage: pageStart > 0 && totalHits > 0,
    startCursor: firstEdge?.cursor,
    endCursor: lastEdge?.cursor,
  };
}

export default pageInfoResolver;

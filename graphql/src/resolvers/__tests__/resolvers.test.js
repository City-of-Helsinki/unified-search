import { createCursor } from '../../utils.ts';
import { pageInfoResolver } from '../pageInfoResolver.ts';

function makeEdge(cursor = {}) {
  return {
    cursor: createCursor(cursor),
    node: {},
  };
}

async function getFirstPage() {
  const edges = [makeEdge(), makeEdge(), makeEdge()];

  return pageInfoResolver(edges, 3, {
    after: null,
    first: 1,
  });
}

async function getMiddlePage() {
  const edges = [makeEdge(), makeEdge(), makeEdge()];

  return pageInfoResolver(edges, 3, {
    after: createCursor({
      offset: 1,
    }),
    first: 1,
  });
}

async function getLastPage() {
  const edges = [makeEdge(), makeEdge(), makeEdge()];

  return pageInfoResolver(edges, 3, {
    after: createCursor({
      offset: 2,
    }),
    first: 1,
  });
}

describe('resolvers', () => {
  describe('pageInfoResolver', () => {
    it('should return falsy for empty results', async () => {
      expect(await pageInfoResolver([], 0, {})).toEqual({
        hasNextPage: false,
        hasPreviousPage: false,
        startCursor: null,
        endCursor: null,
      });
    });

    describe('hasNextPage', () => {
      it('should have a next page on the first page', async () => {
        const pageInfo = await getFirstPage();

        expect(pageInfo.hasNextPage).toEqual(true);
      });

      it('should have a next page in the middle of pages', async () => {
        const pageInfo = await getMiddlePage();

        expect(pageInfo.hasNextPage).toEqual(true);
      });

      it('should not have a next page on the last page', async () => {
        const pageInfo = await getLastPage();

        expect(pageInfo.hasNextPage).toEqual(false);
      });
    });

    describe('hasPreviousPage', () => {
      it('should not have a previous page on the first page', async () => {
        const pageInfo = await getFirstPage();

        expect(pageInfo.hasPreviousPage).toEqual(false);
      });

      it('should have a previous page in the middle of pages', async () => {
        const pageInfo = await getMiddlePage();

        expect(pageInfo.hasPreviousPage).toEqual(true);
      });

      it('should have a previous page on the last page', async () => {
        const pageInfo = await getLastPage();

        expect(pageInfo.hasPreviousPage).toEqual(true);
      });
    });
  });
});

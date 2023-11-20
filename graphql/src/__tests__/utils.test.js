import {
  getEsOffsetPaginationQuery,
  createCursor,
  escapeQuery,
} from '../utils';

describe('utils', () => {
  describe('getEsOffsetPaginationQuery', () => {
    it('should error when before is provided', () => {
      expect(() => getEsOffsetPaginationQuery({ before: {} })).toThrowError();
    });

    it('should error when last', () => {
      expect(() => getEsOffsetPaginationQuery({ last: 10 })).toThrowError();
    });

    it('should error when first is not a positive number', () => {
      expect(() =>
        getEsOffsetPaginationQuery({ first: 'first' })
      ).toThrowError();
      expect(() => getEsOffsetPaginationQuery({ first: -1 })).toThrowError();
    });

    describe('when after', () => {
      it('should return an offset that points to results after the cursor', () => {
        expect(
          getEsOffsetPaginationQuery({
            after: createCursor({
              offset: 5,
              meta: {},
            }),
          })
        ).toEqual({
          from: 5,
        });
      });

      describe('with first', () => {
        it('should only provide the first n elements', () => {
          expect(
            getEsOffsetPaginationQuery({
              first: 5,
              after: createCursor({
                offset: 5,
              }),
            })
          ).toEqual({
            from: 5,
            size: 5,
          });
        });
      });
    });
  });

  describe('escapeQuery', () => {
    it("should escape Elastic Search's special characters", () => {
      expect(
        escapeQuery('+ - = && || > < ! ( ) { } [ ] ^ " ~ * ? : \\ /')
      ).toEqual(
        '\\+ \\- \\= \\&& \\|| \\> \\< \\! \\( \\) \\{ \\} \\[ \\] \\^ \\" \\~ \\* \\? \\: \\\\ \\/'
      );
    });

    it("should not escape other than Elastic Search's special characters", () => {
      expect(
        escapeQuery(
          'Test / Another + read-only: "More <text> & Ääni, öylätti, Åland"'
        )
      ).toEqual(
        'Test \\/ Another \\+ read\\-only\\: \\"More \\<text\\> & Ääni, öylätti, Åland\\"'
      );
    });
  });
});

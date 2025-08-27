import { describe, expect, it } from 'vitest';

import { MATCH_PHRASE_BOOST_MULTIPLIER, SEARCH_WEIGHT } from '../constants.js';

describe('SEARCH_WEIGHT', () => {
  it('only normal, high and veryHigh are defined', () => {
    expect(SEARCH_WEIGHT).toHaveProperty('normal');
    expect(SEARCH_WEIGHT).toHaveProperty('high');
    expect(SEARCH_WEIGHT).toHaveProperty('veryHigh');
    expect(Object.keys(SEARCH_WEIGHT)).toHaveLength(3); // No more than the above
  });

  it('weights must be ordered', () => {
    expect(SEARCH_WEIGHT.normal).toBeLessThan(SEARCH_WEIGHT.high);
    expect(SEARCH_WEIGHT.high).toBeLessThan(SEARCH_WEIGHT.veryHigh);
  });

  it('smallest value must be at least 1', () => {
    expect(SEARCH_WEIGHT.normal).toBeGreaterThanOrEqual(1);
  });

  /**
   * Make sure ratio of consecutive weights is large enough to have a meaningful
   * effect on search results. The lower limit is semi-arbitrarily chosen, so
   * change as need be.
   */
  it.each([1.1])(
    'ratio of consecutive weights must be at least %j',
    (expectedMinimumRatio) => {
      expect(SEARCH_WEIGHT.high / SEARCH_WEIGHT.normal).toBeGreaterThan(
        expectedMinimumRatio
      );
      expect(SEARCH_WEIGHT.veryHigh / SEARCH_WEIGHT.high).toBeGreaterThan(
        expectedMinimumRatio
      );
    }
  );
});

describe('MATCH_PHRASE_BOOST_MULTIPLIER', () => {
  it('must be at least 1', () => {
    expect(MATCH_PHRASE_BOOST_MULTIPLIER).toBeGreaterThan(1);
  });
});

import type { ElasticLanguage, TranslatableField } from '../../../../types.js';
import { ES_LOCATION_INDEX } from '../../constants.js';
import type { ElasticSearchIndex } from '../../types.js';

/**
 * Semi-arbitrarily chosen weights for scaling search results.
 *
 * `normal`: Normal weight is the baseline i.e. no boost nor reduction.
 * `high`: High weight is double the normal weight.
 * `veryHigh`: Very high weight is triple the normal weight.
 *
 * Higher the weight, more the importance of the field in search results.
 *
 * The scale can be changed, the current invariants are that
 * normal < high < veryHigh (i.e. they are ordered)
 * and that they're different enough to have an effect on the search result
 * (otherwise they would be meaningless).
 */
export const SEARCH_WEIGHT = {
  normal: 1,
  high: 2,
  veryHigh: 3,
} as const;

// Some fields should be boosted / weighted to get more relevant result set
export const searchFieldsBoostMapping: Record<
  string | number,
  (lang: ElasticLanguage, index: ElasticSearchIndex) => TranslatableField[]
> = {
  // Normally weighted search fields for different indexes
  [SEARCH_WEIGHT.normal]: (
    lang: ElasticLanguage,
    index: ElasticSearchIndex
  ) => {
    return (
      {
        [ES_LOCATION_INDEX]: [`venue.description.${lang}`],
      }[index] ?? []
    );
  },
  [SEARCH_WEIGHT.veryHigh]: (
    lang: ElasticLanguage,
    index: ElasticSearchIndex
  ) => {
    return (
      {
        [ES_LOCATION_INDEX]: [`venue.name.${lang}`],
      }[index] ?? []
    );
  },
};

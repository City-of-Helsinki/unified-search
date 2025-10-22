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
 *
 * The values could be changed to non-integers if more granularity is needed,
 * but please check tests and functionality if you do that, as handling
 * floating point values has its pitfalls. As a recommendation, keep to
 * exactly representable floating point numbers i.e. fractions that are sums of
 * powers of two, e.g. 1.5=2^0+2^-1 or 2.125=2^1+2^-3, to avoid precision issues.
 */
export const SEARCH_WEIGHT = {
  normal: 1,
  high: 2,
  veryHigh: 3,
} as const;

export type SearchWeight = (typeof SEARCH_WEIGHT)[keyof typeof SEARCH_WEIGHT];
export type StringSearchWeight = `${SearchWeight}`;

/**
 * Boost multiplier for `match_phrase` queries.
 *
 * Meant to make sure that exact phrase matches are ranked higher than
 * regular matches.
 *
 * For example, if a user searches for "art museum" we want to make sure
 * that results containing the exact phrase "art museum" are ranked higher
 * than those that just contain the words "art" and "museum" separately.
 *
 * Must be greater than 1 to have an effect.
 */
export const MATCH_PHRASE_BOOST_MULTIPLIER = SEARCH_WEIGHT.high;

export type SearchFieldMappingFunction = (
  lang: ElasticLanguage,
  index: ElasticSearchIndex
) => TranslatableField[];

export type SearchFieldsBoostMapping = Partial<
  // Javascript converts number object keys to strings, so let's use string keys
  Record<StringSearchWeight, SearchFieldMappingFunction>
>;

// Some fields should be boosted / weighted to get more relevant result set
export const searchFieldsBoostMapping: SearchFieldsBoostMapping = {
  [SEARCH_WEIGHT.normal]: (lang, index) =>
    index === ES_LOCATION_INDEX ? [`venue.description.${lang}`] : [],
  [SEARCH_WEIGHT.veryHigh]: (lang, index) =>
    index === ES_LOCATION_INDEX ? [`venue.name.${lang}`] : [],
};

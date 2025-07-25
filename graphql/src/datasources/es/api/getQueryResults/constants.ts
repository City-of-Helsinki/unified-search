import type { ElasticLanguage, TranslatableField } from '../../../../types.js';
import { ES_LOCATION_INDEX } from '../../constants.js';
import type { ElasticSearchIndex } from '../../types.js';

// Some fields should be boosted / weighted to get more relevant result set
export const searchFieldsBoostMapping: Record<
  string | number,
  (lang: ElasticLanguage, index: ElasticSearchIndex) => TranslatableField[]
> = {
  // Normally weighted search fields for different indexes
  1: (lang: ElasticLanguage, index: ElasticSearchIndex) => {
    return (
      {
        [ES_LOCATION_INDEX]: [`venue.description.${lang}`],
      }[index] ?? []
    );
  },
  3: (lang: ElasticLanguage, index: ElasticSearchIndex) => {
    return (
      {
        [ES_LOCATION_INDEX]: [`venue.name.${lang}`],
      }[index] ?? []
    );
  },
};

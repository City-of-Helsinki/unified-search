import type { ElasticLanguage } from '../../../../types';
import { ES_EVENT_INDEX, ES_LOCATION_INDEX } from '../../constants';
import type { ElasticSearchIndex } from '../../types';

// Some fields should be boosted / weighted to get more relevant result set
export const searchFieldsBoostMapping = {
  // Normally weighted search fields for different indexes
  1: (lang: ElasticLanguage, index: ElasticSearchIndex) => {
    return (
      {
        [ES_LOCATION_INDEX]: [`venue.description.${lang}`],
        [ES_EVENT_INDEX]: [`event.name.${lang}`, `event.description.${lang}`],
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

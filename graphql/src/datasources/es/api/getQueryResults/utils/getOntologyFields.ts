import type { ElasticLanguage } from '../../../../../types';
import { ES_EVENT_INDEX, ES_LOCATION_INDEX } from '../../../constants';
import type { ElasticSearchIndex } from '../../../types';

// Ontology fields for different indexes
export function getOntologyFields(
  lang: ElasticLanguage,
  index: ElasticSearchIndex
) {
  if (index === ES_LOCATION_INDEX) {
    return [
      `links.raw_data.ontologyword_ids_enriched.extra_searchwords_${lang}`,
      `links.raw_data.ontologyword_ids_enriched.ontologyword_${lang}`,
      `links.raw_data.ontologytree_ids_enriched.name_${lang}`,
      `links.raw_data.ontologytree_ids_enriched.extra_searchwords_${lang}`,
    ];
  } else if (index === ES_EVENT_INDEX) {
    return [`ontology.${lang}`, 'ontology.alt'];
  }
  return [];
}

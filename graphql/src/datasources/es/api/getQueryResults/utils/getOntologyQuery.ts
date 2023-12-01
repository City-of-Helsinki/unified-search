import { GraphQlToElasticLanguageMap } from '../../../../../constants';
import { ES_DEFAULT_INDEX } from '../../../constants';
import type { GetQueryResultsProps } from '../types';
import { getOntologyFields } from './getOntologyFields';

/** @deprecated Deprecated as unused. */
export function getOntologyQuery({
  index = ES_DEFAULT_INDEX,
  languages = Object.values(GraphQlToElasticLanguageMap),
  ontology,
}: Pick<GetQueryResultsProps, 'index' | 'languages' | 'ontology'>) {
  const ontologyMatchers = languages.reduce(
    (acc, language) => ({
      ...acc,
      [language]: {
        multi_match: {
          query: ontology,
          fields: getOntologyFields(language, index),
        },
      },
    }),
    {}
  );

  return {
    query: {
      bool: {
        should: [
          ...Object.values(
            languages.map((language) => ({
              bool: { must: [ontologyMatchers[language]] },
            }))
          ).flat(),
        ],
      },
    },
  };
}

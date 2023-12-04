import { GraphQlToElasticLanguageMap } from '../../../../../constants';
import { type ElasticLanguage } from '../../../../../types';
import { ES_DEFAULT_INDEX } from '../../../constants';
import type { GetQueryResultsProps } from '../types';
import { getOntologyFields } from './getOntologyFields';

export const getOntologyMatchers = ({
  index = ES_DEFAULT_INDEX,
  languages = Object.values(GraphQlToElasticLanguageMap),
  query,
}: Pick<GetQueryResultsProps, 'index' | 'languages'> & { query: string }) =>
  languages.reduce<{
    [key in ElasticLanguage]?: {
      multi_match: {
        query: string;
        fields: ReturnType<typeof getOntologyFields>;
      };
    };
  }>(
    (acc, language) => ({
      ...acc,
      [language]: {
        multi_match: {
          query,
          fields: getOntologyFields(language, index),
        },
      },
    }),
    {}
  );

/** @deprecated Deprecated as unused. */
export function getOntologyQuery({
  index = ES_DEFAULT_INDEX,
  languages = Object.values(GraphQlToElasticLanguageMap),
  ontology,
}: Pick<GetQueryResultsProps, 'index' | 'languages' | 'ontology'>) {
  const ontologyMatchers = getOntologyMatchers({
    index,
    languages,
    query: ontology,
  });

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

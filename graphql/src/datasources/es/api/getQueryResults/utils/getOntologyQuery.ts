import { GraphQlToElasticLanguageMap } from '../../../../../constants.js';
import { type ElasticLanguage } from '../../../../../types.js';
import { ES_DEFAULT_INDEX } from '../../../constants.js';
import type { GetQueryResultsProps } from '../types.js';
import { getOntologyFields } from './getOntologyFields.js';

type OntologyMatchers = {
  [key in ElasticLanguage]?: {
    multi_match: {
      query: string;
      fields: ReturnType<typeof getOntologyFields>;
    };
  };
};

export function getOntologyMatchers({
  index = ES_DEFAULT_INDEX,
  languages = Object.values(GraphQlToElasticLanguageMap),
  query,
}: Pick<GetQueryResultsProps, 'index' | 'languages'> & { query: string }) {
  const matchers: OntologyMatchers = {};

  for (const language of languages) {
    matchers[language] = {
      multi_match: {
        query,
        fields: getOntologyFields(language, index),
      },
    };
  }

  return matchers;
}

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

  const shouldClauses = languages.map((language) => ({
    bool: {
      must: [ontologyMatchers[language]],
    },
  }));

  return {
    query: {
      bool: {
        should: shouldClauses,
      },
    },
  };
}

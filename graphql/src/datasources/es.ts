import { ElasticLanguage } from '../types';

const { RESTDataSource } = require('apollo-datasource-rest');

const ELASTIC_SEARCH_URI: string = process.env.ES_URI;

class ElasticSearchAPI extends RESTDataSource {
  constructor() {
    super();
    this.baseURL = ELASTIC_SEARCH_URI;
    this.defaultIndex = 'location';
  }

  async getQueryResults(
    q?: string,
    ontology?: string,
    administrativeDivision?: string,
    index?: string,
    from?: number,
    size?: number,
    languages?: ElasticLanguage[]
  ) {
    const es_index = index ? index : this.defaultIndex;

    const searchFields = (lang: string, index: string) => {
      if (index === 'location') {
        return [
          `venue.name.${lang}`,
          `venue.description.${lang}`,
          `links.raw_data.short_desc_${lang}`,
        ]
      }
      else if (index === 'event') {
        return [
          `event.name.${lang}`,
          `event.description.${lang}`,
        ]
      }
      return [];
    };

    const ontologyFields = (lang: string, index: string) => {
      if (index === 'location') {
        return [
          `links.raw_data.ontologyword_ids_enriched.extra_searchwords_${lang}`,
          `links.raw_data.ontologyword_ids_enriched.ontologyword_${lang}`,
          `links.raw_data.ontologytree_ids_enriched.name_${lang}`,
          `links.raw_data.ontologytree_ids_enriched.extra_searchwords_${lang}`,
        ]
      }
      else if (index === 'event') {
        return [
          `ontology.${lang}`,
          `ontology.alt`,
        ]
      }
      return [];
    }

    const defaultQuery = languages.reduce(
      (acc, language) => ({
        ...acc,
        [language]: {
          query_string: {
            query: q,
            fields: searchFields(language, index),
          },
        },
      }),
      {}
    );

    // Resolve query
    let query: any = {
      query: {
        bool: {
          should: Object.values(defaultQuery),
        },
      },
    };

    // Resolve ontology
    if (ontology) {
      const ontologyMatchers = languages.reduce(
        (acc, language) => ({
          ...acc,
          [language]: {
            multi_match: {
              query: ontology,
              fields: ontologyFields(language, index),
            },
          },
        }),
        {}
      );

      query = {
        query: {
          bool: {
            should: languages.map((language) => ({
              bool: {
                must: [defaultQuery[language], ontologyMatchers[language]],
              },
            })),
          },
        },
      };
    }

    // Resolve administrative division
    if (administrativeDivision) {
      query.query.bool.minimum_should_match = 1;
      query.query.bool.filter = {
        term: {
          'venue.location.administrativeDivisions.id.keyword': administrativeDivision,
        },
      };
    }

    // Resolve pagination
    query = {
      from,
      size,
      ...query,
    };

    return this.post(`${es_index}/_search`, undefined, {
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(query),
    });
  }

  async getSuggestions(
    prefix: string,
    languages: ElasticLanguage[],
    index: string = this.defaultIndex,
    size: number
  ) {
    const query = {
      // Hide all source fields to decrease network load
      _source: '',
      suggest: {
        suggestions: {
          prefix,
          completion: {
            field: 'suggest',
            skip_duplicates: true,
            size,
            contexts: {
              language: languages,
            },
          },
        },
      },
    };

    return this.post(`${index}/_search`, undefined, {
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(query),
    });
  }

  async getMapping(q) {
    const data = await this.get(`test-index/_mapping`);
    return data;
  }
}

export { ElasticSearchAPI };

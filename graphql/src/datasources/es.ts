import { ConnectionArguments, ElasticLanguage } from '../types';
import { getEsOffsetPaginationQuery, targetFieldLanguages } from '../utils';

const { RESTDataSource } = require('apollo-datasource-rest');

const ELASTIC_SEARCH_URI: string = process.env.ES_URI;

class ElasticSearchAPI extends RESTDataSource {
  constructor() {
    super();
    this.baseURL = ELASTIC_SEARCH_URI;
    // 'test-index' is alias for all available indexes
    this.defaultIndex = 'test-index';
  }

  async getQueryResults(
    q?: string,
    ontology?: string,
    index?: string,
    connectionArguments?: ConnectionArguments,
    languages?: ElasticLanguage[]
  ) {
    const es_index = index ? index : this.defaultIndex;
    const defaultQuery = {
      multi_match: {
        query: q,
        fields: [
          'venue.name.',
          'venue.description.',
          'links.raw_data.short_desc_',
        ].reduce(
          (acc, fieldPath) => [
            ...acc,
            ...targetFieldLanguages(fieldPath, languages),
          ],
          []
        ),
      },
    };

    // Resolve query
    let query: any = {
      query: defaultQuery,
    };

    // Resolve ontology
    if (ontology) {
      /* TODO, depends on index specific data types */

      query = {
        query: {
          bool: {
            must: [
              defaultQuery,
              {
                multi_match: {
                  query: ontology,
                  fields: [
                    'links.raw_data.ontologyword_ids_enriched.extra_searchwords_',
                    'links.raw_data.ontologyword_ids_enriched.ontologyword_',
                    'links.raw_data.ontologytree_ids_enriched.name_',
                    'links.raw_data.ontologytree_ids_enriched.extra_searchwords_',
                  ].reduce(
                    (acc, fieldPath) => [
                      ...acc,
                      ...targetFieldLanguages(fieldPath, languages),
                    ],
                    []
                  ),
                },
              },
            ],
          },
        },
      };
    }

    /*
      const data = await this.post(`test-index/_search`, undefined,
          {
            headers: { 'Content-Type': 'application/json', },
            body: JSON.stringify(query)
          },
      );
    */

    // Resolve pagination
    query = {
      ...getEsOffsetPaginationQuery(connectionArguments),
      ...query,
    };

    const data = this.post(`${es_index}/_search`, undefined, {
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(query),
    }).then((r) => {
      console.log(r.hits.hits[0]);
      return r;
    });

    return [data];
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

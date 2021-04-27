import { ConnectionArguments } from '../types';
import { getEsOffsetPaginationQuery } from '../utils';

const { RESTDataSource } = require('apollo-datasource-rest');

const ELASTIC_SEARCH_URI: string = process.env.ES_URI;

class ElasticSearchAPI extends RESTDataSource {
  constructor() {
    super();
    this.baseURL = ELASTIC_SEARCH_URI;
  }

  async getQueryResults(
    q?: string,
    ontology?: string,
    index?: string,
    connectionArguments?: ConnectionArguments
  ) {
    // 'test-index' is alias for all available indexes
    const es_index = index ? index : 'test-index';

    // Resolve query
    let query: any = {
      query: {
        query_string: {
          query: q,
        },
      },
    };

    // Resolve ontology
    if (ontology) {
      /* TODO, depends on index specific data types */

      query = {
        query: {
          bool: {
            must: [
              {
                query_string: {
                  query: q,
                },
              },
              {
                multi_match: {
                  query: ontology,
                  fields: [
                    'links.raw_data.ontologyword_ids_enriched.extra_searchwords_*',
                    'links.raw_data.ontologyword_ids_enriched.ontologyword_*',
                    'links.raw_data.ontologytree_ids_enriched.name_*',
                    'links.raw_data.ontologytree_ids_enriched.extra_searchwords_*',
                  ],
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

  async getMapping(q) {
    const data = await this.get(`test-index/_mapping`);
    return data;
  }
}

export { ElasticSearchAPI };

('links.raw_data.ontologyword_ids_enriched.ontologyword_fi.keyword');

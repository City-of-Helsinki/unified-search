const { RESTDataSource } = require('apollo-datasource-rest');

const ELASTIC_SEARCH_URI: string = process.env.ES_URI;

class ElasticSearchAPI extends RESTDataSource {
  constructor() {
    super();
    this.baseURL = ELASTIC_SEARCH_URI;
  }

  async getQueryResults(q, ontology, index) {
    // 'test-index' is alias for all available indexes
    const es_index = index ? index : 'test-index';

    let query: any = {
      query: {
        query_string: {
          query: q,
        },
      },
    };

    if (ontology) {
      /* TODO, depends on index specific data types */

      query = {
        query: {
          bool: {
            must: [
              {
                query_string: {
                  query: q
                }
              }
            ],
            should: [
              {
                term: {
                  "links.raw_data.ontologyword_ids_enriched.extra_searchwords_fi": ontology
                }
              },
              {
                term: {
                  "links.raw_data.ontologyword_ids_enriched.ontologyword_fi": ontology
                }
              }
            ]
          }
        }
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


"links.raw_data.ontologyword_ids_enriched.ontologyword_fi.keyword"
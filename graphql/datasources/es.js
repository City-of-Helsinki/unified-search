const { RESTDataSource } = require('apollo-datasource-rest');

const ELASTIC_SEARCH_URL = "http://localhost:9200";


class ElasticSearchAPI extends RESTDataSource {
    constructor() {
      super();
      this.baseURL = ELASTIC_SEARCH_URL;
    }

    async getQueryResults(q, index) {

      // 'test-index' is alias for all available indexes
      const es_index = index ? index : 'test-index'

      const query = {
        query: {
            query_string: {
                query: q
            }
        }
      };

    /*
      const data = await this.post(`test-index/_search`, undefined,
          {
            headers: { 'Content-Type': 'application/json', },
            body: JSON.stringify(query)
          },
      );
    */

    const data = this.post(`${es_index}/_search`, undefined,
      {
        headers: { 'Content-Type': 'application/json', },
        body: JSON.stringify(query)
        },

      ).then((r) => { console.log(r.hits.hits[0]); return r });

      return [data];
    }

    async getMapping(q) {
      const data = await this.get(`test-index/_mapping`);
      return data;
    }
  }

module.exports = { ElasticSearchAPI };

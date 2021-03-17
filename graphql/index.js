const { makeExecutableSchema, ApolloServer } = require('apollo-server');

const { elasticSearchSchema } = require('./schemas/es');
const { palvelukarttaSchema } = require('./schemas/palvelukartta');
const { ElasticSearchAPI } = require('./datasources/es');


const querySchema = `
  type Query {
    unifiedSearch(
        """
        Free form query string, corresponding to user search input
        """
        q: String,

      ): [ElasticSearchResult]
  }
`;


const resolvers = {
  Query: {
    unifiedSearch: async (_source, { q }, { dataSources }) => {
            return dataSources.elasticSearchAPI.getQueryResults(q);
          },
    },
};


const combinedSchema = makeExecutableSchema({
  typeDefs: [querySchema, elasticSearchSchema, palvelukarttaSchema],
  resolvers
});


const server = new ApolloServer(
    {
    schema: combinedSchema,
    dataSources: () => {
        return {
            elasticSearchAPI: new ElasticSearchAPI(),
            };
        },
    }
);
server.listen().then(({url}) => console.log(`Server running at ${url}`));

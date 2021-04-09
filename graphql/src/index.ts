const {
  makeExecutableSchema,
  ApolloServer,
  SchemaDirectiveVisitor,
} = require('apollo-server');

const { elasticSearchSchema } = require('./schemas/es');
const { palvelukarttaSchema } = require('./schemas/palvelukartta');
const { linkedeventsSchema } = require('./schemas/linkedevents');
const { locationSchema } = require('./schemas/location');
const { sharedSchema } = require('./schemas/shared');
const { reservationSchema } = require('./schemas/reservation');
const { eventSchema } = require('./schemas/event');
const { actorSchema } = require('./schemas/actor');
const { geoSchema } = require('./schemas/geojson');
const { querySchema } = require('./schemas/query');

const { ElasticSearchAPI } = require('./datasources/es');


const resolvers = {
  Query: {
    unifiedSearch: async (_source: any, { q, index }: any, { dataSources }: any) => {
      const res = await dataSources.elasticSearchAPI.getQueryResults(q, index);
      return { es_results: res };
    },
  },
  SearchResultConnection: {
    count(parent: { es_results: any; }, args: any, context: any, info: any) {
      const { es_results } = parent;
      return es_results[0].then((r: { hits: { total: { value: any; }; }; }) => r.hits.total.value);
    },
    max_score(parent: { es_results: any; }, args: any, context: any, info: any) {
      const { es_results } = parent;
      return es_results[0].then((r: { hits: { max_score: any; }; }) => r.hits.max_score);
    },
    pageInfo(parent: any, args: any, context: any, info: any) {
      return {
        hasNextPage: false,
        hasPreviousPage: false,
        startCursor: 'startCursor123',
        endCursor: 'endCursor123',
      };
    },
    edges(parent: { es_results: any; }, args: any, context: any, info: any) {
      console.log('at edges');
      const { es_results } = parent;
      console.log(es_results);

      es_results[0].then((r: any) => console.log(r));
      const edges = es_results[0].then((r: { hits: { hits: any[]; }; }) =>
        r.hits.hits.map(function (e: { _score: any; _source: { venue: any; }; }) {
          return {
            cursor: 123,
            node: {
              _score: e._score,
              venue: { venue: e._source.venue }, // pass parent to child resolver. How to do this better?
            },
          };
        })
      );
      return edges;
    },
  },

  Venue: {
    name({ venue }: any, args: any, context: any, info: any) {
      return venue.name;
    },
    description({ venue }: any, args: any, context: any, info: any) {
      return venue.description;
    },
    location({ venue }: any, args: any, context: any, info: any) {
      return venue.location;
    },
    openingHours({ venue }: any, args: any, context: any, info: any) {
      return venue.openingHours;
    },
  },

  RawJSON: {
    data(parent: any, args: any, context: any, info: any) {
      // Testing and debugging only
      return JSON.stringify(parent);
    },
  },

  SearchResultNode: {
    // TODO
    searchCategories: () => ['POINT_OF_INTEREST'],
  },

  LegalEntity: {
    __resolveType(obj: any, context: any, info: any) {
      return null;
    },
  },
  GeoJSONCRSProperties: {
    __resolveType(obj: any, context: any, info: any) {
      return null;
    },
  },
  GeoJSONGeometryInterface: {
    __resolveType(obj: any, context: any, info: any) {
      return null;
    },
  },
  GeoJSONInterface: {
    __resolveType(obj: any, context: any, info: any) {
      return null;
    },
  },
};

const combinedSchema = makeExecutableSchema({
  typeDefs: [
    querySchema,
    elasticSearchSchema,
    palvelukarttaSchema,
    linkedeventsSchema,
    locationSchema,
    sharedSchema,
    reservationSchema,
    eventSchema,
    actorSchema,
    geoSchema,
  ],
  resolvers,
});

const server = new ApolloServer({
  schema: combinedSchema,
  dataSources: () => {
    return {
      elasticSearchAPI: new ElasticSearchAPI(),
    };
  },
});
server.listen().then(({ url }: any) => console.log(`Server running at ${url}`));
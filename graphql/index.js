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

class OriginDirective extends SchemaDirectiveVisitor {
  visitFieldDefinition(field) {
    const { resource, type, attr } = this.args;
    field.resolve = () => {
      resource, type, attr;
    };
  }

  visitObject(type) {
    console.log(`visitObject: ${type}`);
  }
}

const resolvers = {
  Query: {
    unifiedSearch: async (_source, { q, index }, { dataSources }) => {
      const res = await dataSources.elasticSearchAPI.getQueryResults(q, index);
      return { es_results: res };
    },
  },
  SearchResultConnection: {
    count(parent, args, context, info) {
      const { es_results } = parent;
      return es_results[0].then((r) => r.hits.total.value);
    },
    max_score(parent, args, context, info) {
      const { es_results } = parent;
      return es_results[0].then((r) => r.hits.max_score);
    },
    pageInfo(parent, args, context, info) {
      return {
        hasNextPage: false,
        hasPreviousPage: false,
        startCursor: 'startCursor123',
        endCursor: 'endCursor123',
      };
    },
    edges(parent, args, context, info) {
      console.log('at edges');
      const { es_results } = parent;
      console.log(es_results);

      es_results[0].then((r) => console.log(r));
      const edges = es_results[0].then((r) =>
        r.hits.hits.map(function (e) {
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
    name({ venue }, args, context, info) {
      return venue.name;
    },
    description({ venue }, args, context, info) {
      return venue.description;
    },
    location({ venue }, args, context, info) {
      return venue.location;
    },
    openingHours({ venue }, args, context, info) {
      return venue.openingHours;
    },
  },

  RawJSON: {
    data(parent, args, context, info) {
      // Testing and debugging only
      return JSON.stringify(parent);
    },
  },

  SearchResultNode: {
    // TODO
    searchCategories: () => ['POINT_OF_INTEREST'],
  },

  LegalEntity: {
    __resolveType(obj, context, info) {
      return null;
    },
  },
  GeoJSONCRSProperties: {
    __resolveType(obj, context, info) {
      return null;
    },
  },
  GeoJSONGeometryInterface: {
    __resolveType(obj, context, info) {
      return null;
    },
  },
  GeoJSONInterface: {
    __resolveType(obj, context, info) {
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
  schemaDirectives: {
    origin: OriginDirective,
  },
});

const server = new ApolloServer({
  schema: combinedSchema,
  dataSources: () => {
    return {
      elasticSearchAPI: new ElasticSearchAPI(),
    };
  },
});
server.listen().then(({ url }) => console.log(`Server running at ${url}`));

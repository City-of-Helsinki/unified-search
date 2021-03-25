const { makeExecutableSchema, ApolloServer, SchemaDirectiveVisitor } = require('apollo-server');

const { elasticSearchSchema } = require('./schemas/es');
const { palvelukarttaSchema } = require('./schemas/palvelukartta');
const { linkedeventsSchema } = require('./schemas/linkedevents');
const { locationSchema } = require('./schemas/location');
const { sharedSchema } = require('./schemas/shared');
const { reservationSchema } = require('./schemas/reservation');
const { eventSchema } = require('./schemas/event');
const { actorSchema } = require('./schemas/actor');
const { geoSchema } = require('./schemas/geojson');

const { ElasticSearchAPI } = require('./datasources/es');


const querySchema = `
  directive @origin(service: String, type: String, attr: String) repeatable on FIELD_DEFINITION | OBJECT

  enum UnifiedSearchResultCategory {
    POINT_OF_INTEREST
    EVENT
    RESERVABLE
    ENROLLABLE
    ARTWORK
    ARTICLE
    SERVICE
  }

  type SearchResultConnection {
    """ Elasticsearch raw results """
    es_results: [ElasticSearchResult]

    count: Int
    max_score: Float
    pageInfo: SearchResultPageInfo
    edges: [SearchResultEdge!]!
  }

  type SearchResultPageInfo {
    hasNextPage: Boolean!
    hasPreviousPage: Boolean!
    startCursor: String
    endCursor: String
  }

  type SearchResultEdge {
    cursor: String!
    node: SearchResultNode!
  }

  type SearchResultNode {
    _score: Float
    id: ID!
    name: LanguageString!
    description: LanguageString!
    resources: DescriptionResources
    canonicalUrl: String!
    searchCategories: [UnifiedSearchResultCategory!]!
  }

  type Query {
    unifiedSearch(
        """
        Free form query string, corresponding to user search input
        """
        q: String,

        """
        Optional search index.
        """
        index: String,

      ): SearchResultConnection
  }
`;


class OriginDirective extends SchemaDirectiveVisitor {
    visitFieldDefinition(field) {
      const {resource, type, attr} = this.args
      field.resolve = () => { resource, type, attr }
    }

    visitObject(type) {
      console.log(`visitObject: ${type}`)
    }
  }

  const resolvers = {
  Data: {
    __resolveType(obj, context, info) {
      console.log(obj)
      if(obj.origin === 'linkedevents'){
        return 'LinkedeventsPlace';
      }
      if(obj.origin === 'palvelukartta'){
        return 'PalvelukarttaUnit';
      }

      return null; // GraphQLError is thrown
    },
  },
  Query: {
    unifiedSearch: async (_source, { q, index }, { dataSources }) => {
          const res = await dataSources.elasticSearchAPI.getQueryResults(q, index);
          return {es_results: res}
          },
    },
    SearchResultConnection: {
      count(parent, args, context, info) {
        const { es_results } = parent;
        return es_results[0].then((r) => r.hits.total.value);
      },
      max_score(parent, args, context, info) {
        const { es_results } = parent;
        return es_results[0].then( (r) => r.hits.max_score);
      },
      pageInfo(parent, args, context, info) {
        return {
          hasNextPage: false,
          hasPreviousPage: false,
          startCursor: "startCursor123",
          endCursor: "endCursor123"
        }
      },
      edges(parent, args, context, info) {
        console.log("at edges");
        const { es_results } = parent;
        console.log(es_results);

        es_results[0].then( (r) => console.log(r));
        const edges = es_results[0].then((r) => r.hits.hits.map( function (e) {
           return {
             cursor: 123,
             node: {
               _score: e._score,
               name: {
                 fi: e._source.name_fi ? e._source.name_fi : e._source.name.fi
                },
               description: {
                 fi: e.description ? e.description.fi : e.desc_fi
                }
              }
            }
          }));
        return edges;
      },
    },

  LegalEntity: {
    __resolveType(obj, context, info) {
      return null
    }
  },
  GeoJSONCRSProperties: {
    __resolveType(obj, context, info) {
      return null
    }
  },
  GeoJSONGeometryInterface: {
    __resolveType(obj, context, info) {
      return null
    }
  },
  GeoJSONInterface: {
    __resolveType(obj, context, info) {
      return null
    }
  },

};


const combinedSchema = makeExecutableSchema({
  typeDefs: [querySchema, elasticSearchSchema, palvelukarttaSchema, linkedeventsSchema,
    locationSchema, sharedSchema, reservationSchema, eventSchema, actorSchema, geoSchema],
  resolvers,
  schemaDirectives: {
    origin: OriginDirective,
    }
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

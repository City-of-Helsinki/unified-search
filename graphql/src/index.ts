const { makeExecutableSchema, ApolloServer } = require('apollo-server-express');

import cors from 'cors';
import express from 'express';
import {
  createCursor,
  elasticLanguageFromGraphqlLanguage,
  getEsOffsetPaginationQuery,
} from './utils';
import pageInfoResolver from './resolvers/pageInfoResolver';
import { ConnectionArguments, ConnectionCursorObject } from './types';

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

const OK = 'OK';
const SERVER_IS_NOT_READY = 'SERVER_IS_NOT_READY';

type UnifiedSearchQuery = {
  q?: String;
  ontology?: string;
  administrativeDivisionId?: string;
  ontologyTreeId?: string;
  index?: string;
  languages?: string[];
} & ConnectionArguments;

function edgesFromEsResults(results: any, getCursor: any) {
  return results.hits.hits.map(function (
    e: { _score: any; _source: { venue: any; event: any } },
    index: number
  ) {
    return {
      cursor: getCursor(index + 1),
      node: {
        _score: e._score,
        venue: { venue: e._source.venue }, // pass parent to child resolver. How to do this better?
        event: { event: e._source.event },
      },
    };
  });
}

function getHits(results: any) {
  return results.hits.total.value;
}

const resolvers = {
  Query: {
    unifiedSearch: async (
      _source: any,
      {
        q,
        ontology,
        administrativeDivisionId,
        ontologyTreeId,
        index,
        before,
        after,
        first,
        last,
        languages,
      }: UnifiedSearchQuery,
      { dataSources }: any
    ) => {
      const connectionArguments = { before, after, first, last };
      const { from, size } = getEsOffsetPaginationQuery(connectionArguments);

      const result = await dataSources.elasticSearchAPI.getQueryResults(
        q,
        ontology,
        administrativeDivisionId,
        ontologyTreeId,
        index,
        from,
        size,
        elasticLanguageFromGraphqlLanguage(languages)
      );

      const getCursor = (offset: number) =>
        createCursor<ConnectionCursorObject>({
          offset: from + offset,
        });

      // Find shared data
      const edges = edgesFromEsResults(result, getCursor);
      const hits = getHits(result);

      return { es_results: [result], edges, hits, connectionArguments };
    },
    unifiedSearchCompletionSuggestions: async (
      _source: any,
      { prefix, languages, index, size }: any,
      { dataSources }: any
    ) => {
      const res = await dataSources.elasticSearchAPI.getSuggestions(
        prefix,
        elasticLanguageFromGraphqlLanguage(languages),
        index,
        size
      );

      return {
        suggestions: res.suggest.suggestions[0].options.map((option) => ({
          label: option.text,
        })),
      };
    },
    administrativeDivisions: async (_, __, { dataSources }: any) => {
      const res = await dataSources.elasticSearchAPI.getAdministrativeDivisions();
      return res.hits.hits.map((hit: any) => ({
        id: hit._id,
        ...hit._source,
      }));
    },
  },
  SearchResultConnection: {
    count({ hits }: any) {
      return hits;
    },
    max_score({ es_results }: any) {
      return es_results[0].hits.max_score;
    },
    pageInfo({ edges, hits, connectionArguments }: any) {
      return pageInfoResolver(edges, hits, connectionArguments);
    },
    edges({ edges }: any) {
      return edges;
    },
    es_results({ es_results }: any) {
      return es_results;
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
    images({ venue }: any, args: any, context: any, info: any) {
      return venue.images;
    },
    meta({ venue }: any, args: any, context: any, info: any) {
      return venue.meta;
    },
  },

  Event: {
    name({ event }: any, args: any, context: any, info: any) {
      return event.name;
    },
    description({ event }: any, args: any, context: any, info: any) {
      return event.description;
    },
    meta({ event }: any, args: any, context: any, info: any) {
      return event.meta;
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
      return 'GeoJSONPoint';
    },
  },
  GeoJSONInterface: {
    __resolveType(obj: any, context: any, info: any) {
      return null;
    },
  },
  GeoJSONPoint: {
    type() {
      return 'Point';
    },
    coordinates(obj: any) {
      const long = obj.geometry?.coordinates?.longitude ?? obj.longitude;
      const lat = obj.geometry?.coordinates?.latitude ?? obj.latitude;

      return long && lat ? [long, lat] : null;
    },
  },
  GeoJSONFeature: {
    type() {
      return 'Point';
    },
    geometry(parent: any) {
      return parent;
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

(async () => {
  const server = new ApolloServer({
    schema: combinedSchema,
    dataSources: () => {
      return {
        elasticSearchAPI: new ElasticSearchAPI(),
      };
    },
    introspection: true,
    playground: process.env.PLAYGROUND || false,
  });

  let serverIsReady = false;

  const signalReady = () => {
    serverIsReady = true;
  };

  const checkIsServerReady = (response) => {
    if (serverIsReady) {
      response.send(OK);
    } else {
      response.status(500).send(SERVER_IS_NOT_READY);
    }
  };

  const app = express();

  app.use(cors());

  app.get('/healthz', (request, response) => {
    checkIsServerReady(response);
  });

  app.get('/readiness', (request, response) => {
    checkIsServerReady(response);
  });

  server.applyMiddleware({ app, path: '/search' });

  const port = process.env.GRAPHQL_PROXY_PORT || 4000;

  app.listen({ port }, () => {
    signalReady();

    // eslint-disable-next-line no-console
    console.log(
      `🚀 Server ready at http://localhost:${port}${server.graphqlPath}`
    );
  });
})();

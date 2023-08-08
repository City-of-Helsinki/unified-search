const { ApolloServer } = require('apollo-server-express');
import { buildSubgraphSchema } from '@apollo/subgraph';
import {
  ApolloServerPluginLandingPageGraphQLPlayground,
  ApolloServerPluginLandingPageDisabled,
} from 'apollo-server-core';

import responseCachePlugin from 'apollo-server-plugin-response-cache';
import { ValidationError } from 'apollo-server-express';

import cors from 'cors';
import express from 'express';
import * as Sentry from '@sentry/node';

import {
  createCursor,
  elasticLanguageFromGraphqlLanguage,
  getEsOffsetPaginationQuery,
  isDefined,
} from './utils';
import pageInfoResolver from './resolvers/pageInfoResolver';
import { ConnectionArguments, ConnectionCursorObject } from './types';
import { OrderByDistanceParams, OrderByNameParams } from './datasources/es';

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
const { ontologySchema } = require('./schemas/ontology');

const { ElasticSearchAPI } = require('./datasources/es');

const OK = 'OK';
const SERVER_IS_NOT_READY = 'SERVER_IS_NOT_READY';

type UnifiedSearchQuery = {
  q?: String;
  ontology?: string;
  administrativeDivisionId?: string;
  administrativeDivisionIds?: string[];
  ontologyTreeId?: string;
  ontologyTreeIds?: string[];
  ontologyWordIds?: string[];
  providerTypes?: string[];
  serviceOwnerTypes?: string[];
  targetGroups?: string[];
  mustHaveReservableResource?: boolean;
  accessibilityProfilesWithoutShortcomings?: string[];
  index?: string;
  languages?: string[];
  openAt?: string;
  orderByDistance?: OrderByDistanceParams | null;
  orderByName?: OrderByNameParams | null;
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

function getTodayString() {
  const d = new Date();
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return [year, month, day].join('-');
}

const resolvers = {
  Query: {
    unifiedSearch: async (
      _source: any,
      {
        q,
        ontology,
        administrativeDivisionId,
        administrativeDivisionIds,
        ontologyTreeId,
        ontologyTreeIds,
        ontologyWordIds,
        providerTypes,
        serviceOwnerTypes,
        targetGroups,
        mustHaveReservableResource,
        accessibilityProfilesWithoutShortcomings,
        index,
        before,
        after,
        first,
        last,
        languages,
        openAt,
        orderByDistance,
        orderByName,
      }: UnifiedSearchQuery,
      { dataSources }: any,
      info: any
    ) => {
      const connectionArguments = { before, after, first, last };
      const { from, size } = getEsOffsetPaginationQuery(connectionArguments);

      if (isDefined(orderByDistance) && isDefined(orderByName)) {
        throw new ValidationError(
          'Cannot use both "orderByDistance" and "orderByName".'
        );
      }
      if (orderByDistance === null) {
        throw new ValidationError('"orderByDistance" cannot be null.');
      }
      if (orderByName === null) {
        throw new ValidationError('"orderByName" cannot be null.');
      }

      const result = await dataSources.elasticSearchAPI.getQueryResults(
        q,
        ontology,
        administrativeDivisionId,
        administrativeDivisionIds,
        ontologyTreeId,
        ontologyTreeIds,
        ontologyWordIds,
        providerTypes,
        serviceOwnerTypes,
        targetGroups,
        mustHaveReservableResource,
        accessibilityProfilesWithoutShortcomings,
        index,
        from,
        size,
        elasticLanguageFromGraphqlLanguage(languages),
        openAt,
        orderByDistance,
        orderByName
      );

      const getCursor = (offset: number) =>
        createCursor<ConnectionCursorObject>({
          offset: from + offset,
        });

      // Find shared data
      const edges = edgesFromEsResults(result, getCursor);
      const hits = getHits(result);

      if (result.hits.hits.length >= 1000) {
        info.cacheControl.setCacheHint({
          maxAge: parseInt(process.env.CACHE_MAX_AGE ?? '3600', 10),
        });
      }

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
    administrativeDivisions: async (_, args, { dataSources }: any) => {
      const res = await dataSources.elasticSearchAPI.getAdministrativeDivisions(
        args
      );
      return res.hits.hits.map((hit: any) => ({
        id: hit._id,
        ...hit._source,
      }));
    },
    ontologyTree: async (_, args, { dataSources }: any) => {
      const res = await dataSources.elasticSearchAPI.getOntologyTree(args);
      return res.hits.hits.map((hit: any) => ({
        id: hit._id,
        ...hit._source,
      }));
    },
    ontologyWords: async (_, args, { dataSources }: any) => {
      const res = await dataSources.elasticSearchAPI.getOntologyWords(args);

      return res.hits.hits.map((hit: any) => ({
        id: hit._id,
        ...hit._source,
        label: hit._source.name,
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

  UnifiedSearchVenue: {
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
    ontologyWords({ venue }: any) {
      return venue.ontologyWords;
    },
    serviceOwner({ venue }: any, args: any, context: any, info: any) {
      return venue.serviceOwner;
    },
    resources({ venue }: any, args: any, context: any, info: any) {
      return venue.resources;
    },
    targetGroups({ venue }: any, args: any, context: any, info: any) {
      return venue.targetGroups;
    },
    accessibility({ venue }: any, args: any, context: any, info: any) {
      return venue.accessibility;
    },
    meta({ venue }: any, args: any, context: any, info: any) {
      return venue.meta;
    },
  },

  OpeningHours: {
    today({ data }: any) {
      const openingHoursToday = data.find(
        (openingHoursDay) => openingHoursDay.date === getTodayString()
      );
      return openingHoursToday ? openingHoursToday.times : [];
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

const combinedSchema = buildSubgraphSchema({
  typeDefs: [
    querySchema,
    elasticSearchSchema,
    palvelukarttaSchema,
    linkedeventsSchema,
    locationSchema,
    sharedSchema, // FIXME: OVerlapping with events-proxy (https://tapahtumat-proxy.test.kuva.hel.ninja/proxy/graphql); Keyword and Location Image
    reservationSchema,
    eventSchema,
    actorSchema,
    geoSchema,
    ontologySchema,
  ],
  resolvers,
});

const sentryConfig = {
  // adapted from https://blog.sentry.io/2020/07/22/handling-graphql-errors-using-sentry
  requestDidStart(_) {
    return {
      didEncounterErrors(ctx) {
        // If we couldn't parse the operation, don't
        // do anything here
        if (!ctx.operation) {
          return;
        }
        for (const err of ctx.errors) {
          // Add scoped report details and send to Sentry
          Sentry.withScope((scope) => {
            // Annotate whether failing operation was query/mutation/subscription
            scope.setTag('kind', ctx.operation.operation);
            // Log query and variables as extras
            // (make sure to strip out sensitive data!)
            scope.setExtra('query', ctx.request.query);
            scope.setExtra('variables', ctx.request.variables);
            if (err.path) {
              // We can also add the path as breadcrumb
              scope.addBreadcrumb({
                category: 'query-path',
                message: err.path.join(' > '),
                level: Sentry.Severity.Debug,
              });
            }
            Sentry.captureException(err);
          });
        }
      },
    };
  },
};

(async () => {
  const server = new ApolloServer({
    schema: combinedSchema,
    dataSources: () => {
      return {
        elasticSearchAPI: new ElasticSearchAPI(),
      };
    },
    playground:
      process.env.PLAYGROUND !== null ? Boolean(process.env.PLAYGROUND) : true,
    introspection: true,
    plugins: [responseCachePlugin(), sentryConfig],
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

  await server.start();

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

Sentry.init({ dsn: process.env.SENTRY_DSN });

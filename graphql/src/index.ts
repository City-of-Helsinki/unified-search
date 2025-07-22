import { ApolloServer } from '@apollo/server';
import { expressMiddleware } from '@as-integrations/express5';
import responseCachePlugin from '@apollo/server-plugin-response-cache';
import { ApolloServerPluginDrainHttpServer } from '@apollo/server/plugin/drainHttpServer';
import { buildSubgraphSchema } from '@apollo/subgraph';
import http from 'http';

import cors from 'cors';
import express from 'express';
import * as Sentry from '@sentry/node';

import {
  createCursor,
  elasticLanguageFromGraphqlLanguage,
  getEsOffsetPaginationQuery,
  isDefined,
} from './utils.js';
import pageInfoResolver from './resolvers/pageInfoResolver.js';
import {
  type ConnectionArguments,
  type ConnectionCursorObject,
} from './types.js';
import {
  type AccessibilityProfileType,
  type ElasticSearchIndex,
  type OrderByDistanceParams,
  type OrderByNameParams,
} from './datasources/es/types.js';

import { elasticSearchSchema } from './schemas/es.js';
import { palvelukarttaSchema } from './schemas/palvelukartta.js';
import { linkedeventsSchema } from './schemas/linkedevents.js';
import { locationSchema } from './schemas/location.js';
import { sharedSchema } from './schemas/shared.js';
import { eventSchema } from './schemas/event.js';
import { actorSchema } from './schemas/actor.js';
import { geoSchema } from './schemas/geojson.js';
import { querySchema } from './schemas/query.js';
import { ontologySchema } from './schemas/ontology.js';

import { ElasticSearchAPI } from './datasources/es/index.js';
import { GraphQLError } from 'graphql';
import { ApolloServerErrorCode } from '@apollo/server/errors';

const OK = 'OK';
const SERVER_IS_NOT_READY = 'SERVER_IS_NOT_READY';

type UnifiedSearchQuery = {
  text?: string;
  ontology?: string;
  administrativeDivisionIds?: string[];
  ontologyTreeIdOrSets?: string[][];
  ontologyWordIdOrSets?: string[][];
  providerTypes?: string[];
  serviceOwnerTypes?: string[];
  targetGroups?: string[];
  mustHaveReservableResource?: boolean;
  index?: ElasticSearchIndex;
  languages?: string[];
  openAt?: string;
  orderByDistance?: OrderByDistanceParams;
  orderByName?: OrderByNameParams;
  orderByAccessibilityProfile?: AccessibilityProfileType;
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

function validateOrderByArguments(
  orderByDistance?: OrderByDistanceParams,
  orderByName?: OrderByNameParams,
  orderByAccessibilityProfile?: AccessibilityProfileType
) {
  const orderByArgs = {
    orderByDistance,
    orderByName,
    orderByAccessibilityProfile,
  };

  const isOrderByAmbiguous =
    Object.values(orderByArgs).filter(isDefined).length > 1;

  if (isOrderByAmbiguous) {
    throw new GraphQLError(
      `Cannot use several of ${Object.keys(orderByArgs).join(', ')}`,
      {
        extensions: {
          code: ApolloServerErrorCode.GRAPHQL_VALIDATION_FAILED,
        },
      }
    );
  }

  for (const [orderByArgName, value] of Object.entries(orderByArgs)) {
    if (value === null) {
      throw new GraphQLError(`"${orderByArgName}" cannot be null.`, {
        extensions: {
          code: ApolloServerErrorCode.GRAPHQL_VALIDATION_FAILED,
        },
      });
    }
  }
}

const resolvers = {
  Query: {
    unifiedSearch: async (
      _source: any,
      {
        text,
        ontology,
        administrativeDivisionIds,
        ontologyTreeIdOrSets,
        ontologyWordIdOrSets,
        providerTypes,
        serviceOwnerTypes,
        targetGroups,
        mustHaveReservableResource,
        index,
        after,
        first,
        languages,
        openAt,
        orderByDistance,
        orderByName,
        orderByAccessibilityProfile,
      }: UnifiedSearchQuery,
      { dataSources }: any,
      info: any
    ) => {
      const connectionArguments = { after, first };
      const { from, size } = getEsOffsetPaginationQuery(connectionArguments);

      validateOrderByArguments(
        orderByDistance,
        orderByName,
        orderByAccessibilityProfile
      );

      const result = await dataSources.elasticSearchAPI.getQueryResults({
        text,
        ontology,
        administrativeDivisionIds,
        ontologyTreeIdOrSets,
        ontologyWordIdOrSets,
        providerTypes,
        serviceOwnerTypes,
        targetGroups,
        mustHaveReservableResource,
        index,
        from,
        size,
        languages: elasticLanguageFromGraphqlLanguage(languages),
        openAt,
        orderByDistance,
        orderByName,
        orderByAccessibilityProfile,
      });

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
      const res = await dataSources.elasticSearchAPI.getSuggestions({
        prefix,
        languages: elasticLanguageFromGraphqlLanguage(languages),
        size,
        index,
      });

      return {
        suggestions: res.suggest.suggestions[0].options.map((option) => ({
          label: option.text,
        })),
      };
    },
    administrativeDivisions: async (_, args, { dataSources }: any) => {
      const res =
        await dataSources.elasticSearchAPI.getAdministrativeDivisions(args);
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
    async pageInfo({ edges, hits, connectionArguments }: any) {
      return await pageInfoResolver(edges, hits, connectionArguments);
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
    reservation({ venue }: any, args: any, context: any, info: any) {
      return venue.reservation;
    },
    targetGroups({ venue }: any, args: any, context: any, info: any) {
      return venue.targetGroups;
    },
    accessibility({ venue }: any, args: any, context: any, info: any) {
      return venue.accessibility;
    },
    accessibilityShortcomingFor(
      { venue }: any,
      args: any,
      context: any,
      info: any
    ) {
      if (args.profile) {
        const shortcoming = venue.accessibility.shortcomings.filter(
          (shortcoming: any) => shortcoming.profile === args.profile
        );
        if (shortcoming && shortcoming.length > 0) {
          return shortcoming[0];
        }
      }
      return undefined;
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
    eventSchema,
    actorSchema,
    geoSchema,
    ontologySchema,
  ],
  resolvers,
});

const sentryConfig = {
  // adapted from https://blog.sentry.io/2020/07/22/handling-graphql-errors-using-sentry
  async requestDidStart(_) {
    return {
      async didEncounterErrors(ctx) {
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
                level: 'debug',
              });
            }
            Sentry.captureException(err);
          });
        }
      },
    };
  },
};

void (async () => {
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
  const httpServer = http.createServer(app);

  const server = new ApolloServer({
    schema: combinedSchema,
    introspection: true,
    plugins: [
      ApolloServerPluginDrainHttpServer({ httpServer }),
      responseCachePlugin(),
      sentryConfig,
    ],
  });
  await server.start();

  app.use(
    '/search',
    cors(),
    express.json(),
    expressMiddleware(server, {
      context: async () => ({
        dataSources: {
          elasticSearchAPI: new ElasticSearchAPI(),
        },
      }),
    })
  );

  const port = process.env.GRAPHQL_PROXY_PORT || 4000;

  httpServer.listen({ port }, () => {
    signalReady();
    // eslint-disable-next-line no-console
    console.log(`🚀 Server ready at http://localhost:${port}/search`);
  });

  app.get('/healthz', (request, response) => {
    checkIsServerReady(response);
  });

  app.get('/readiness', (request, response) => {
    checkIsServerReady(response);
  });
})();

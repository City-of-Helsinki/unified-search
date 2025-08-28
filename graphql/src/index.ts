import http from 'http';

import type { GraphQLResolveInfoWithCacheControl } from '@apollo/cache-control-types';
import { ApolloServer } from '@apollo/server';
import { ApolloServerPluginLandingPageDisabled } from '@apollo/server/plugin/disabled';
import { ApolloServerPluginDrainHttpServer } from '@apollo/server/plugin/drainHttpServer';
import { ApolloServerPluginLandingPageLocalDefault } from '@apollo/server/plugin/landingPage/default';
import responseCachePlugin from '@apollo/server-plugin-response-cache';
import { buildSubgraphSchema } from '@apollo/subgraph';
import { expressMiddleware } from '@as-integrations/express5';
import * as Sentry from '@sentry/node';
import cors from 'cors';
import dotenv from 'dotenv';
import express from 'express';
import helmet, { HelmetOptions } from 'helmet';

import { corsConfig, CSP } from './constants.js';
import { ElasticSearchAPI } from './datasources/es/index.js';
import type {
  AccessibilityProfileType,
  AdministrativeDivisionParams,
  ElasticSearchIndex,
  OntologyTreeParams,
  OntologyWordParams,
  OrderByDistanceParams,
  OrderByNameParams,
  SuggestionsParams,
} from './datasources/es/types.js';
import healthz from './healthz.js';
import readiness from './readiness.js';
import pageInfoResolver, { Edge } from './resolvers/pageInfoResolver.js';
import { elasticSearchSchema } from './schemas/es.js';
import { geoSchema } from './schemas/geojson.js';
import { locationSchema } from './schemas/location.js';
import { ontologySchema } from './schemas/ontology.js';
import { palvelukarttaSchema } from './schemas/palvelukartta.js';
import { querySchema } from './schemas/query.js';
import { sharedSchema } from './schemas/shared.js';
import type {
  ConnectionArguments,
  ConnectionCursorObject,
  EsHit,
  EsResults,
  Venue,
} from './types.js';
import {
  createCursor,
  edgesFromEsResults,
  elasticLanguageFromGraphqlLanguage,
  findClosestEnvFile,
  getEsOffsetPaginationQuery,
  getHits,
  getTodayString,
  validateOrderByArguments,
} from './utils.js';

const ENV_FILE_PATH = findClosestEnvFile();

if (ENV_FILE_PATH) {
  dotenv.config({ path: ENV_FILE_PATH });
} else {
  // eslint-disable-next-line no-console
  console.log('No .env file found, using environment variables directly.');
}

const SERVER_IS_NOT_READY = 'SERVER_IS_NOT_READY';

const ENABLE_APOLLO_SANDBOX = ['true', 'yes', '1'].includes(
  (process.env.ENABLE_APOLLO_SANDBOX ?? '').toString().toLowerCase().trim()
);

function getLandingPagePlugin() {
  if (ENABLE_APOLLO_SANDBOX) {
    return ApolloServerPluginLandingPageLocalDefault({
      embed: { runTelemetry: false },
    });
  }
  return ApolloServerPluginLandingPageDisabled();
}

/**
 * CSP (i.e. Content Security Policy) configuration
 * without Apollo Sandbox use.
 *
 * This is a very restrictive policy because this is a GraphQL server
 * and querying/mutating & introspecting the schema don't need much.
 *
 * Configuration options documented at:
 * https://helmetjs.github.io/#reference
 */
const cspConfigWithoutApolloSandbox = {
  contentSecurityPolicy: {
    useDefaults: false, // No defaults, the wanted configuration is explicit
    directives: {
      baseUri: [CSP.none],
      childSrc: [CSP.none],
      connectSrc: [CSP.none],
      defaultSrc: [CSP.none],
      fontSrc: [CSP.none],
      formAction: [CSP.none],
      frameAncestors: [CSP.none],
      frameSrc: [CSP.none],
      imgSrc: [CSP.none],
      manifestSrc: [CSP.none],
      mediaSrc: [CSP.none],
      objectSrc: [CSP.none],
      scriptSrc: [CSP.none],
      styleSrc: [CSP.none],
      workerSrc: [CSP.none],
      upgradeInsecureRequests: [], // Enable upgrade-insecure-requests
    },
  },
} as const satisfies HelmetOptions;

/**
 * CSP (i.e. Content Security Policy) configuration
 * with Apollo Sandbox use.
 *
 * WARNING: This should not be used in production environment!
 *
 * Configuration options documented at:
 * https://helmetjs.github.io/#reference
 */
const cspConfigWithApolloSandbox = {
  contentSecurityPolicy: {
    useDefaults: false, // No defaults, the wanted configuration is explicit
    directives: {
      ...cspConfigWithoutApolloSandbox.contentSecurityPolicy.directives,
      scriptSrc: [
        CSP.self,
        CSP.unsafeInline,
        'https://embeddable-sandbox.cdn.apollographql.com',
      ],
      styleSrc: [CSP.self, CSP.unsafeInline, 'https://fonts.googleapis.com'],
      imgSrc: [
        CSP.self,
        'https://apollo-server-landing-page.cdn.apollographql.com',
      ],
      fontSrc: [CSP.self, 'https://fonts.gstatic.com'],
      frameSrc: [CSP.self, 'https://sandbox.embed.apollographql.com'],
      connectSrc: [CSP.self],
      manifestSrc: [
        CSP.self,
        'https://apollo-server-landing-page.cdn.apollographql.com',
      ],
    },
  },
} as const satisfies HelmetOptions;

function getCspConfig():
  | typeof cspConfigWithApolloSandbox
  | typeof cspConfigWithoutApolloSandbox {
  if (ENABLE_APOLLO_SANDBOX) {
    return cspConfigWithApolloSandbox;
  }
  return cspConfigWithoutApolloSandbox;
}

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

type VenueProps = {
  venue: Venue;
};

type QueryContext = {
  dataSources: {
    elasticSearchAPI: ElasticSearchAPI;
  };
};

type GeoJSONPointInput = {
  geometry?: {
    coordinates?: {
      longitude?: number;
      latitude?: number;
    };
  };
  longitude?: number;
  latitude?: number;
};

type LongitudeLatitude = [longitude: number, latitude: number];

type PageInfoProps = {
  edges: Edge[];
  hits: number;
  connectionArguments: ConnectionArguments;
};

const resolvers = {
  Query: {
    unifiedSearch: async (
      _source: unknown,
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
      { dataSources }: QueryContext,
      info: GraphQLResolveInfoWithCacheControl
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
      _source: unknown,
      { prefix, languages, index, size }: SuggestionsParams,
      { dataSources }: QueryContext
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
    administrativeDivisions: async (
      _,
      args: AdministrativeDivisionParams,
      { dataSources }: QueryContext
    ) => {
      const res: EsResults =
        await dataSources.elasticSearchAPI.getAdministrativeDivisions(args);
      return res.hits.hits.map((hit: EsHit) => ({
        id: hit._id,
        ...hit._source,
      }));
    },
    ontologyTree: async (
      _,
      args: OntologyTreeParams,
      { dataSources }: QueryContext
    ) => {
      const res: EsResults =
        await dataSources.elasticSearchAPI.getOntologyTree(args);
      return res.hits.hits.map((hit: EsHit) => ({
        id: hit._id,
        ...hit._source,
      }));
    },
    ontologyWords: async (
      _,
      args: OntologyWordParams,
      { dataSources }: QueryContext
    ) => {
      const res: EsResults =
        await dataSources.elasticSearchAPI.getOntologyWords(args);

      return res.hits.hits.map((hit: EsHit) => ({
        id: hit._id,
        ...hit._source,
        label: hit._source.name,
      }));
    },
  },

  SearchResultConnection: {
    count({ hits }: PageInfoProps) {
      return hits;
    },
    max_score({ es_results }: unknown) {
      return es_results[0].hits.max_score;
    },
    async pageInfo({ edges, hits, connectionArguments }: PageInfoProps) {
      return await pageInfoResolver(edges, hits, connectionArguments);
    },
    edges({ edges }: PageInfoProps) {
      return edges;
    },
    es_results({ es_results }: unknown) {
      return es_results;
    },
  },

  UnifiedSearchVenue: {
    name({ venue }: VenueProps) {
      return venue.name;
    },
    description({ venue }: VenueProps) {
      return venue.description;
    },
    location({ venue }: VenueProps) {
      return venue.location;
    },
    openingHours({ venue }: VenueProps) {
      return venue.openingHours;
    },
    images({ venue }: VenueProps) {
      return venue.images;
    },
    ontologyWords({ venue }: VenueProps) {
      return venue.ontologyWords;
    },
    serviceOwner({ venue }: VenueProps) {
      return venue.serviceOwner;
    },
    reservation({ venue }: VenueProps) {
      return venue.reservation;
    },
    targetGroups({ venue }: VenueProps) {
      return venue.targetGroups;
    },
    accessibility({ venue }: VenueProps) {
      return venue.accessibility;
    },
    accessibilityShortcomingFor(
      { venue }: VenueProps,
      args: { profile?: AccessibilityProfileType }
    ) {
      if (args.profile) {
        const shortcoming = venue.accessibility.shortcomings.filter(
          (shortcoming) => shortcoming.profile === args.profile
        );
        if (shortcoming && shortcoming.length > 0) {
          return shortcoming[0];
        }
      }
      return undefined;
    },
    meta({ venue }: VenueProps) {
      return venue.meta;
    },
  },

  OpeningHours: {
    today({ data }: unknown) {
      const openingHoursToday = data.find(
        (openingHoursDay) => openingHoursDay.date === getTodayString()
      );
      return openingHoursToday ? openingHoursToday.times : [];
    },
  },

  RawJSON: {
    data(parent: unknown) {
      // Testing and debugging only
      return JSON.stringify(parent);
    },
  },

  GeoJSONCRSProperties: {
    __resolveType() {
      return null;
    },
  },
  GeoJSONGeometryInterface: {
    __resolveType() {
      return 'GeoJSONPoint';
    },
  },
  GeoJSONInterface: {
    __resolveType() {
      return null;
    },
  },
  GeoJSONPoint: {
    type() {
      return 'Point';
    },
    coordinates(obj: GeoJSONPointInput): LongitudeLatitude | null {
      const long = obj.geometry?.coordinates?.longitude ?? obj.longitude;
      const lat = obj.geometry?.coordinates?.latitude ?? obj.latitude;

      return long && lat ? [long, lat] : null;
    },
  },
  GeoJSONFeature: {
    type() {
      return 'Point';
    },
    geometry(parent: unknown) {
      return parent;
    },
  },
};

const combinedSchema = buildSubgraphSchema({
  typeDefs: [
    querySchema,
    elasticSearchSchema,
    palvelukarttaSchema,
    locationSchema,
    sharedSchema, // FIXME: Overlapping with events-proxy (https://tapahtumat-proxy.test.kuva.hel.ninja/proxy/graphql); Location Image
    geoSchema,
    ontologySchema,
  ],
  resolvers,
});

const sentryConfig = {
  // adapted from https://blog.sentry.io/2020/07/22/handling-graphql-errors-using-sentry
  async requestDidStart() {
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
  let serverIsReady: boolean = false;

  const signalReady = () => {
    serverIsReady = true;
  };

  const app = express();
  const httpServer = http.createServer(app);

  const server = new ApolloServer({
    schema: combinedSchema,
    introspection: true,
    plugins: [
      getLandingPagePlugin(),
      ApolloServerPluginDrainHttpServer({ httpServer }),
      responseCachePlugin(),
      sentryConfig,
    ],
  });
  await server.start();

  app.use(
    '/search',
    helmet(getCspConfig()),
    cors(corsConfig),
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

  app.get('/healthz', (_, response) => {
    if (!serverIsReady) {
      response.status(500).send(SERVER_IS_NOT_READY);
    }
    return healthz(response);
  });

  app.get('/readiness', (_, response) => {
    if (!serverIsReady) {
      response.status(500).send(SERVER_IS_NOT_READY);
    }
    return readiness(response);
  });
})();

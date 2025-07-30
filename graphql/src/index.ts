import http from 'http';

import type { GraphQLResolveInfoWithCacheControl } from '@apollo/cache-control-types';
import { ApolloServer } from '@apollo/server';
import { ApolloServerErrorCode } from '@apollo/server/errors';
import { ApolloServerPluginLandingPageDisabled } from '@apollo/server/plugin/disabled';
import { ApolloServerPluginDrainHttpServer } from '@apollo/server/plugin/drainHttpServer';
import responseCachePlugin from '@apollo/server-plugin-response-cache';
import { buildSubgraphSchema } from '@apollo/subgraph';
import { expressMiddleware } from '@as-integrations/express5';
import * as Sentry from '@sentry/node';
import cors from 'cors';
import express from 'express';
import { GraphQLError } from 'graphql';

import type { GetSuggestionProps } from './datasources/es/api/index.js';
import { ElasticSearchAPI } from './datasources/es/index.js';
import {
  type AccessibilityProfileType,
  type AdministrativeDivisionParams,
  type ElasticSearchIndex,
  type OntologyTreeParams,
  type OntologyWordParams,
  type OrderByDistanceParams,
  type OrderByNameParams,
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
import {
  type ConnectionArguments,
  type ConnectionCursorObject,
} from './types.js';
import {
  createCursor,
  elasticLanguageFromGraphqlLanguage,
  getEsOffsetPaginationQuery,
  isDefined,
} from './utils.js';

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

// FIXME: Combine GraphQL and TypeScript types, e.g. by generating the latter from the former
type Venue = {
  accessibility?: {
    shortcomings: Array<{ profile: AccessibilityProfileType }>;
  };
  description?: unknown;
  images?: unknown;
  location?: unknown;
  meta?: unknown;
  name?: unknown;
  ontologyWords?: unknown;
  openingHours?: unknown;
  reservation?: unknown;
  serviceOwner?: unknown;
  targetGroups?: unknown;
};

type VenueProps = {
  venue: Venue;
};

type EsHitSource = {
  name?: unknown;
  venue?: Venue;
};

type EsHit = {
  _score: number;
  _source: EsHitSource;
  _id?: string;
};

type EsResults = {
  hits: {
    hits: EsHit[];
    total: { value: number };
    max_score?: number;
  };
  suggest?: {
    suggestions: Array<{
      options: Array<{ text: string }>;
    }>;
  };
};

type QueryContext = {
  dataSources: {
    elasticSearchAPI: ElasticSearchAPI;
  };
};

type GetCursor = (index: number) => string;

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

const edgesFromEsResults = (results: EsResults, getCursor: GetCursor) =>
  results.hits.hits.map((e: EsHit, index: number) => ({
    cursor: getCursor(index + 1),
    node: {
      _score: e._score,
      venue: { venue: e._source.venue }, // pass parent to child resolver. How to do this better?
    },
  }));

const getHits = (results: EsResults) => results.hits.total.value;

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
      { prefix, languages, index, size }: GetSuggestionProps,
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
    sharedSchema, // FIXME: OVerlapping with events-proxy (https://tapahtumat-proxy.test.kuva.hel.ninja/proxy/graphql); Keyword and Location Image
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
      ApolloServerPluginLandingPageDisabled(), // No need for landing page
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

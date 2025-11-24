// eslint-disable-next-line
import './sentry-init.mjs'; // MUST be FIRST IMPORT! See file for details.

import http from 'http';

import { ApolloServer } from '@apollo/server';
import { ApolloServerPluginLandingPageDisabled } from '@apollo/server/plugin/disabled';
import { ApolloServerPluginDrainHttpServer } from '@apollo/server/plugin/drainHttpServer';
import { ApolloServerPluginLandingPageLocalDefault } from '@apollo/server/plugin/landingPage/default';
import responseCachePlugin from '@apollo/server-plugin-response-cache';
import { buildSubgraphSchema } from '@apollo/subgraph';
import { expressMiddleware } from '@as-integrations/express5';
import cors from 'cors';
import dotenv from 'dotenv';
import express from 'express';
import helmet from 'helmet';

import {
  corsConfig,
  cspConfigWithApolloSandbox,
  cspConfigWithoutApolloSandbox,
} from './constants.js';
import { ElasticSearchAPI } from './datasources/es/index.js';
import healthz from './healthz.js';
import readiness from './readiness.js';
import { getResolvers } from './resolvers/getResolvers.js';
import { getSchemas } from './schemas/getSchemas.js';
import { findClosestEnvFile, sentryConfig } from './utils.js';

const ENV_FILE_PATH = findClosestEnvFile();

if (ENV_FILE_PATH) {
  dotenv.config({ path: ENV_FILE_PATH });
} else {
  // eslint-disable-next-line no-console
  console.info('No .env file found, using environment variables directly.');
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

const getCspConfig = () =>
  ENABLE_APOLLO_SANDBOX
    ? cspConfigWithApolloSandbox
    : cspConfigWithoutApolloSandbox;

const combinedSchema = buildSubgraphSchema({
  typeDefs: getSchemas(),
  resolvers: getResolvers(),
});

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
    console.info(`🚀 Server ready at http://localhost:${port}/search`);
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

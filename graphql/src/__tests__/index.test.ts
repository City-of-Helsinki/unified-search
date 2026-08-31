import type { Response } from 'express';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => {
  type RouteHandler = (_request: unknown, response: Response) => unknown;

  const state: {
    envFilePath: string | null;
    listenCallback?: () => void;
    middlewareOptions?: { context: () => Promise<unknown> };
  } = {
    envFilePath: null,
  };
  const routes = new Map<string, RouteHandler>();
  const app = {
    get: vi.fn((path: string, handler: RouteHandler) => {
      routes.set(path, handler);
    }),
    use: vi.fn(),
  };
  const httpServer = {
    listen: vi.fn((_options: unknown, callback: () => void) => {
      state.listenCallback = callback;
    }),
  };

  return {
    app,
    buildSubgraphSchema: vi.fn(() => ({ schema: true })),
    cors: vi.fn(() => 'cors-middleware'),
    createServer: vi.fn(() => httpServer),
    disabledLandingPagePlugin: vi.fn(() => 'disabled-landing-page'),
    dotenvConfig: vi.fn(),
    drainHttpServerPlugin: vi.fn(() => 'drain-http-server'),
    elasticSearchApiConstructor: vi.fn(),
    expressJson: vi.fn(() => 'json-middleware'),
    expressMiddleware: vi.fn((_server: unknown, options: unknown) => {
      state.middlewareOptions = options as {
        context: () => Promise<unknown>;
      };
      return 'graphql-middleware';
    }),
    getResolvers: vi.fn(() => ({ Query: {} })),
    getSchemas: vi.fn(() => ['schema']),
    helmet: vi.fn(() => 'helmet-middleware'),
    httpServer,
    localLandingPagePlugin: vi.fn(() => 'local-landing-page'),
    responseCachePlugin: vi.fn(() => 'response-cache'),
    routes,
    sentryConfig: { name: 'sentry' },
    startServer: vi.fn(),
    state,
  };
});

vi.mock('../sentry-init.mjs', () => ({}));

vi.mock('node:http', () => ({
  default: { createServer: mocks.createServer },
}));

vi.mock('@apollo/server', () => ({
  ApolloServer: class {
    start = mocks.startServer;
  },
}));

vi.mock('@apollo/server/plugin/disabled', () => ({
  ApolloServerPluginLandingPageDisabled: mocks.disabledLandingPagePlugin,
}));

vi.mock('@apollo/server/plugin/drainHttpServer', () => ({
  ApolloServerPluginDrainHttpServer: mocks.drainHttpServerPlugin,
}));

vi.mock('@apollo/server/plugin/landingPage/default', () => ({
  ApolloServerPluginLandingPageLocalDefault: mocks.localLandingPagePlugin,
}));

vi.mock('@apollo/server-plugin-response-cache', () => ({
  default: mocks.responseCachePlugin,
}));

vi.mock('@apollo/subgraph', () => ({
  buildSubgraphSchema: mocks.buildSubgraphSchema,
}));

vi.mock('@as-integrations/express5', () => ({
  expressMiddleware: mocks.expressMiddleware,
}));

vi.mock('cors', () => ({ default: mocks.cors }));
vi.mock('dotenv', () => ({ default: { config: mocks.dotenvConfig } }));
vi.mock('helmet', () => ({ default: mocks.helmet }));

vi.mock('express', () => ({
  default: Object.assign(
    vi.fn(() => mocks.app),
    {
      json: mocks.expressJson,
    }
  ),
}));

vi.mock('../datasources/es/index.js', () => ({
  ElasticSearchAPI: class {
    constructor() {
      mocks.elasticSearchApiConstructor();
    }
  },
}));

vi.mock('../resolvers/getResolvers.js', () => ({
  getResolvers: mocks.getResolvers,
}));

vi.mock('../schemas/getSchemas.js', () => ({
  getSchemas: mocks.getSchemas,
}));

vi.mock('../utils.js', () => ({
  findClosestEnvFile: () => mocks.state.envFilePath,
  sentryConfig: mocks.sentryConfig,
}));

const ORIGINAL_PROCESS_ENV = { ...process.env };

const makeResponse = () => {
  const response = {
    json: vi.fn(),
    send: vi.fn(),
    status: vi.fn(),
  };
  response.json.mockReturnValue(response);
  response.send.mockReturnValue(response);
  response.status.mockReturnValue(response);
  return response;
};

const getRoute = (path: string) => {
  const route = mocks.routes.get(path);
  expect(route).toBeDefined();
  return route!;
};

describe('GraphQL server entry point', () => {
  beforeEach(() => {
    vi.resetModules();
    vi.clearAllMocks();
    process.env = { ...ORIGINAL_PROCESS_ENV };
    delete process.env.ENABLE_APOLLO_SANDBOX;
    mocks.routes.clear();
    mocks.state.envFilePath = null;
    mocks.state.listenCallback = undefined;
    mocks.state.middlewareOptions = undefined;
    vi.spyOn(console, 'info').mockImplementation(() => undefined);
  });

  afterEach(() => {
    process.env = { ...ORIGINAL_PROCESS_ENV };
    vi.restoreAllMocks();
  });

  it('serves health endpoints before and after the server becomes ready', async () => {
    await import('../index.js');

    const healthzRoute = getRoute('/healthz');
    const readinessRoute = getRoute('/readiness');
    const unavailableHealthzResponse = makeResponse();
    const unavailableReadinessResponse = makeResponse();

    healthzRoute({}, unavailableHealthzResponse as unknown as Response);
    readinessRoute({}, unavailableReadinessResponse as unknown as Response);

    expect(unavailableHealthzResponse.status).toHaveBeenCalledWith(500);
    expect(unavailableHealthzResponse.send).toHaveBeenCalledWith(
      'SERVER_IS_NOT_READY'
    );
    expect(unavailableHealthzResponse.json).not.toHaveBeenCalled();
    expect(unavailableReadinessResponse.status).toHaveBeenCalledWith(500);
    expect(unavailableReadinessResponse.send).toHaveBeenCalledWith(
      'SERVER_IS_NOT_READY'
    );
    expect(unavailableReadinessResponse.json).not.toHaveBeenCalled();

    expect(mocks.state.listenCallback).toBeDefined();
    mocks.state.listenCallback?.();

    const readyHealthzResponse = makeResponse();
    const readyReadinessResponse = makeResponse();
    healthzRoute({}, readyHealthzResponse as unknown as Response);
    readinessRoute({}, readyReadinessResponse as unknown as Response);

    expect(readyHealthzResponse.status).toHaveBeenCalledWith(200);
    expect(readyHealthzResponse.json).toHaveBeenCalledWith({ status: 'ok' });
    expect(readyReadinessResponse.status).toHaveBeenCalledWith(200);
    expect(readyReadinessResponse.json).toHaveBeenCalledWith(
      expect.objectContaining({ status: 'ok' })
    );

    const context = await mocks.state.middlewareOptions?.context();
    expect(context).toStrictEqual({
      dataSources: { elasticSearchAPI: expect.any(Object) },
    });
    expect(mocks.elasticSearchApiConstructor).toHaveBeenCalledOnce();
    expect(mocks.disabledLandingPagePlugin).toHaveBeenCalledOnce();
  });

  it('loads the environment file and enables Apollo Sandbox', async () => {
    process.env.ENABLE_APOLLO_SANDBOX = 'yes';
    mocks.state.envFilePath = '/config/.env';

    await import('../index.js');

    expect(mocks.dotenvConfig).toHaveBeenCalledWith({ path: '/config/.env' });
    expect(mocks.localLandingPagePlugin).toHaveBeenCalledWith({
      embed: { runTelemetry: false },
    });
    expect(mocks.disabledLandingPagePlugin).not.toHaveBeenCalled();
  });
});

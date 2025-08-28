import fs from 'fs';
import path from 'path';

import { ApolloServerErrorCode } from '@apollo/server/errors';
import * as Sentry from '@sentry/node';
import { GraphQLError } from 'graphql';

import {
  GraphQlToElasticLanguageMap,
  elasticSearchQueryStringSpecialCharsRegExpPattern,
} from './constants.js';
import type {
  AccessibilityProfileType,
  OrderByDistanceParams,
  OrderByNameParams,
} from './datasources/es/types.js';
import type {
  ConnectionArguments,
  ElasticSearchPagination,
  ConnectionCursorObject,
  ElasticLanguage,
  EsResults,
  GetCursor,
  EsHit,
} from './types.js';

export function createCursor<T>(query: T): string {
  return Buffer.from(JSON.stringify(query)).toString('base64');
}

export function readCursor<T>(cursor: string | null): T {
  if (!cursor) {
    return null;
  }

  return JSON.parse(Buffer.from(cursor, 'base64').toString('utf8')) as T;
}

export function getEsOffsetPaginationQuery({
  after,
  first = null,
}: ConnectionArguments): ElasticSearchPagination {
  if ((first !== null && typeof first !== 'number') || first < 0) {
    throw new Error('First must be a positive number');
  }

  let offset = 0;
  // If no size can be inferred, let elastic use its default logic
  const size = first ?? undefined;

  if (after) {
    const afterObject = readCursor<ConnectionCursorObject>(after);

    offset = afterObject.offset;
  }

  return {
    from: offset,
    size,
  };
}

export function elasticLanguageFromGraphqlLanguage(
  graphqlLanguages: string[]
): ElasticLanguage[] {
  return graphqlLanguages.map(
    (language) => GraphQlToElasticLanguageMap[language]
  );
}

export function targetFieldLanguages(
  field: string,
  languages: ElasticLanguage[]
) {
  // If all languages are targeted, use wildcard search
  if (languages.length === Object.values(GraphQlToElasticLanguageMap).length) {
    return [`${field}*`];
  }

  return languages.map((language) => `${field}${language}`);
}

export function isDefined<T>(value: T): value is Exclude<T, undefined> {
  return typeof value !== 'undefined';
}

/**
 * If you need to use any of the characters which function as operators in your query itself (and not as operators),
 * then you should escape them with a leading backslash.
 *
 * The reserved special characters are:
 * `+ - = && || > < ! ( ) { } [ ] ^ " ~ * ? : \ /`.
 * "Failing to escape these special characters correctly could lead to a syntax error
 * which prevents your query from running."
 *
 * Reference:
 * https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#_reserved_characters
 */
export function escapeQuery(text: string) {
  return text.replace(
    elasticSearchQueryStringSpecialCharsRegExpPattern,
    '\\$1'
  );
}

const ENV_FILE = '.env' as const;

const ENV_FILE_PATHS = [
  `./${ENV_FILE}`,
  `../${ENV_FILE}`,
  `../../${ENV_FILE}`,
  `../../../${ENV_FILE}`,
] as const;

type EnvFilePath = (typeof ENV_FILE_PATHS)[number];

/**
 * Finds the closest `.env` file in the current directory or its parents
 * (max. up 3 levels).
 *
 * @return Path to closest `.env` file including the filename itself,
 *         or null if not found.
 */
export function findClosestEnvFile(): EnvFilePath | null {
  // Try local directory first, then the parent, then parent's parent and so on.
  for (const envFilePath of ENV_FILE_PATHS) {
    if (fs.existsSync(envFilePath)) {
      return envFilePath;
    }
  }
  return null;
}

/**
 * Finds the closest `.env` file's directory (max. up 3 levels).
 *
 * @return Directory of closest `.env` file, or null if not found.
 */
export function findClosestEnvFileDir() {
  const envFilePath = findClosestEnvFile();
  if (envFilePath) {
    return path.dirname(envFilePath);
  }
  return null;
}

export const edgesFromEsResults = (results: EsResults, getCursor: GetCursor) =>
  results.hits.hits.map((e: EsHit, index: number) => ({
    cursor: getCursor(index + 1),
    node: {
      _score: e._score,
      venue: { venue: e._source.venue }, // pass parent to child resolver. How to do this better?
    },
  }));

export const getHits = (results: EsResults) => results.hits.total.value;

export function getTodayString() {
  const d = new Date();
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return [year, month, day].join('-');
}

export function validateOrderByArguments(
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

/**
 * Sentry configuration for Apollo Server
 *
 * Based on https://blog.sentry.io/2020/07/22/handling-graphql-errors-using-sentry
 */
export const sentryConfig = {
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
} as const;

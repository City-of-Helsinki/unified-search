import fs from 'fs';
import path from 'path';

import {
  GraphQlToElasticLanguageMap,
  elasticSearchQueryStringSpecialCharsRegExpPattern,
} from './constants.js';
import {
  type ConnectionArguments,
  type ElasticSearchPagination,
  type ConnectionCursorObject,
  type ElasticLanguage,
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

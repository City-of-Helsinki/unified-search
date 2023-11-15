import { GraphQlToElasticLanguageMap } from './constants';
import {
  type ConnectionArguments,
  type ElasticSearchPagination,
  type ConnectionCursorObject,
  type ElasticLanguage,
} from './types';

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

export function isDefined(value: any) {
  return typeof value !== 'undefined';
}

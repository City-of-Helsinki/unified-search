import fs from 'fs';

import { ApolloServerErrorCode } from '@apollo/server/errors';
import { GraphQLError } from 'graphql';
import { describe, it, vi, beforeEach, afterEach, expect } from 'vitest';

import type {
  AccessibilityProfileType,
  OrderByDistanceParams,
  OrderByNameParams,
} from '../datasources/es/types.js';
import type { EsResults, GetCursor } from '../types.js';
import {
  getEsOffsetPaginationQuery,
  createCursor,
  escapeQuery,
  getTodayString,
  validateOrderByArguments,
  edgesFromEsResults,
  targetFieldLanguages,
  elasticLanguageFromGraphqlLanguage,
  findClosestEnvFile,
  findClosestEnvFileDir,
} from '../utils.js';

const UNSUPPORTED_ENV_FILE_PATHS = [
  '.env.local',
  'env.test',
  './.env.production',
  './.env.local',
  '../.env.development',
  '../../.env.test',
  '../../../.env.production',
] as const;

describe('utils', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('getEsOffsetPaginationQuery', () => {
    it('should error when first is not a positive number', () => {
      expect(() =>
        // @ts-expect-error testing invalid input, so types should fail
        getEsOffsetPaginationQuery({ first: 'first' })
      ).toThrowError();
      expect(() => getEsOffsetPaginationQuery({ first: -1 })).toThrowError();
    });

    describe('when after', () => {
      it('should return an offset that points to results after the cursor', () => {
        expect(
          getEsOffsetPaginationQuery({
            after: createCursor({
              offset: 5,
              meta: {},
            }),
          })
        ).toEqual({
          from: 5,
        });
      });

      describe('with first', () => {
        it('should only provide the first n elements', () => {
          expect(
            getEsOffsetPaginationQuery({
              first: 5,
              after: createCursor({
                offset: 5,
              }),
            })
          ).toEqual({
            from: 5,
            size: 5,
          });
        });
      });
    });
  });

  describe('escapeQuery', () => {
    it("should escape Elastic Search's special characters", () => {
      expect(
        escapeQuery('+ - = && || > < ! ( ) { } [ ] ^ " ~ * ? : \\ /')
      ).toEqual(
        '\\+ \\- \\= \\&& \\|| \\> \\< \\! \\( \\) \\{ \\} \\[ \\] \\^ \\" \\~ \\* \\? \\: \\\\ \\/'
      );
    });

    it("should not escape other than Elastic Search's special characters", () => {
      expect(
        escapeQuery(
          'Test / Another + read-only: "More <text> & Ääni, öylätti, Åland"'
        )
      ).toEqual(
        'Test \\/ Another \\+ read\\-only\\: \\"More \\<text\\> & Ääni, öylätti, Åland\\"'
      );
    });
  });

  describe('getTodayString', () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it('should return current date in ISO 8601 date format', () => {
      vi.setSystemTime(new Date('2025-08-29T12:34:56Z'));
      expect(getTodayString()).toStrictEqual('2025-08-29');
      vi.setSystemTime(new Date('2021-12-03'));
      expect(getTodayString()).toStrictEqual('2021-12-03');
    });
  });

  describe('validateOrderByArguments', () => {
    const exampleOrderByDistance = {
      latitude: 12.5,
      longitude: 23.75,
      order: 'ASCENDING',
    } as const satisfies OrderByDistanceParams;

    const exampleOrderByName = {
      order: 'ASCENDING',
    } as const satisfies OrderByNameParams;

    const exampleOrderByAccessibilityProfile =
      'visually_impaired' as const satisfies AccessibilityProfileType;

    it('should throw exception when arguments are ambiguous', () => {
      const ambiguousProps = [
        [
          exampleOrderByDistance,
          exampleOrderByName,
          exampleOrderByAccessibilityProfile,
        ],
        [exampleOrderByDistance, exampleOrderByName, undefined],
        [exampleOrderByDistance, undefined, exampleOrderByAccessibilityProfile],
        [undefined, exampleOrderByName, exampleOrderByAccessibilityProfile],
      ] as const;

      for (const [
        orderByDistance,
        orderByName,
        orderByAccessibilityProfile,
      ] of ambiguousProps) {
        expect(() =>
          validateOrderByArguments(
            orderByDistance,
            orderByName,
            orderByAccessibilityProfile
          )
        ).toThrowError(
          new GraphQLError(
            'Cannot use more than one orderBy parameter simultaneously',
            {
              extensions: {
                code: ApolloServerErrorCode.GRAPHQL_VALIDATION_FAILED,
              },
            }
          )
        );
      }
    });

    describe('unambiguous params', () => {
      it('should throw exception when orderByDistance is null', () => {
        expect(() => validateOrderByArguments(null)).toThrowError(
          new GraphQLError('"orderByDistance" cannot be null.', {
            extensions: {
              code: ApolloServerErrorCode.GRAPHQL_VALIDATION_FAILED,
            },
          })
        );
      });

      it('should throw exception when orderByName is null', () => {
        expect(() => validateOrderByArguments(undefined, null)).toThrowError(
          new GraphQLError('"orderByName" cannot be null.', {
            extensions: {
              code: ApolloServerErrorCode.GRAPHQL_VALIDATION_FAILED,
            },
          })
        );
      });

      it('should throw exception when orderByAccessibilityProfile is null', () => {
        expect(() =>
          validateOrderByArguments(undefined, undefined, null)
        ).toThrowError(
          new GraphQLError('"orderByAccessibilityProfile" cannot be null.', {
            extensions: {
              code: ApolloServerErrorCode.GRAPHQL_VALIDATION_FAILED,
            },
          })
        );
      });
    });
  });

  describe('edgesFromEsResults', () => {
    const exampleEsResults = {
      hits: {
        hits: [
          {
            _score: 1.5,
            _source: {
              name: 'Example 1',
              venue: { name: 'Test venue 1' },
            },
            _id: '1',
          },
          {
            _score: 1.0,
            _source: {
              name: 'Example 2',
              venue: { name: 'Test venue 2' },
            },
            _id: '2',
          },
        ],
        total: { value: 2 },
        max_score: 1.5,
      },
    } as const satisfies EsResults;

    const exampleGetCursor: GetCursor = (index: number) =>
      `testGetCursor:${index}`;

    it('should map results correctly', () => {
      const result = edgesFromEsResults(exampleEsResults, exampleGetCursor);
      expect(result).toStrictEqual([
        {
          cursor: 'testGetCursor:1',
          node: {
            _score: 1.5,
            venue: {
              venue: { name: 'Test venue 1' },
            },
          },
        },
        {
          cursor: 'testGetCursor:2',
          node: {
            _score: 1,
            venue: {
              venue: { name: 'Test venue 2' },
            },
          },
        },
      ]);
    });
  });

  describe('targetFieldLanguages', () => {
    it.each([
      ['field1', ['fi' as const], ['field1fi' as const]],
      ['field2', ['sv' as const], ['field2sv' as const]],
      ['TEST 123 field', ['en' as const], ['TEST 123 fielden' as const]],
      ['x', ['fi' as const, 'en' as const], ['xfi' as const, 'xen' as const]],
      ['abc', ['fi' as const, 'sv' as const, 'en' as const], ['abc*' as const]],
    ])(
      `targetFieldLanguages(%o, %o) == %o`,
      (field, languages, expectedResult) => {
        const result = targetFieldLanguages(field, languages);
        expect(result).toStrictEqual(expectedResult);
      }
    );
  });

  describe('elasticLanguageFromGraphqlLanguage', () => {
    it.each([
      [[], []],
      [['FINNISH'], ['fi']],
      [['SWEDISH'], ['sv']],
      [['ENGLISH'], ['en']],
      [
        ['FINNISH', 'SWEDISH'],
        ['fi', 'sv'],
      ],
      [
        ['FINNISH', 'ENGLISH'],
        ['fi', 'en'],
      ],
      [
        ['SWEDISH', 'ENGLISH'],
        ['sv', 'en'],
      ],
      [
        ['FINNISH', 'SWEDISH', 'ENGLISH'],
        ['fi', 'sv', 'en'],
      ],
      // Duplicates of valid languages
      [
        ['ENGLISH', 'SWEDISH', 'FINNISH', 'FINNISH', 'SWEDISH'],
        ['en', 'sv', 'fi', 'fi', 'sv'],
      ],
      // Only invalid languages and languages that have no mapping
      [['INVALID'], [undefined]],
      [
        ['INVALID', '123', 'ARABIC'],
        [undefined, undefined, undefined],
      ],
      // Mix of languages that have a mapping and some that don't
      [
        ['FINNISH', 'INVALID', 'ENGLISH', 'ARABIC', 'HINDI'],
        ['fi', undefined, 'en', undefined, undefined],
      ],
    ])(
      'elasticLanguageFromGraphqlLanguage(%o) == %o',
      (graphqlLanguages, expectedResult) => {
        const result = elasticLanguageFromGraphqlLanguage(graphqlLanguages);
        expect(result).toStrictEqual(expectedResult);
      }
    );
  });

  describe('findClosestEnvFile', () => {
    it('should return ./.env when found in current directory', () => {
      vi.spyOn(fs, 'existsSync').mockImplementation(
        (path) => path === './.env'
      );

      const result = findClosestEnvFile();

      expect(result).toBe('./.env');
      expect(fs.existsSync).toHaveBeenCalledWith('./.env');
    });

    it('should return ../.env when found in parent directory', () => {
      vi.spyOn(fs, 'existsSync').mockImplementation(
        (path) => path === '../.env'
      );

      const result = findClosestEnvFile();

      expect(result).toBe('../.env');
      expect(fs.existsSync).toHaveBeenCalledWith('./.env');
      expect(fs.existsSync).toHaveBeenCalledWith('../.env');
    });

    it('should return ../../.env when found 2 levels up', () => {
      vi.spyOn(fs, 'existsSync').mockImplementation(
        (path) => path === '../../.env'
      );

      const result = findClosestEnvFile();

      expect(result).toBe('../../.env');
      expect(fs.existsSync).toHaveBeenCalledWith('./.env');
      expect(fs.existsSync).toHaveBeenCalledWith('../.env');
      expect(fs.existsSync).toHaveBeenCalledWith('../../.env');
    });

    it('should return ../../../.env when found 3 levels up', () => {
      vi.spyOn(fs, 'existsSync').mockImplementation(
        (path) => path === '../../../.env'
      );

      const result = findClosestEnvFile();

      expect(result).toBe('../../../.env');
      expect(fs.existsSync).toHaveBeenCalledWith('./.env');
      expect(fs.existsSync).toHaveBeenCalledWith('../.env');
      expect(fs.existsSync).toHaveBeenCalledWith('../../.env');
      expect(fs.existsSync).toHaveBeenCalledWith('../../../.env');
    });

    it('should return null when .env file is out of the maximum search depth', () => {
      vi.spyOn(fs, 'existsSync').mockImplementation(
        (path) => path === '../../../../.env'
      );

      const result = findClosestEnvFile();

      expect(fs.existsSync).toHaveBeenCalledTimes(4); // Maximum search depth
      expect(result).toBe(null); // Not found within maximum search depth
      expect(fs.existsSync).toHaveBeenCalledWith('./.env');
      expect(fs.existsSync).toHaveBeenCalledWith('../.env');
      expect(fs.existsSync).toHaveBeenCalledWith('../../.env');
      expect(fs.existsSync).toHaveBeenCalledWith('../../../.env');
    });

    it('should return the closest .env file when multiple exist', () => {
      vi.spyOn(fs, 'existsSync').mockImplementation(
        (path) => path === '../.env' || path === '../../.env'
      );

      const result = findClosestEnvFile();

      expect(result).toBe('../.env');
      expect(fs.existsSync).toHaveBeenCalledTimes(2);
      expect(fs.existsSync).toHaveBeenCalledWith('./.env');
      expect(fs.existsSync).toHaveBeenCalledWith('../.env');
    });

    it.each(UNSUPPORTED_ENV_FILE_PATHS)(
      'should return null when only unsupported %s file is available',
      (envFilePath) => {
        vi.spyOn(fs, 'existsSync').mockImplementation(
          (path) => path === envFilePath
        );
        const result = findClosestEnvFile();

        expect(result).toBe(null);
      }
    );
  });

  describe('findClosestEnvFileDir', () => {
    it('should return "." when .env is found in current directory', () => {
      vi.spyOn(fs, 'existsSync').mockImplementation(
        (path) => path === './.env'
      );

      const result = findClosestEnvFileDir();

      expect(result).toBe('.');
    });

    it('should return ".." when .env is found in parent directory', () => {
      vi.spyOn(fs, 'existsSync').mockImplementation(
        (path) => path === '../.env'
      );

      const result = findClosestEnvFileDir();

      expect(result).toBe('..');
    });

    it('should return "../.." when .env is found 2 levels up', () => {
      vi.spyOn(fs, 'existsSync').mockImplementation(
        (path) => path === '../../.env'
      );

      const result = findClosestEnvFileDir();

      expect(result).toBe('../..');
    });

    it('should return "../../.." when .env is found 3 levels up', () => {
      vi.spyOn(fs, 'existsSync').mockImplementation(
        (path) => path === '../../../.env'
      );

      const result = findClosestEnvFileDir();

      expect(result).toBe('../../..');
    });

    it('should return null when .env file is out of the maximum search depth', () => {
      vi.spyOn(fs, 'existsSync').mockImplementation(
        (path) => path === '../../../../.env'
      );

      const result = findClosestEnvFileDir();

      expect(result).toBe(null); // Not found within maximum search depth
      expect(fs.existsSync).toHaveBeenCalledTimes(4); // Maximum search depth
    });

    it('should return the closest .env file directory when multiple exist', () => {
      vi.spyOn(fs, 'existsSync').mockImplementation(
        (path) => path === '../../.env' || path === '../../../.env'
      );

      const result = findClosestEnvFileDir();

      expect(result).toBe('../..');
      expect(fs.existsSync).toHaveBeenCalledTimes(3);
      expect(fs.existsSync).toHaveBeenCalledWith('./.env');
      expect(fs.existsSync).toHaveBeenCalledWith('../.env');
      expect(fs.existsSync).toHaveBeenCalledWith('../../.env');
    });

    it.each(UNSUPPORTED_ENV_FILE_PATHS)(
      'should return null when only unsupported %s file is available',
      (envFilePath) => {
        vi.spyOn(fs, 'existsSync').mockImplementation(
          (path) => path === envFilePath
        );
        const result = findClosestEnvFileDir();

        expect(result).toBe(null);
      }
    );
  });
});

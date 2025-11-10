import { describe, expect, it } from 'vitest';

import {
  MATCH_PHRASE_BOOST_MULTIPLIER,
  SEARCH_WEIGHT,
} from '../../constants.js';
import { queryBuilder } from '../queryBuilder.js';

describe('queryBuilder', () => {
  /**
   * Test single language simple case with varying parameters such as
   * language, ordering and text.
   *
   * Also tests how search weights/boosts are combined to form the final
   * search weight values.
   */
  it.each(['fi', 'sv', 'en'] as const)(
    'test single language simple case with varying parameters',
    (lang) => {
      for (const order of ['ASCENDING', 'DESCENDING'] as const) {
        for (const text of ['testing', 'Longer text 1234'] as const) {
          const params = {
            index: 'location' as const,
            languages: [lang],
            text,
            from: 20 as const,
            size: 10 as const,
            administrativeDivisionIds: ['admin_div_id' as const],
            orderByName: { order },
          };

          const expectedOrder =
            params.orderByName.order === 'ASCENDING' ? 'asc' : 'desc';

          const result = queryBuilder(params);

          expect(result).toStrictEqual({
            from: params.from,
            query: {
              bool: {
                filter: [
                  {
                    bool: {
                      should: [
                        {
                          term: {
                            'venue.location.administrativeDivisions.id.keyword':
                              params.administrativeDivisionIds[0],
                          },
                        },
                      ],
                    },
                  },
                ],
                minimum_should_match: 1,
                should: [
                  {
                    match_bool_prefix: {
                      [`venue.description.${lang}`]: {
                        boost: SEARCH_WEIGHT.normal,
                        fuzziness: 'AUTO',
                        operator: 'or',
                        query: params.text,
                      },
                    },
                  },
                  {
                    match_bool_prefix: {
                      [`venue.name.${lang}`]: {
                        boost: SEARCH_WEIGHT.veryHigh,
                        fuzziness: 'AUTO',
                        operator: 'or',
                        query: params.text,
                      },
                    },
                  },
                  {
                    match_phrase: {
                      [`venue.description.${lang}`]: {
                        boost:
                          SEARCH_WEIGHT.normal * MATCH_PHRASE_BOOST_MULTIPLIER,
                        query: params.text,
                      },
                    },
                  },
                  {
                    match_phrase: {
                      [`venue.name.${lang}`]: {
                        boost:
                          SEARCH_WEIGHT.veryHigh *
                          MATCH_PHRASE_BOOST_MULTIPLIER,
                        query: params.text,
                      },
                    },
                  },
                  {
                    multi_match: {
                      fields: [
                        `links.raw_data.ontologyword_ids_enriched.extra_searchwords_${lang}`,
                        `links.raw_data.ontologyword_ids_enriched.ontologyword_${lang}`,
                        `links.raw_data.ontologytree_ids_enriched.name_${lang}`,
                        `links.raw_data.ontologytree_ids_enriched.extra_searchwords_${lang}`,
                      ],
                      query: params.text,
                    },
                  },
                ],
              },
            },
            size: params.size,
            sort: [
              {
                [`venue.name.${lang}.keyword`]: {
                  missing: '_last',
                  order: expectedOrder,
                },
              },
            ],
          });
        }
      }
    }
  );
});

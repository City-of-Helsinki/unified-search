# GraphQL search API (a.k.a. `graphql` app)

GraphQL search API on top of Elasticsearch to provide high level interface
for end users of [Unified Search](https://github.com/City-of-Helsinki/unified-search).

**Table of Contents**

<!-- DON'T EDIT THE TOC SECTION, INSTEAD RE-RUN md-toc TO UPDATE IT -->
<!--TOC-->

- [Requirements](#requirements)
- [Running](#running)
  - [With Docker & Docker compose](#with-docker--docker-compose)
  - [Without Docker](#without-docker)
- [Environments](#environments)
- [GraphQL search API documentation](#graphql-search-api-documentation)
  - [administrativeDivisions query](#administrativedivisions-query)
  - [ontologyTree query](#ontologytree-query)
  - [ontologyWords query](#ontologywords-query)
  - [unifiedSearch query](#unifiedsearch-query)
    - [Required parameters](#required-parameters)
    - [Optional filter parameters](#optional-filter-parameters)
    - [Optional sorting parameters](#optional-sorting-parameters)
    - [Optional pagination parameters](#optional-pagination-parameters)
    - [Special case for ontology parameter](#special-case-for-ontology-parameter)
    - [Special case for text parameter of \*](#special-case-for-text-parameter-of-)
    - [Weighting of search results](#weighting-of-search-results)
  - [unifiedSearchCompletionSuggestions query](#unifiedsearchcompletionsuggestions-query)
- [How the search works](#how-the-search-works)
  - [Data analysis & indexing](#data-analysis--indexing)
  - [Matching the text parameter](#matching-the-text-parameter)
    - [1. Using match_bool_prefix query](#1-using-match_bool_prefix-query)
    - [2. Using match_phrase query](#2-using-match_phrase-query)
    - [3. Using multi_match query](#3-using-multi_match-query)
- [Additional example GraphQL queries](#additional-example-graphql-queries)
  - [Pagination and scores](#pagination-and-scores)
  - [Raw data for debugging purposes](#raw-data-for-debugging-purposes)
- [Elasticsearch queries](#elasticsearch-queries)
  - [Date ranges](#date-ranges)
- [Code linting & formatting](#code-linting--formatting)
- [Pre-commit hooks](#pre-commit-hooks)

<!--TOC-->

## Requirements

Requirements defined & provided by [Dockerfile](./Dockerfile):

- Node.js 22
- Latest Yarn v1

## Running

### With Docker & Docker compose

Because Docker compose handles more than just this app,
its use is described in the [repository root README](../README.md).

### Without Docker

1. Install [requirements](#requirements)
   - Node.js using e.g. [nvm](https://github.com/nvm-sh/nvm) / [nvm-windows](https://github.com/coreybutler/nvm-windows)
   - Yarn v1 using e.g. [Yarn installation guide](https://classic.yarnpkg.com/lang/en/docs/install/)
2. Run `yarn start` for development, or `yarn build` & `yarn serve` for production build.

## Environments

Where is the GraphQL API running?

Based on info from [kuva-unified-search](https://dev.azure.com/City-of-Helsinki/kuva-unified-search) Azure DevOps project:

- Review per PR (e.g. PR #321): https://kuva-unified-search-pr321.api.dev.hel.ninja/search
- Development: https://kuva-unified-search.api.dev.hel.ninja/search
- Testing: https://kuva-unified-search.api.test.hel.ninja/search
- Staging: https://kuva-unified-search.api.stage.hel.ninja/search
- Production: https://kuva-unified-search.api.hel.fi/search

## GraphQL search API documentation

The GraphQL search API's documentation & client is available at `/search` endpoint
(as long as Apollo Sandbox has been enabled with `ENABLE_APOLLO_SANDBOX=true`):

- Locally: http://localhost:4000/search
- In deployed environments, see [Environments](#environments)

### administrativeDivisions query

**Lists administrative divisions** in Finland or Helsinki:

| helsinkiCommonOnly param | Used Elasticsearch index                  | Query result                         |
| ------------------------ | ----------------------------------------- | ------------------------------------ |
| `false` or not provided  | `administrative_division`                 | Administrative divisions in Finland  |
| `true`                   | `helsinki_common_administrative_division` | Administrative divisions in Helsinki |

The Helsinki divisions are used in practice for dropdown populating (e.g. in https://kultus.hel.fi/ "Places" dropdown),
and the Finland listing is not used at all.

**Example query**:

NOTE: `ingest_data administrative_division` must have been run for this to work.

Show all Helsinki's administrative divisions:

```graphql
query {
  administrativeDivisions(helsinkiCommonOnly: true) {
    id
    type
    municipality
    name {
      fi
      sv
      en
    }
  }
}
```

<details>

<summary>
Partial output of the example query (Click to expand)
</summary>

```json
{
  "data": {
    "administrativeDivisions": [
      {
        "id": "ocd-division/country:fi/kunta:helsinki/kaupunginosa:kruununhaka",
        "type": "neighborhood",
        "municipality": "Helsinki",
        "name": {
          "fi": "Kruununhaka",
          "sv": "Kronohagen",
          "en": null
        }
      },
      ...
      {
        "id": "ocd-division/country:fi/kunta:helsinki/osa-alue:puroniitty",
        "type": "sub_district",
        "municipality": "Helsinki",
        "name": {
          "fi": "Puroniitty",
          "sv": "Bäckängen",
          "en": null
        }
      }
    ]
  }
}
```

</details>

### ontologyTree query

**Lists ontology tree nodes** from `ontology_tree` Elasticsearch index:

| rootId param | leavesOnly param        | Query result                | Pseudocode filter                                                  |
| ------------ | ----------------------- | --------------------------- | ------------------------------------------------------------------ |
| Not provided | `false` or not provided | All nodes                   | \*                                                                 |
| Not provided | `true`                  | Leaves                      | NOT exists(childIds)                                               |
| An ID value  | `false` or not provided | Subtree under given root ID | (rootId IN ancestorIds OR \_id == rootId)                          |
| An ID value  | `true`                  | Leaves under given root ID  | (rootId IN ancestorIds OR \_id == rootId) AND NOT exists(childIds) |

**Example query**:

NOTE: `ingest_data ontology_tree` must have been run for this to work.

Show ontology tree for root ID 551 i.e. "Sports and physical exercise":

```graphql
query {
  ontologyTree(rootId: 551) {
    id
    name {
      fi
      sv
      en
    }
    childIds
    ancestorIds
  }
}
```

<details>

<summary>
Partial output of the example query (Click to expand)
</summary>

```json
{
  "data": {
    "ontologyTree": [
      {
        "id": "2357",
        "name": {
          "fi": "Padelhalli",
          "sv": "Padelhall",
          "en": "Padel hall"
        },
        "childIds": [],
        "ancestorIds": ["614", "601", "551", "1403"]
      },
      ...
      {
        "id": "617",
        "name": {
          "fi": "Monitoimihalli / areena",
          "sv": "Allaktivitetshall/multiarena",
          "en": "Multipurpose hall/arena"
        },
        "childIds": [],
        "ancestorIds": ["614", "601", "551", "1403"]
      }
    ]
  }
}
```

</details>

### ontologyWords query

**Lists ontology words** from `ontology_word` Elasticsearch index:

| ids param          | Query result                  | Pseudocode filter |
| ------------------ | ----------------------------- | ----------------- |
| Not provided       | All ontology words            | \*                |
| Array of ID values | Ontology words with given IDs | \_id in ids       |

**Example query**:

NOTE: `ingest_data ontology_word` must have been run for this to work.

Show all ontology words:

```graphql
query {
  ontologyWords {
    id
    label {
      fi
      sv
      en
    }
  }
}
```

<details>

<summary>
Partial output of the example query (Click to expand)
</summary>

```json
{
  "data": {
    "ontologyWords": [
      {
        "id": "230",
        "label": {
          "fi": "järjestötoiminta (osallisuutta lisäävä toiminta)",
          "sv": "organisationsverksamhet (verksamhet som ökar delaktigheten)",
          "en": "organisational activities (activities that increase inclusion)"
        }
      },
      ...
      {
        "id": "1103",
        "label": {
          "fi": "huoltorakennukset",
          "sv": "servicebyggnader",
          "en": "service buildings"
        }
      }
    ]
  }
}
```

</details>

### unifiedSearch query

**Fuzzy free text venue search** from `location` Elasticsearch index
with various filters, sorting options and pagination.

**Example query**:

NOTE: `ingest_data location` must have been run for this to work.

This searches the `location` index for the free text "koira" (dog in Finnish):

```graphql
query {
  unifiedSearch(index: location, text: "koira", languages: FINNISH) {
    edges {
      cursor
      node {
        venue {
          name {
            fi
          }
          description {
            fi
          }
        }
      }
    }
  }
}
```

<details>

<summary>
Partial output of the example query (Click to expand)
</summary>

```json
{
  "data": {
    "unifiedSearch": {
      "edges": [
        {
          "cursor": "eyJvZmZzZXQiOjF9",
          "node": {
            "venue": {
              "name": {
                "fi": "Saarnilaakson koira-aitaus"
              },
              "description": {
                "fi": "Saarnilaakson koira-aitaus on yksiosainen 3620 m2 koira-aitaus, jossa on metsää ja korkeuseroja. Pysäköinti 300 m päässä."
              }
            }
          }
        },
        ...
        {
          "cursor": "eyJvZmZzZXQiOjEwfQ==",
          "node": {
            "venue": {
              "name": {
                "fi": "Koira-aitaus Krakanpuisto"
              },
              "description": {
                "fi": "Krakanpuistossa on kaksi koira-aitausta, joissa on agilityvälineitä sekä pienille että isoille koirille."
              }
            }
          }
        }
      ]
    }
  }
}
```

</details>

#### Required parameters

- `text`: User search input
  - Matched using full text search queries, see [how the search works](#how-the-search-works) for details.

#### Optional filter parameters

| Filter parameter           | Description                                                                                                                                                |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| administrativeDivisionIds  | Filter with given administrative division IDs (see [administrativeDivisions query](#administrativedivisions-query)])                                       |
| languages                  | Filter the source fields to only the given languages' versions (default fi/sv/en)                                                                          |
| mustHaveReservableResource | Filter to show only venues that have at least one reservable resource (`false` or `true`)                                                                  |
| ontology                   | Overriding filter to match based on ontology only, see [Special case for ontology parameter](#special-case-for-ontology-parameter)                         |
| ontologyTreeIdOrSets       | Filter to match at least one ontology tree ID from each list (see [ontologyTree query](#ontologytree-query))                                               |
| ontologyWordIdOrSets       | Filter to match at least one ontology word ID from each list (see [ontologyWords query](#ontologywords-query))                                             |
| openAt                     | Filter to show only venues open at the given moment, ISO 8601 datetime or e.g. "now+3h"                                                                    |
| providerTypes              | Filter to match any of the given provider types, e.g. association or municipality (see [enum ProviderType](./src/schemas/location.ts))                     |
| serviceOwnerTypes          | Filter to match any of the given service owner types, e.g. municipal service or purchased service (see [enum ServiceOwnerType](./src/schemas/location.ts)) |
| targetGroups               | Filter to match any of the given target groups, e.g. youth or elderly people (see [enum TargetGroup](./src/schemas/location.ts))                           |

#### Optional sorting parameters

| Sorting parameter           | Description                                                                                  |
| --------------------------- | -------------------------------------------------------------------------------------------- |
| orderByDistance             | Sort results by distance from given coordinates (nearest first)                              |
| orderByName                 | Sort results by name in the first language in `languages` parameter (alphabetical order)     |
| orderByAccessibilityProfile | Sort results by given accessibility profile's shortcoming count (i.e. 0, 1, ..., N, unknown) |

#### Optional pagination parameters

| Pagination parameter | Description                        |
| -------------------- | ---------------------------------- |
| after                | Cursor after which to show results |
| first                | Number of results to show          |

#### Special case for ontology parameter

The `ontology` parameter is a special case and only applied if `text` parameter is not `*`.
It can be used to filter with given ontology words (see [ontologyWords query](#ontologywords-query))
and using it will override the query to only search the following fields in `location` index
(where `{lang}` is `fi`/`sv`/`en`, depending on `languages` parameter):

- `links.raw_data.ontologyword_ids_enriched.extra_searchwords_{lang}`
- `links.raw_data.ontologyword_ids_enriched.ontologyword_{lang}`
- `links.raw_data.ontologytree_ids_enriched.name_{lang}`
- `links.raw_data.ontologytree_ids_enriched.extra_searchwords_{lang}`

The ontology words will be matched to the above fields using [multi_match query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-multi-match-query)
with the default [best_fields type](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-multi-match-query#type-best-fields)
(i.e. "Finds documents which match any field, but uses the \_score from the best field").

So, basically the ontology word filtering special case will find locations/venues that match the
given ontology word in any of the given languages in any of the above fields, and apply the optional
filtering, sorting and pagination parameters.

#### Special case for text parameter of \*

When `text` parameter is `*`, it means "match all documents" (i.e. no fuzzy matching) and
it uses [query_string query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-query-string-query)
with `query` of `*`. The optional filtering, sorting and pagination parameters are applied
except for the `ontology` parameter.

#### Weighting of search results

To give more importance to venue name and description fields in `location` index's
search results, the search results are weighted in the normal search cases
(i.e. when `text` parameter is not `*` and `ontology` parameter is not used).

Here are the location/venue search's used weights:

| Field       | Single word match | Phrase match (2x single match) |
| ----------- | ----------------- | ------------------------------ |
| name        | 3x                | 6x                             |
| description | 1x                | 2x                             |

So this makes it so that phrase matches (e.g. "art museum") in `name` field
are weighted highest (6x), followed by single word matches (e.g. "art" or "museum")
in `name` (3x), followed by phrase matches in `description` (2x), and finally the
single word matches in `description` (1x).

Given the above, location/venue search prioritizes the search matches in this order:

1. `name` field phrase match
2. `name` field single word match
3. `description` field phrase match
4. `description` field single word match

The weights are defined in [constants files](./src/datasources/es/api/getQueryResults/constants.ts).

### unifiedSearchCompletionSuggestions query

**Exact prefix matching** unique ontology word **suggestions** from `location` index.

Uses Elasticsearch's [completion suggester](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-suggesters-completion.html).

Query parameters:

- `prefix`: Text prefix to match suggestions against
- `languages`: Languages to provide suggestions for (default fi/sv/en)
- `size`: Maximum number of suggestions to return (default 5)
- `index`: Elasticsearch index to get suggestions from (default `location`, the only supported index)

**Example query**:

NOTE: `ingest_data location` must have been run for this to work.

```graphql
query {
  unifiedSearchCompletionSuggestions(
    prefix: "ki"
    languages: FINNISH
    index: location
  ) {
    suggestions {
      label
    }
  }
}
```

<details>

<summary>
Output of the example query (Click to expand)
</summary>

```json
{
  "data": {
    "unifiedSearchCompletionSuggestions": {
      "suggestions": [
        { "label": "Kieliohjelma" },
        { "label": "Kierrättäminen" },
        { "label": "kielikylpy englanti" },
        { "label": "kielikylpy ruotsi" },
        { "label": "kielikylpy suomi-ruotsi (perusopetus)" }
      ]
    }
  }
}
```

</details>

## How the search works

Disclaimer:

    This is a best effort attempt to describe how the search works.

    Because of the complexity of Elasticsearch and its documentation it is not
    guaranteed that all details are exact.

    You can verify with the following sources (From abstract to concrete):
    - Elasticsearch's official documentation ("what it is supposed to do")
    - Elasticsearch's source code ("how it is implemented")
    - By running queries in Elasticsearch Dev Tools ("how it behaves on I/O level")
    - By running and debugging the code ("how it really works")

Here is an overview of how the free text search's normal case works
(i.e. when `text` parameter is not `*` and `ontology` parameter is not used)
in [`unifiedSearch` query](#unifiedsearch-query).

### Data analysis & indexing

When indexing data in Elasticsearch language specific analyzers are used for indexing the localized
venue `name` and `description` fields only:

- [finnish analyzer](https://www.elastic.co/docs/reference/text-analysis/analysis-lang-analyzer#finnish-analyzer) for Finnish language
- [swedish analyzer](https://www.elastic.co/docs/reference/text-analysis/analysis-lang-analyzer#swedish-analyzer) for Swedish language
- [english analyzer](https://www.elastic.co/docs/reference/text-analysis/analysis-lang-analyzer#english-analyzer) for English language

According to [stemmer token filter documentation](https://www.elastic.co/docs/reference/text-analysis/analysis-stemmer-tokenfilter)
the used language-dependent stemming algorithms are:

- `finnish`: [Finnish stemming algorithm](https://snowballstem.org/algorithms/finnish/stemmer.html)
- `swedish`: [Swedish stemming algorithm](https://snowballstem.org/algorithms/swedish/stemmer.html)
- `english`: [The Porter stemming algorithm](https://snowballstem.org/algorithms/porter/stemmer.html)

For general level info about the text analysis, see Elasticsearch docs for an
[overview of the text analysis in Elasticsearch](https://www.elastic.co/docs/manage-data/data-store/text-analysis).

For non-fuzzy sorting the venue `name` and `description` fields are also indexed
as keyword fields with `.keyword` suffix, e.g. `venue.name.fi.keyword`, but **only** if
the field is not over 256 characters in length. If it is, then the keyword version is not
indexed at all.

### Matching the text parameter

In normal cases `text` parameter is matched to fields (where `{lang}` is `fi`/`sv`/`en`,
depending on `languages` parameter):

- `venue.name.{lang}`
- `venue.description.{lang}`

using the weights described in [Weighting of search results](#weighting-of-search-results) section
to boost the importance of e.g. matches in venue name over matches in venue description.

The matching is done with three types of queries combined i.e. so that their match scores
are all added together (more an entry matches any of these, higher its score, and thus higher its position
in the search results):

#### 1. Using match_bool_prefix query

The [match_bool_prefix query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-match-bool-prefix-query)
with [fuzziness](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-match-query#query-dsl-match-query-fuzziness)
set to [AUTO](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/common-options#fuzziness) is
used as one of the queries for matching `text` parameter.

AUTO fuzziness (with `fuzzy_transpositions` i.e. swaps of adjacent characters allowed by default) means according to string length:

- `0–2`: must match exactly
- `3–5`: allow one edit (i.e. deletion/insertion/substitution/swap of adjacent characters), e.g. "cat" → "at", "coat", "cut" or "act"
- `>5`: allow two edits, e.g. "elephant" → "oliphant" or "elefant"

What `match_bool_prefix` query here does it analyzes `text` parameter using a language specific analyzer based
on the queried field (e.g. finnish analyzer with `venue.name.fi` and english analyzer with `venue.description.en`),
splits it into terms, makes [bool queries](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-bool-query)
from all but the last term, and a [prefix query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-prefix-query)
from the last term. What this means is that fuzzy matching only affects the terms before the last term, and the last
term is matched exactly as a prefix.

As an example "edeltäjien innostuminen ja" would be split to terms "edeltäj" and "innostumin"
(according to the [Finnish stemming algorithm](https://snowballstem.org/algorithms/finnish/stemmer.html)),
and those would be fuzzy matched according to their string lengths (i.e. two edits allowed for both),
and the last term would be the exact prefix matched "ja", which would match e.g. "ja", "jatkuu" or "japanissa".

#### 2. Using match_phrase query

The [match_phrase query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-match-query-phrase)
with default `slop` of zero (i.e. tokens must match at their exact positions) is used as one of the queries
for matching `text` parameter. It uses phrase matching to give higher scores to results that match the whole
phrase in the correct order.

For an overview of phrase matching, see [Phrase Queries blog post](https://www.elastic.co/blog/phrase-queries-a-world-without-stopwords).

Here `match_phrase` query analyzes `text` parameter using a language specific analyzer based on the queried
field, and makes a `phrase` query out of the analyzed text (Elasticsearch documentation does not explain what
a `phrase` query is, but for more details see
[MatchPhraseQueryBuilder class](https://github.com/elastic/elasticsearch/blob/v9.1.3/server/src/main/java/org/elasticsearch/index/query/MatchPhraseQueryBuilder.java)).

So, most likely e.g. "edeltäjien innostuminen ja" would be split to terms "edeltäj" and "innostumin"
(according to the [Finnish stemming algorithm](https://snowballstem.org/algorithms/finnish/stemmer.html)) and likely "ja" (as it is such a simple word),
and those would be matched exactly at their exact positions against the queried field's analyzed tokens.

What this means, is that this query allows for word variations according to each language, and after
that requires the whole modified phrase to match exactly in the correct order. As an example,
"edeltäjä innostuneelle" and "edeltäjästään innostuneiden" would match, as both would be stemmed to
"edeltäj innostun" i.e. the same exact phrase.

#### 3. Using multi_match query

The [multi_match query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-multi-match-query)
with the default [best_fields type](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-multi-match-query#type-best-fields)
(i.e. "Finds documents which match any field, but uses the \_score from the best field.") is used as one of
the queries for matching `text` parameter.

This does relatively the same as using `ontology` parameter, although not exactly using the same query types.
The `multi_match` query is used for matching `text` against ontology word & tree names and extra search words
(See [Special case for ontology parameter](#special-case-for-ontology-parameter) section for the used fields).

So, this is used to add ontology based matching to the venue search's normal case.

## Additional example GraphQL queries

It is recommended to use a GraphQL client for sending queries.

You can also use the Apollo Sandbox GraphQL client, if you have it enabled with
`ENABLE_APOLLO_SANDBOX=true` in your `.env` file, locally at http://localhost:4000/search

### Pagination and scores

NOTE: `ingest_data location` must have been run for this to work.

```graphql
query {
  unifiedSearch(text: "koira", index: location) {
    count
    max_score
    pageInfo {
      startCursor
      endCursor
      hasNextPage
      hasPreviousPage
    }
    edges {
      cursor
      node {
        venue {
          name {
            fi
            sv
            en
          }
          openingHours {
            url
            is_open_now_url
          }
          location {
            url {
              fi
            }
          }
        }
        _score
      }
    }
  }
}
```

### Raw data for debugging purposes

NOTE: `ingest_data location` must have been run for this to work.

```graphql
query {
  unifiedSearch(text: "koira", index: location, first: 3) {
    count
    max_score
    edges {
      node {
        venue {
          name {
            fi
            sv
            en
          }
        }
        _score
      }
    }
    es_results {
      took
      hits {
        max_score
        total {
          value
        }
        hits {
          _index
          _source {
            data
          }
        }
      }
    }
  }
}
```

## Elasticsearch queries

You can run these queries [locally in Elasticsearch Dev Tools](http://localhost:5601/app/dev_tools#/console).

### Date ranges

Date can be used in queries assuming mapping type is correct (`date` in ES, `datetime.datetime` in Python):

Get documents created in the last 2 minutes:

```elasticsearch
GET /location/_search
{
  "query": {
    "range": {
      "venue.meta.createdAt": {
        "gte": "now-2m/m"
      }
    }
  }
}
```

Related Elasticsearch documentation:

- [Elasticsearch Date Math](https://www.elastic.co/guide/en/elasticsearch/reference/current/common-options.html#date-math)
- [Using the range query with date fields](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-range-query.html#ranges-on-dates)

## Code linting & formatting

This project uses ESLint and prettier for JavaScript/TypeScript code linting and formatting.

## Pre-commit hooks

Because [pre-commit](https://pre-commit.com/) does not support monorepos, it must be configured at repository root.

For this reason, see [repository root README.md](../README.md#pre-commit-hooks) for how to set up pre-commit hooks.

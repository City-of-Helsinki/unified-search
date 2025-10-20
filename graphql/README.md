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
- [Weighting of search results](#weighting-of-search-results)
- [Used Elasticsearch queries and algorithms](#used-elasticsearch-queries-and-algorithms)
  - [Full-text search queries](#full-text-search-queries)
    - [match_bool_prefix](#match_bool_prefix)
    - [match_phrase](#match_phrase)
    - [multi_match](#multi_match)
    - [query_string](#query_string)
  - [Filtering queries](#filtering-queries)
    - [term](#term)
    - [exists](#exists)
  - [Query composition](#query-composition)
    - [bool query](#bool-query)
  - [Autocomplete](#autocomplete)
    - [Completion suggester](#completion-suggester)
- [Example GraphQL queries](#example-graphql-queries)
  - [Administrative divisions query](#administrative-divisions-query)
  - [Free text search - location index](#free-text-search---location-index)
  - [Pagination and scores](#pagination-and-scores)
  - [Raw data for debugging purposes](#raw-data-for-debugging-purposes)
  - [Suggestions for text completion](#suggestions-for-text-completion)
  - [Ontology tree query](#ontology-tree-query)
  - [Ontology words query](#ontology-words-query)
- [Example Elasticsearch queries](#example-elasticsearch-queries)
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

The GraphQL search API's documentation is available at `/search` endpoint
(as long as Apollo Sandbox has been enabled with `ENABLE_APOLLO_SANDBOX=true`):
- Locally: http://localhost:4000/search
- In deployed environments, see [Environments](#environments)

## Weighting of search results

To give more importance to certain fields in search results,
GraphQL search API's search results are weighted.

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

## Used Elasticsearch queries and algorithms

The GraphQL search API uses various Elasticsearch query types and features. This section documents which queries are used and where they are constructed in the codebase.

### Full-text search queries

#### match_bool_prefix

The [match_bool_prefix query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-bool-prefix-query.html) is an Elasticsearch query type that analyzes text and constructs a [bool query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html) from the analyzed terms, with the final term treated as a prefix.

**Parameters used in our implementation** ([searchWithBoolPrefix](./src/datasources/es/api/getQueryResults/utils/getDefaultBoolQuery.ts)):
- `operator: "or"`
  - Documents matching any term are returned (see [operator parameter](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-bool-prefix-query.html#match-bool-prefix-query-params))
- `fuzziness: "AUTO"`
  - Allows fuzzy matching based on term length (see [fuzziness parameter](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-bool-prefix-query.html#match-bool-prefix-query-params))
- `boost`
  - Set directly to the base boost weight from [SEARCH_WEIGHT constants](./src/datasources/es/api/getQueryResults/constants.ts)

**Fuzziness behavior:**

The `AUTO` [fuzziness setting](https://www.elastic.co/guide/en/elasticsearch/reference/current/common-options.html#fuzziness) generates an edit distance based on term length:
- 0-2 characters: 0 edit distance (exact match required)
- 3-5 characters: 1 edit distance allowed
- 6+ characters: 2 edit distances allowed

**Fields searched:**

As defined in [searchFieldsBoostMapping](./src/datasources/es/api/getQueryResults/constants.ts):
- `venue.name.{language}` (boost: SEARCH_WEIGHT.veryHigh = 3)
- `venue.description.{language}` (boost: SEARCH_WEIGHT.normal = 1)

#### match_phrase

The [match_phrase query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-query-phrase.html) is an Elasticsearch query type that analyzes text and matches documents containing the exact phrase in the specified order.

**Parameters used in our implementation** ([searchWithPhrase](./src/datasources/es/api/getQueryResults/utils/getDefaultBoolQuery.ts)):
- `boost`
  - Calculated as: base boost weight × [MATCH_PHRASE_BOOST_MULTIPLIER](./src/datasources/es/api/getQueryResults/constants.ts) (which equals 2)

**Fields searched:**

As defined in [searchFieldsBoostMapping](./src/datasources/es/api/getQueryResults/constants.ts):
- `venue.name.{language}` (base boost: 3, final boost: 3 × 2 = 6)
- `venue.description.{language}` (base boost: 1, final boost: 1 × 2 = 2)

Per [Elasticsearch documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-query-phrase.html), phrase queries analyze the text and create a phrase query out of the analyzed text, matching documents where the terms appear in the same order.

#### multi_match

The [multi_match query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-multi-match-query.html) is an Elasticsearch query type that runs the same query across multiple fields.

**Parameters used in our implementation** ([getOntologyMatchers](./src/datasources/es/api/getQueryResults/utils/getOntologyQuery.ts)):
- `fields`
  - Array of [ontology fields](./src/datasources/es/api/getQueryResults/utils/getOntologyFields.ts) to search

**Fields searched:**

As defined in [getOntologyFields](./src/datasources/es/api/getQueryResults/utils/getOntologyFields.ts):
- `links.raw_data.ontologyword_ids_enriched.extra_searchwords_{language}`
- `links.raw_data.ontologyword_ids_enriched.ontologyword_{language}`
- `links.raw_data.ontologytree_ids_enriched.name_{language}`
- `links.raw_data.ontologytree_ids_enriched.extra_searchwords_{language}`

#### query_string

The [query_string query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html) is an Elasticsearch query type that parses and executes queries using [query string syntax](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#query-string-syntax).

**Usage in our implementation:**
- Applied in [createQuery](./src/datasources/es/api/getQueryResults/utils/createQuery.ts) only when the search text parameter equals [`*`](./src/datasources/es/constants.ts),
which is a **deprecated** "search all" functionality.

### Filtering queries

#### term

The [term query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-term-query.html) is an Elasticsearch query type that returns documents containing an exact term in a field. Per Elasticsearch documentation: "Avoid using the term query for text fields" - the term query is designed for exact matching on keyword, numeric, date, or boolean fields.

**Usage in our implementation:**

Applied in [buildArrayFilter](./src/datasources/es/utils.ts) (which wraps term queries in a bool query with should clause) and directly in [filterQuery](./src/datasources/es/api/getQueryResults/utils/filterQuery.ts) for:
- Administrative division IDs (`venue.location.administrativeDivisions.id.keyword`)
- Ontology tree IDs (`links.raw_data.ontologytree_ids_enriched.id`)
- Ontology word IDs (`links.raw_data.ontologyword_ids_enriched.id`)
- Provider types (`venue.serviceOwner.providerType.keyword`)
- Service owner types (`venue.serviceOwner.type.keyword`)
- Target groups (`venue.targetGroups.keyword`)
- Opening hours datetime (`venue.openingHours.openRanges`)
- Reservation availability (`venue.reservation.reservable`)

#### exists

The [exists query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-exists-query.html) is an Elasticsearch query type that returns documents where a specified field has any non-null value.

**Usage in our implementation:**
- Applied in [buildMustHaveReservableResourceFilter](./src/datasources/es/api/getQueryResults/utils/filterQuery.ts) to check for:
  - External reservation URL field (`venue.reservation.externalReservationUrl`)

Per the code implementation, this is combined with a term query in a bool query with should clause to find venues that are either directly reservable OR have an external reservation URL.

### Query composition

#### bool query

The [bool query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html) is an Elasticsearch query type that combines multiple query clauses using boolean logic. It supports four occurrence types: `must`, `filter`, `should`, and `must_not`.

**Usage in our implementation:**

Constructed in [getDefaultBoolQuery](./src/datasources/es/api/getQueryResults/utils/getDefaultBoolQuery.ts) with the following clauses:

- **`should` clause**
  - Contains match_bool_prefix, match_phrase, and multi_match queries. Per [Elasticsearch documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html#score-bool-filter), when there is no `must` or `filter` clause, at least one `should` clause must match (unless `minimum_should_match` is set differently). Documents matching multiple should clauses receive higher scores.
- **`filter` clause**
  - Added by [filterQuery](./src/datasources/es/api/getQueryResults/utils/filterQuery.ts) when filters are provided. Contains term and exists queries. Per [Elasticsearch documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html#score-bool-filter): "The clause (query) must appear in matching documents. However unlike must the score of the query will be ignored."
- **`minimum_should_match: 1`**
  - Set when filters are applied. Per [Elasticsearch documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html#bool-min-should-match), this parameter "specifies the number or percentage of should clauses returned documents must match."

**Query structure as constructed in [getDefaultBoolQuery](./src/datasources/es/api/getQueryResults/utils/getDefaultBoolQuery.ts):**
```json
{
  "query": {
    "bool": {
      "should": [
        /* match_bool_prefix queries */,
        /* match_phrase queries */,
        /* multi_match queries */
      ],
      "filter": [
        /* term queries */,
        /* exists queries */
      ],
      "minimum_should_match": 1
    }
  }
}
```

### Autocomplete

#### Completion suggester

The [completion suggester](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-suggesters.html#completion-suggester) is an Elasticsearch feature that provides auto-complete/search-as-you-type functionality. Per [Elasticsearch documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-suggesters.html#completion-suggester): "The completion suggester is a so-called prefix suggester. It does not do spell correction like the term or phrase suggesters but allows basic fuzzy options."

**Parameters used in our implementation** ([makeSuggestionsQuery](./src/datasources/es/api/getQueryResults/utils/makeSuggestionsQuery.ts)):
- `field: "suggest"` - The field containing completion data
- `skip_duplicates: true` - Per [Elasticsearch documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-suggesters.html#completion-suggester), "whether duplicate suggestions should be filtered out"
- `size` - Maximum number of suggestions to return
- `contexts.language` - Context filter to return suggestions for specific languages

**GraphQL API integration:**

The completion suggester is called via [ElasticSearchAPI.getSuggestions](./src/datasources/es/index.ts), which is invoked by the [unifiedSearchCompletionSuggestionsResolver](./src/resolvers/query/unifiedSearchCompletionSuggestionsResolver.ts). This resolver is exposed as the [`unifiedSearchCompletionSuggestions` GraphQL query](./src/schemas/query.ts) in the [query resolvers](./src/resolvers/query/getQueryResolvers.ts).

## Example GraphQL queries

It is recommended to use a GraphQL client for sending queries.

You can also use the Apollo Sandbox GraphQL client, if you have it enabled with
`ENABLE_APOLLO_SANDBOX=true` in your `.env` file, locally at http://localhost:4000/search

### Administrative divisions query

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

### Free text search - location index

NOTE: `ingest_data location` must have been run for this to work.

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

### Suggestions for text completion

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

### Ontology tree query

NOTE: `ingest_data ontology_tree` must have been run for this to work.

Show ontology tree for root ID 505 i.e. "Renting recreational spaces":

```graphql
query {
  ontologyTree(rootId: 505) {
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

### Ontology words query

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

## Example Elasticsearch queries

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

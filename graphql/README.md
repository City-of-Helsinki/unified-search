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
- [Example GraphQL queries](#example-graphql-queries)
  - [Administrative divisions query](#administrative-divisions-query)
  - [Free text search - location index](#free-text-search---location-index)
  - [Pagination and scores](#pagination-and-scores)
  - [Raw data for debugging purposes](#raw-data-for-debugging-purposes)
  - [Suggestions for text completion](#suggestions-for-text-completion)
  - [Ontology tree query](#ontology-tree-query)
  - [Ontology words query](#ontology-words-query)
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

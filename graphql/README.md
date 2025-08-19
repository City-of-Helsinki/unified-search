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
- [GraphQL queries](#graphql-queries)
  - [Free text search - location index](#free-text-search---location-index)
  - [Pagination and scores](#pagination-and-scores)
  - [Raw data for debugging purposes](#raw-data-for-debugging-purposes)
  - [Suggestions for text completion](#suggestions-for-text-completion)
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
2. Run `yarn start` for development, or `yarn transpile` & `yarn serve` for production build.

## Environments

Where is the GraphQL API running?

Based on info from [kuva-unified-search](https://dev.azure.com/City-of-Helsinki/kuva-unified-search) Azure DevOps project:

- Review per PR (e.g. PR #321): https://kuva-unified-search-pr321.api.dev.hel.ninja/search
- Testing: https://kuva-unified-search.api.test.hel.ninja/search
- Staging: https://kuva-unified-search.api.stage.hel.ninja/search
- Production: https://kuva-unified-search.api.hel.fi/search

## GraphQL queries

It is recommended to use a GraphQL client for sending queries.

### Free text search - location index

    query {
      unifiedSearch(index: "location", text: "koira", languages:FINNISH) {
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

### Pagination and scores

    query {
      unifiedSearch(text: "koira", index: "location") {
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

### Raw data for debugging purposes

    query {
      unifiedSearch(text: "koira", index: "location", first: 3) {
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

### Suggestions for text completion

    query {
      unifiedSearchCompletionSuggestions(prefix:"ki", languages:FINNISH, index:"location")
      {
        suggestions {
          label
        }
      }
    }

### Date ranges

Date can be used in queries assuming mapping type is correct (`date` in ES, `datetime.datetime` in Python):

Get documents created in the last 2 minutes:

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

For references, see:

- https://www.elastic.co/guide/en/elasticsearch/reference/current/common-options.html#date-math
- https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-range-query.html#ranges-on-dates

## Code linting & formatting

This project uses ESLint and prettier for JavaScript/TypeScript code linting and formatting.

## Pre-commit hooks

Because [pre-commit](https://pre-commit.com/) does not support monorepos, it must be configured at repository root.

For this reason, see [repository root README.md](../README.md#pre-commit-hooks) for how to set up pre-commit hooks.

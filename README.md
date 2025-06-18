# Common unified search

This is common unified search: multi domain search over multiple services.

Solution consists of following parts:

[Data collector](https://github.com/City-of-Helsinki/unified-search/tree/main/sources)

- Python Django application for fetching data from multiple sources and storing it to the OpenSearch (or earlier to the Elasticsearch).
- Django management commands are triggered by Kubernetes cron jobs.

[OpenSearch](https://opensearch.org/) (local dev) / [Elasticsearch](https://www.elastic.co/elasticsearch) (review/testing/staging/production)

- Search engine for indexing the data.

[GraphQL API](https://github.com/City-of-Helsinki/unified-search/tree/main/graphql)

- GraphQL API on top of OpenSearch providing high level interface for end (frontend) users.

# Environments

Based on info from [kuva-unified-search](https://dev.azure.com/City-of-Helsinki/kuva-unified-search) Azure DevOps project:

## Data collector

- Review per PR (e.g. PR #321): https://kuva-unified-search-sources-pr321.api.dev.hel.ninja/
- Testing: https://kuva-unified-search-sources.api.test.hel.ninja/
- Staging: https://kuva-unified-search-sources.api.stage.hel.ninja/
- Production: https://kuva-unified-search-sources.api.hel.ninja/

## OpenSearch / Elasticsearch

OpenSearch is used only for local development.

All other environments (i.e. review/testing/staging/production) use Elasticsearch.

## GraphQL API

- Review per PR (e.g. PR #321): https://kuva-unified-search-pr321.api.dev.hel.ninja/search
- Testing: https://kuva-unified-search.api.test.hel.ninja/search
- Staging: https://kuva-unified-search.api.stage.hel.ninja/search
- Production: https://kuva-unified-search.api.hel.fi/search

# Development

Docker compose sets up 3 node local test environment with Kibana. Make sure at least 4 GB of RAM is allocated to Docker.

    docker compose up

To verify nodes are up and running:

    curl -X GET "localhost:9200/_cat/nodes?v=true&pretty"

Services:

- GraphQL search API: http://localhost:4000/search
- OpenSearch Dashboard at http://localhost:5601
- OpenSearch Dashboard Dev Tools at http://localhost:5601/app/dev_tools#/console
- OpenSearch at http://localhost:9200
- Data sources (data collector) at http://localhost:5000/

## Fetching data with data collector

Following management command can be used to fetch data from external data sources and store it to OpenSearch:

    docker compose exec sources python manage.py ingest_data

It is also possible to limit command to certain importer:

    docker compose exec sources python manage.py ingest_data location

Delete all data:

    docker compose exec sources python manage.py ingest_data --delete

Delete data imported by given importer:

    docker compose exec sources python manage.py ingest_data location --delete

Currently implemented importers and the indexes they create:

- **event** (event)
- **location** (location)
- **ontology_tree** (ontology_tree)
- **ontology_word** (ontology_word)
- **administrative_division** (administrative_division, helsinki_common_administrative_division)

## Testing

Following test script is available for basic health check<br>
(Install Python 3.9 [virtual env](https://docs.astral.sh/uv/pip/environments/) with [uv](https://github.com/astral-sh/uv)
using `uv venv --python 3.9`, `uv pip install -r test/requirements.txt` and activate it with
`source .venv/bin/activate` or `.venv/Scripts/activate` first):

    pytest test/test_es_health.py --log-cli-level=debug

Sources tests, with `docker compose`:

    docker compose exec sources pytest

GraphQL tests under `graphql` folder (Install dependencies with `yarn` first):

    yarn test:ci

## GraphQL search API

If not running with `docker compose`, start Apollo based GraphQL server at `unified-search/graphql/`:

    node index.js

## GraphQL queries

It is recommended to use GraphQL client such as Altair for sending queries.

### Search all with specified ontology

    query {
      unifiedSearch(index: "event", text: "*", ontology: "vapaaehtoistoiminta", languages:FINNISH) {
        edges {
          cursor
          node {
            event {
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

### Free text search - event index

    query {
      unifiedSearch(index: "event", text: "koira", languages:FINNISH) {
        edges {
          cursor
          node {
            event {
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
            searchCategories
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

For references, see

https://www.elastic.co/guide/en/elasticsearch/reference/current/common-options.html#date-math

https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-range-query.html#ranges-on-dates

## GraphQL search API - using curl

    $ curl --insecure -X POST -H "Content-Type: application/json" --data '{"query":"query{unifiedSearch(text:\"leikkipuisto\", index:\"location\"){count}}"}' <GraphQL base URL>/search

    {"data":{"unifiedSearch":{"count":61}}}

## Python dependencies

Install pip-tools to obtain pip-compile command:

    pip install pip-tools

Compile requirements.in to requirements.txt:

    pip-compile

Install dependencies from requirements.txt:

    pip install -r requirements.txt

## Known issues

1. New index is added but Elasticsearch returns elasticsearch.exceptions.AuthorizationException.

   Elasticsearch access control list needs to be updated with access to new index. When using Aiven it
   can be done from its control panel (under ACL).

# Issues board

https://helsinkisolutionoffice.atlassian.net/projects/US/issues/

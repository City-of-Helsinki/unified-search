# Common unified search

This is common unified search: multi domain search over multiple services.

Solution consists of following parts:

[Data collector](https://github.com/City-of-Helsinki/unified-search/tree/develop/sources)
- Python Django application for fetching data from multiple sources and storing it to Elasticsearch.
- Django management commands are triggered by Kubernetes cron jobs.

Elasticsearch
- Search engine for indexing the data.

[GraphQL API](https://github.com/City-of-Helsinki/unified-search/tree/develop/graphql)
- GraphQL API on top of Elasticsearch providing high level interface for end (frontend) users.

# Endpoints

- Stable at https://unified-search.prod.kuva.hel.ninja/search
- Staging at https://unified-search.test.kuva.hel.ninja/search

# Development

Docker compose sets up 3 node local test environment with Kibana. Make sure at least 4 GB of RAM is allocated to Docker.

    docker-compose up

To verify nodes are up and running:

    curl -X GET "localhost:9200/_cat/nodes?v=true&pretty"

Services:

- GraphQL search API: http://localhost:4000/search
- Kibana at http://localhost:5601
- Kibana Dev Tools at http://localhost:5601/app/dev_tools#/console
- ElasticSearch at http://localhost:9200
- Data sources (data collector) at http://localhost:5000/

Deprecated:
- Graphene based testing GraphQL search API at http://localhost:5001/graphql

## Fetching data with data collector

Following management command can be used to fetch data from external data sources and store it to Elasticsearch:

    docker-compose exec sources python manage.py ingest_data

It is also possible to limit command to certain index:

    docker-compose exec sources python manage.py ingest_data --index location

Delete all data:

    docker-compose exec sources python manage.py ingest_data --delete

Delete data at given index:

    docker-compose exec sources python manage.py ingest_data --delete --index location

## Testing

Following test script is available for basic health check:

    pytest --log-cli-level=debug test_es_health.py

## GraphQL search API

If not running with docker-compose, start Apollo based GraphQL server at `unified-search/graphql/`:

    node index.js

## GraphQL queries

It is recommended to use GraphQL client such as Altair for sending queries. Example:

    query {
      unifiedSearch(q:"koira", index:"location") {
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


## GraphQL search API - using curl

    $ curl --insecure -X POST -H "Content-Type: application/json" --data '{"query":"query{unifiedSearch(q:\"leikkipuisto\", index:\"location\"){count}}"}' <GraphQL base URL>/search

    {"data":{"unifiedSearch":{"count":61}}}

## Python dependencies

Compile requirements.in to requirements.txt:

    pip-compile

Install dependencies from requirements.txt:

    pip install -r requirements.txt

# Issues board

https://helsinkisolutionoffice.atlassian.net/projects/US/issues/
# Common unified search

This is common unified search: multi domain search over multiple services.

# Development

Docker compose sets up 3 node local test environment with Kibana. Make sure at least 4 GB of RAM is allocated to Docker.

	docker-compose up

To verify nodes are up and running:

	curl -X GET "localhost:9200/_cat/nodes?v=true&pretty"

Services:

- Kibana at http://localhost:5601
- Kibana Dev Tools at http://localhost:5601/app/dev_tools#/console
- ElasticSearch at http://localhost:9200
- Data sources (data collector) at http://localhost:5000/
- GraphQL search API at http://localhost:5001/graphql

## Testing

Following management command can be used to fetch data from external data sources.
This is fully for testing purposes and subject to change:

	docker-compose exec sources python manage.py ingest_data

After running the management command there should be data available at ES.
Following test script is available to verify it:

	pytest --log-cli-level=debug test_es_search.py

To delete testing data:

	docker-compose exec sources python manage.py ingest_data --delete


## GraphQL search API

Start Apollo based GraphQL server at unified-search/graphql/:

	node index.js

See Queries.


## GraphQL queries

# Write your query or mutation here

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
        hits{
          _index
          _source {
            data
            }
          }
        }
      }
   }
}


## GraphQL search API - Graphene

Graphene Django based GraphQL search API is available at http://localhost:5001/graphql.

After ingesting data, try

	query {
		q(match:"helsinki") {
			text
			count
			rawResults
		}
	}

## Python dependencies

Compile requirements.in to requirements.txt:

	pip-compile

Install dependencies from requirements.txt:

	pip install -r requirements.txt

# Issues board

https://helsinkisolutionoffice.atlassian.net/projects/US/issues/
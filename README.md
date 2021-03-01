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

## Testing

Following management command can be used to fetch data from external data sources.
This is fully for testing purposes and subject to change:

	docker-compose exec sources python manage.py ingest_data

After running the management command there should be data available at ES.
Following test script is available to verify it:

	pytest --log-cli-level=debug test_es_search.py

To delete testing data:

	docker-compose exec sources python manage.py ingest_data --delete

## Python dependencies

Compile requirements.in to requirements.txt:

	pip-compile

Install dependencies from requirements.txt:

	pip install -r requirements.txt

# Issues board

https://helsinkisolutionoffice.atlassian.net/projects/US/issues/
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

## Python dependencies

Compile requirements.in to requirements.txt:

	pip-compile

Install dependencies from requirements.txt:

	pip install -r requirements.txt

# Issues board

https://helsinkisolutionoffice.atlassian.net/projects/US/issues/
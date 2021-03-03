import graphene
from elasticsearch import Elasticsearch


def es_search(search_term):
    es = Elasticsearch([{"host": "es01", "port": 9200}])

    query = {"query": {"query_string": {"query": search_term}}}

    s = es.search(index="test-index", body=query)

    count = s["hits"]["total"]["value"]
    raw_results = s["hits"]["hits"]
    return count, raw_results


class QueryResult(graphene.ObjectType):
    text = graphene.String()
    count = graphene.Int()
    # This gets exposed as rawResults
    raw_results = graphene.String()


class Query(graphene.ObjectType):
    q = graphene.Field(QueryResult, match=graphene.String())

    def resolve_q(root, info, match):
        count, raw_results = es_search(match)
        return QueryResult(text=match, count=count, raw_results=raw_results)


schema = graphene.Schema(query=Query)

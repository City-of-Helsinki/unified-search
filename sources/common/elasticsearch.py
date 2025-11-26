from django.conf import settings
from elasticsearch import Elasticsearch


def get_elasticsearch_client():
    """
    Returns an Elasticsearch client configured according to current settings.
    """
    basic_auth = (
        (settings.ES_USERNAME, settings.ES_PASSWORD) if settings.ES_USERNAME else None
    )
    return Elasticsearch(hosts=settings.ES_URI, basic_auth=basic_auth)

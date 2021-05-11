from .traffic import request_json
import logging


logger = logging.getLogger(__name__)


class Keyword:
    """ Helper class for dealing with (yso) keyword ID's.
        Instead of fething extra information for each ID separately, get
        local cache and use it to enrich given ID's.
    """

    def __init__(self):
        self.keywords = self._get_keywords()

    def _get_keywords(self):
        url = "https://api.hel.fi/linkedevents/v1/keyword/"
        keywords = {}
        total_count = 0

        logger.debug(f"Fetching {url}")

        while url:
            data = request_json(url)
            total_count += len(data["data"])

            for elem in data["data"]:
                keywords[elem["id"]] = elem

            url = data["meta"]["next"]

        logger.debug(f"Cached {total_count} keywords")
        return keywords

    def enrich_id(self, keyword_id):
        if keyword_id in self.keywords:
            return self.keywords[keyword_id]
        return None

    def enrich(self, keyword_list):
        results = []

        for elem in keyword_list:
            # Format is as follows:
            # {'@id': 'https://linkedevents-api.dev.hel.ninja/linkedevents-dev/v1/keyword/yso:p1235/'}

            _id = elem["@id"].split('/')[-2]
            results.append(self.enrich_id(_id))

        return results

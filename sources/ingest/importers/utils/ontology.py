from typing import List

from .traffic import request_json


class AlreadyFoundError(Exception):
    """Custom expection for checking against duplicate entries."""

    pass


class Ontology:
    """Helper class for dealing with ontology ID's and ontology tree.
    Instead of fething extra information for each ID separately, get
    local cache and use it to enrich given ID's.
    """

    def __init__(self):
        self.ontology_tree = self._get_ontology_tree_ids()
        self.ontology_word = self._get_ontology_word_ids()

    def _get_ontology_tree_ids(self):
        url = "https://www.hel.fi/palvelukarttaws/rest/v4/ontologytree/"
        data = request_json(url)
        return data

    def _get_ontology_word_ids(self):
        url = "https://www.hel.fi/palvelukarttaws/rest/v4/ontologyword/"
        data = request_json(url)
        return data

    def _get_tree_elem(self, _id):
        for e in self.ontology_tree:
            if e["id"] == _id:
                return e
        return None

    def _get_tree(self, _id, hits=None):
        """Get parents recursively."""

        if not hits:
            hits = []
        e = self._get_tree_elem(_id)

        hits.append(e)
        if not e.get("parent_id", None):
            return hits
        return self._get_tree(e["parent_id"], hits)

    def get_ancestor_ids(self, _id: str) -> List[str]:
        return [o["id"] for o in self._get_tree(_id) if o["id"] != _id]

    def enrich_tree_ids(self, id_list):
        """For each id in the list, get tree of related enriched id's and store
        individual entries.
        """

        info = []

        for _id in id_list:
            # Get tree of id's
            data = self._get_tree(_id)
            # Store only individual id's, flat list
            for i in data:
                try:
                    for old_elem in info:
                        if old_elem["id"] == i["id"]:
                            raise AlreadyFoundError
                    info.append(i)
                except AlreadyFoundError:
                    # skip duplicate
                    pass

        return info

    def enrich_word_ids(self, id_list):
        """For each id in the list, get enriched id."""

        info = []

        for _id in id_list:
            for i in self.ontology_word:
                if i["id"] == _id:
                    info.append(i)

        return info

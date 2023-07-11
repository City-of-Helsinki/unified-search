from dataclasses import dataclass
from typing import List, Union

from .base import Importer
from .utils import LanguageString, LanguageStringConverter, Ontology


@dataclass
class OntologyTreeObject:
    name: LanguageString
    ancestorIds: List[str]
    childIds: List[str]
    ontologyWordReference: Union[str, None]


class OntologyTreeImporter(Importer[OntologyTreeObject]):
    index_base_names = ("ontology_tree",)

    def run(self):
        ontology = Ontology()

        for tree_obj in ontology.ontology_tree:
            data = OntologyTreeObject(
                name=LanguageStringConverter(
                    tree_obj, self.use_fallback_languages
                ).get_language_string("name"),
                ancestorIds=ontology.get_ancestor_ids(tree_obj["id"]),
                childIds=tree_obj["child_ids"],
                ontologyWordReference=tree_obj.get("ontologyword_reference"),
            )
            self.add_data(data, extra_params={"id": tree_obj["id"]})

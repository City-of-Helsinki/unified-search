from dataclasses import dataclass

from .base import Importer
from .utils import LanguageString, LanguageStringConverter, Ontology


@dataclass
class OntologyWordObject:
    name: LanguageString


class OntologyWordImporter(Importer[OntologyWordObject]):
    index_base_names = ("ontology_word",)

    def run(self):
        ontology = Ontology()

        for word_obj in ontology.ontology_word:
            data = OntologyWordObject(
                name=LanguageStringConverter(
                    word_obj, self.use_fallback_languages
                ).get_language_string("ontologyword"),
            )
            self.add_data(data, extra_params={"id": word_obj["id"]})

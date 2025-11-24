import logging
from dataclasses import dataclass

from django.utils import timezone

from .base import Importer
from .utils import LanguageString, LanguageStringConverter, Ontology

logger = logging.getLogger(__name__)


@dataclass
class OntologyWordObject:
    name: LanguageString


class OntologyWordImporter(Importer[OntologyWordObject]):
    index_base_names = ("ontology_word",)

    def run(self):
        logger.info(f"Started importing ontology words at {timezone.now():%X}")
        ontology = Ontology()

        for word_obj in ontology.ontology_word:
            data = OntologyWordObject(
                name=LanguageStringConverter(
                    word_obj, self.use_fallback_languages
                ).get_language_string("ontologyword"),
            )
            self.add_data(data, extra_params={"id": word_obj["id"]})

        logger.info(
            f"Finished importing {len(ontology.ontology_word)} ontology words "
            + f"at {timezone.now():%X}"
        )

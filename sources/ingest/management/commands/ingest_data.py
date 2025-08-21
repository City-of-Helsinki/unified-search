import logging
from typing import Dict, Optional, Type, Union

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from ingest.importers.administrative_division import AdministrativeDivisionImporter
from ingest.importers.location import LocationImporter
from ingest.importers.ontology_tree import OntologyTreeImporter
from ingest.importers.ontology_word import OntologyWordImporter

logger = logging.getLogger(__name__)

ImporterMap = Dict[
    str,
    Union[
        Type[AdministrativeDivisionImporter],
        Type[LocationImporter],
        Type[OntologyTreeImporter],
        Type[OntologyWordImporter],
    ],
]


class Command(BaseCommand):
    help = "Ingest data from external data sources"

    all_importers: ImporterMap = {
        "administrative_division": AdministrativeDivisionImporter,
        "location": LocationImporter,
        "ontology_tree": OntologyTreeImporter,
        "ontology_word": OntologyWordImporter,
    }

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            "--ignore-fallback-languages",  # Turn off use_fallback_languages
            dest="use_fallback_languages",
            action="store_false",  # Means use_fallback_languages=False because of dest
            default=True,  # Means use_fallback_languages=True because of dest
            help=(
                "Ignore the use of fallback languages. By default "
                "fallback languages are used in order en, fi, sv."
            ),
        )

        # Positional (optional) argument(s)
        parser.add_argument(
            "importer",
            nargs="*",
            help="Limit to given importer(s)",
        )

    def handle(self, *args, **kwargs):
        start_time = timezone.now()
        logger.info(f"Started at {start_time:%X}")

        importer_map = self.get_importer_map(kwargs["importer"])

        self.handle_import(
            importer_map,
            use_fallback_languages=kwargs.get("use_fallback_languages", True),
        )

        end_time = timezone.now()
        logger.info(
            f"Completed at {end_time:%X}, took {(end_time - start_time).seconds} sec."
        )

    def get_importer_map(self, importer_names: Optional[str]) -> ImporterMap:
        importer_map: ImporterMap = {}
        for importer_name in importer_names or self.all_importers.keys():
            try:
                importer_map[importer_name] = self.all_importers[importer_name]
            except KeyError:
                raise CommandError(
                    f"Unknown importer: '{importer_name}', "
                    f"allowed: {list(self.all_importers.keys())}."
                )
        return importer_map

    def handle_import(
        self, importer_map: ImporterMap, use_fallback_languages: bool
    ) -> None:
        for importer_name, importer_class in importer_map.items():
            logger.info(f"Importing {importer_name}")
            try:
                importer_class(use_fallback_languages=use_fallback_languages).base_run()
            except Exception as e:  # noqa
                logger.exception(e)
                raise e

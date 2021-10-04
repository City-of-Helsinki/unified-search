import logging
from typing import Dict, Optional, Type, Union

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from ...importers import EventImporter, LocationImporter, OntologyTreeImporter, OntologyWordsImporter

logger = logging.getLogger(__name__)

ImporterMap = Dict[
    str, Union[Type[EventImporter], Type[LocationImporter], Type[OntologyTreeImporter], Type[OntologyWordsImporter]]
]


class Command(BaseCommand):
    help = "Ingest data from external data sources"

    all_importers: ImporterMap = {
        "location": LocationImporter,
        "event": EventImporter,
        "ontology_tree": OntologyTreeImporter,
        "ontology_words": OntologyWordsImporter,
    }

    def add_arguments(self, parser):

        # Named (optional) argument
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete stored data",
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

        if kwargs["delete"]:
            self.handle_delete(importer_map)
            return

        self.handle_import(importer_map)

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

    def handle_delete(self, importer_map: ImporterMap) -> None:
        for importer_name, importer_class in importer_map.items():
            logger.info(f"Deleting data {importer_name}")
            try:
                importer_class().delete_all_data()
            except Exception as e:  # noqa
                logger.exception(e)

    def handle_import(self, importer_map: ImporterMap) -> None:
        for importer_name, importer_class in importer_map.items():
            logger.info(f"Importing {importer_name}")
            try:
                importer_class().base_run()
            except Exception as e:  # noqa
                logger.exception(e)

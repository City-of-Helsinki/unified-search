from munigeo.importer.base import get_importers, register_importer
from munigeo.management.commands.geo_import import Command as MunigeoGeoImportCommand


class Command(MunigeoGeoImportCommand):  # NOSONAR
    def handle(self, *args, **options):
        get_importers()

        from ingest.geo_importers import HelsinkiImporter

        register_importer(HelsinkiImporter)
        return super().handle(*args, **options)

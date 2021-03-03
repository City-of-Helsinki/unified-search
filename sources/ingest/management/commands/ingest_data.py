from django.core.management.base import BaseCommand
from django.utils import timezone

from ingest.fetch import servicemap, linkedevents


class Command(BaseCommand):
    help = "Ingest data from external data sources"

    def add_arguments(self, parser):

        # Named (optional) argument
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete stored data",
        )

    def handle(self, *args, **kwargs):
        time = timezone.now().strftime("%X")
        print("It's now %s" % time)

        if kwargs["delete"]:
            print("DELETING DATA")
            servicemap.delete()
            linkedevents.delete()
            return

        # TODO: add proper mapping, this works out of good luck as
        # e.g. ID fields are of different type (string vs float)
        print(linkedevents.fetch())
        print(servicemap.fetch())


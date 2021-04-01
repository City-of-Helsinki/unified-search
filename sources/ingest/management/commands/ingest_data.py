from django.core.management.base import BaseCommand
from django.utils import timezone

from ingest.fetch import servicemap, linkedevents, palvelukartta, location


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
            palvelukartta.delete()
            servicemap.delete()
            linkedevents.delete()
            location.delete()
            return

        """
        print(linkedevents.fetch())
        linkedevents.set_alias("test-index")
        print(servicemap.fetch())
        servicemap.set_alias("test-index")
        print(palvelukartta.fetch())
        palvelukartta.set_alias("test-index")
        """
        location.fetch()


        time = timezone.now().strftime("%X")
        print("Completed at %s" % time)


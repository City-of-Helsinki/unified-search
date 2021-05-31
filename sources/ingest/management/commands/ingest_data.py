from django.core.management.base import BaseCommand
from django.utils import timezone
import logging

from ingest.fetch import location, event


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Ingest data from external data sources"

    def add_arguments(self, parser):

        # Named (optional) argument
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete stored data",
        )

        # Named (optional) argument
        parser.add_argument(
            "--index",
            nargs="*",
            help="Limit to given index(s)",
        )

    def handle(self, *args, **kwargs):
        time = timezone.now().strftime("%X")
        logger.info("Started at %s" % time)

        # Provided by ingest.fetch, defaults to these unless specified on command line
        inds = {
            "location": location,
            "event": event
        }

        index_list = kwargs["index"]

        if index_list:
            # Check validity
            for i in index_list:
                if i not in inds.keys():
                    logger.error(f"Unknown index {i}, allowed: {inds.keys()}")
                    return

            inds = {i: inds[i] for i in index_list}

        # delete indexes
        if kwargs["delete"]:
            for name, _obj in inds.items():
                logger.info(f"DELETING DATA at {name}")
                _obj.delete()
            return

        # fetch indexes
        for name, _obj in inds.items():
            logger.info(f"Fetching {name}")
            _obj.fetch()

        time = timezone.now().strftime("%X")
        logger.info("Completed at %s" % time)

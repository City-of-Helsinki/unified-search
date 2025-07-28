import logging

from django.apps import AppConfig
from health_check.plugins import plugin_dir

logger = logging.getLogger(__name__)


class CustomHealthChecksAppConfig(AppConfig):
    name = "custom_health_checks"

    def ready(self):
        from .backends import DatabaseHealthCheck

        plugin_dir.register(DatabaseHealthCheck)
        logger.info("Registered DatabaseHealthCheck to health_check plugins.")

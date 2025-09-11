import logging
from abc import ABC, abstractmethod
from dataclasses import asdict, is_dataclass
from typing import Generic, List, Optional, Tuple, TypeVar

from django.conf import settings

from common.elasticsearch_compatibility import get_compatible_elasticsearch_package

logger = logging.getLogger(__name__)


IndexableData = TypeVar("IndexableData")


class Importer(ABC, Generic[IndexableData]):
    """Base class for importers.

    This base class provides functionality for ingesting data to Elastic Search. A
    subclass needs to provide index_base_names (normally just one, multiple if you need
    to import multiple kinds of data with the same importer) and implement run(), which
    will be called and should carry out the actual importing / ingesting process.
    Basically it should call apply_mapping() once at the beginning if needed, and then
    add documents using add_data() method.

    For every index_base_name there will be actually two indexes used. Let's use name
    "location" as an example here. Then, there will be actual indexes "location_1" and
    "location_2". In addition, two index aliases are used, "location" (the same as the
    base name) and "location_wip".

    The idea is that normally the data will be in one of the indexes, and "location"
    alias will point to that index. When new data is being imported, the other free
    index is used for that, and "location_wip" alias will point to that index. Once
    the import is finished, the "location" alias is swapped to the new index, and the
    old index is removed.

    A special occasion is when data is being imported the first time. In that case,
    "location" alias will also point to the yet to be finished index so that one
    doesn't need to wait for the import to finish to get some data available.
    """

    index_base_names: Tuple[str, ...]

    def __init__(self, use_fallback_languages=True) -> None:
        if not getattr(self, "index_base_names", None):
            raise NotImplementedError(
                f"Importer {self.__class__.__name__} is missing index_base_names."
            )
        es_package = get_compatible_elasticsearch_package()
        self.es = es_package.Elasticsearch([settings.ES_URI]).options(
            request_timeout=60
        )
        self.es_bulk = es_package.helpers.bulk
        self.NotFoundError = es_package.exceptions.NotFoundError
        self.use_fallback_languages = use_fallback_languages

    @abstractmethod
    def run(self) -> None:
        pass

    def base_run(self):
        """
        Initializes, runs and finishes the importing.
        :return: the count of units imported or None if there was no importer.
        """
        self._initialize()
        result = self.run()
        self._finish()
        return result

    def add_data(
        self,
        data: IndexableData,
        index_base_name: Optional[str] = None,
        extra_params: Optional[dict] = None,
    ) -> None:
        index_name = self._get_wip_alias(index_base_name or self.index_base_names[0])
        body = asdict(data) if is_dataclass(data) else data
        try:
            self.es.index(index=index_name, body=body, **(extra_params or {}))
        except ConnectionError as e:
            logger.error(e)

    def add_data_bulk(
        self,
        data: List[IndexableData],
        index_base_name: Optional[str] = None,
    ) -> None:
        index_name = self._get_wip_alias(index_base_name or self.index_base_names[0])

        body = [
            {"_index": index_name, "_source": asdict(d) if is_dataclass(d) else d}
            for d in data
        ]
        try:
            self.es_bulk(self.es, body)
        except ConnectionError as e:
            logger.error(e)

    def apply_mapping(self, mapping: dict, index_base_name: Optional[str] = None):
        index_name = self._get_wip_alias(index_base_name or self.index_base_names[0])
        logger.debug(f"Applying custom mapping to index {index_name}")
        self.es.indices.put_mapping(index=index_name, body=mapping)

    def _initialize(self) -> None:
        for active_alias in self.index_base_names:
            logger.debug(f"Initializing {active_alias}")

            indexes = (f"{active_alias}_1", f"{active_alias}_2")
            active_index = self._get_index_from_es(active_alias)
            wip_index = indexes[1] if active_index == indexes[0] else indexes[0]

            # Clean everything except possible active index and alias
            for index in indexes:
                if index != active_index:
                    self._delete_index(index)
            self._delete_alias(self._get_wip_alias(active_alias))

            wip_alias = self._get_wip_alias(active_alias)
            wip_index_aliases = {wip_alias}
            if not active_index:
                # Make wip data available when there is no existing index. This is
                # most useful in development where one doesn't need to run the whole
                # import to get some data available.
                wip_index_aliases.add(active_alias)

            logger.debug(
                f"Creating wip index {wip_index} with aliases {wip_index_aliases}"
            )
            self.es.indices.create(
                index=wip_index, body={"aliases": {w: {} for w in wip_index_aliases}}
            )

    def _finish(self) -> None:
        for active_alias in self.index_base_names:
            logger.debug(f"Finishing {active_alias}")

            wip_alias = self._get_wip_alias(active_alias)
            old_active_index = self._get_index_from_es(active_alias)
            wip_index = self._get_index_from_es(wip_alias)

            # Swap active alias to the wip index, delete the wip alias and old active
            # index as long as it is not the same as the wip index
            self.es.indices.update_aliases(
                body={
                    "actions": [
                        {"add": {"index": wip_index, "alias": active_alias}},
                        {
                            "remove": {
                                "index": f"{active_alias}_*",
                                "alias": wip_alias,
                            }
                        },
                    ]
                }
            )
            if old_active_index and old_active_index != wip_index:
                self._delete_index(old_active_index)

    def _delete_index(self, index) -> None:
        logger.debug(f"Deleting index {index}")
        try:
            response = self.es.options(ignore_status=404).indices.delete(index=index)
            logger.debug(response)
        except self.NotFoundError as e:
            if e.error == "index_not_found_exception":
                logger.debug(f"Index {index} does not exist")
            else:
                raise e

    def _delete_alias(self, alias: str) -> None:
        logger.debug(f"Deleting alias {alias}")
        try:
            self.es.options(ignore_status=404).indices.delete_alias(
                index="*", name=alias
            )
        except self.NotFoundError:
            pass

    def _get_index_from_es(self, alias: str) -> Optional[str]:
        try:
            return next(iter(self.es.indices.get_alias(name=alias)))
        except (self.NotFoundError, StopIteration):
            return None

    @staticmethod
    def _get_wip_alias(alias: str) -> str:
        return f"{alias}_wip"

import logging
from abc import ABC, abstractmethod
from dataclasses import asdict, is_dataclass
from typing import Generic, Optional, Tuple, TypeVar

from django.conf import settings
from elasticsearch import Elasticsearch, NotFoundError, RequestError

logger = logging.getLogger(__name__)


IndexableData = TypeVar("IndexableData")


class Importer(ABC, Generic[IndexableData]):
    index_names: Tuple[str, ...]

    def __init__(self) -> None:
        if not getattr(self, "index_names", None):
            raise NotImplementedError(
                f"Importer {self.__class__.__name__} is missing " f'"index_names".'
            )
        self.es = Elasticsearch([settings.ES_URI])

    def create_indexes(self) -> None:
        for index_name in self.index_names:
            logger.debug(f"Creating index {index_name}")
            try:
                response = self.es.indices.create(index=index_name)
                logger.debug(response)
            except RequestError as e:
                if e.error == "resource_already_exists_exception":
                    logger.debug(f"Index {index_name} already exists")
                else:
                    raise e

    def add_to_index(
        self,
        data: IndexableData,
        index_name: Optional[str] = None,
        extra_params: Optional[dict] = None,
    ) -> None:
        index_name = index_name or self.index_names[0]
        body = asdict(data) if is_dataclass(data) else data
        try:
            self.es.index(index=index_name, body=body, **(extra_params or {}))
        except ConnectionError as e:
            logger.error(e)

    def delete_indexes(self) -> None:
        for index_name in self.index_names:
            logger.debug(f"Deleting index {index_name}")
            try:
                response = self.es.indices.delete(index=index_name)
                logger.debug(response)
            except NotFoundError as e:
                if e.error == "index_not_found_exception":
                    logger.debug(f"Index {index_name} does not exist")
                else:
                    raise e

    def apply_mapping(self, mapping: dict, index_name: Optional[str] = None):
        index_name = index_name or self.index_names[0]
        logger.debug(f"Applying custom mapping to index {index_name}")
        self.es.indices.put_mapping(index=index_name, body=mapping)

    @abstractmethod
    def run(self) -> None:
        pass

from dataclasses import dataclass

import pytest

from ingest.importers.base import Importer


@dataclass
class SomeData:
    foo: str


class SomeImporter(Importer[SomeData]):
    index_base_names = ("test",)
    number = 1

    def run(self):
        self.add_data(
            SomeData(foo=f"import number {self.number}"), extra_params={"id": "baz"}
        )
        self.number += 1


def assert_snapshot_match_es_data_and_aliases(snapshot, es):
    es.indices.refresh(index="test")

    hits = es.search(index="test")["hits"]
    snapshot.assert_match(hits)

    aliases = es.indices.get_alias(index="test_*")
    snapshot.assert_match(aliases)


def test_importer_end_results(snapshot, es):
    importer = SomeImporter()

    for _ in range(3):
        importer.base_run()
        assert_snapshot_match_es_data_and_aliases(snapshot, es)


@pytest.mark.parametrize(
    "has_old_data", (False, True), ids=("does not have old data", "has old data")
)
def test_importer_wip_results(snapshot, es, has_old_data):
    class WipTestImporter(Importer):
        index_base_names = ("test",)

        def run(self):
            self.add_data(SomeData(foo="new data"), extra_params={"id": "foo"})

            # check the situation in the middle of the import
            assert_snapshot_match_es_data_and_aliases(snapshot, es)

    if has_old_data:
        es.indices.create(index="test_1", body={"aliases": {"test": {}}})
        es.index(index="test_1", body={"foo": "old data"}, id="foo")

    importer = WipTestImporter()
    importer.base_run()

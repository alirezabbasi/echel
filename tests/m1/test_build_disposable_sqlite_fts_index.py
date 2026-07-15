from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from echel.storage import (
    CanonicalRecordStore,
    CanonicalRepository,
    DisposableIndex,
    IndexError,
    RecordExpectation,
)


ROOT = Path(__file__).resolve().parents[2]
VALID_RECORDS = json.loads(
    (ROOT / "schemas" / "v1" / "fixtures" / "valid-records.json").read_text()
)


class DisposableIndexTests(unittest.TestCase):
    def make_index(self, workspace: Path) -> tuple[CanonicalRecordStore, DisposableIndex]:
        (workspace / ".git").mkdir()
        store = CanonicalRecordStore(CanonicalRepository.create(workspace))
        for fixture in VALID_RECORDS:
            record = deepcopy(fixture)
            record["revision"] = 1
            store.write(record, RecordExpectation.absent())
        return store, DisposableIndex(store)

    @staticmethod
    def canonical_bytes(store: CanonicalRecordStore) -> dict[str, bytes]:
        return {
            path.relative_to(store.repository.root).as_posix(): path.read_bytes()
            for path in sorted(store.repository.records.rglob("*.json"))
        } | {
            "project.json": (store.repository.root / "project.json").read_bytes()
        }

    def test_rebuild_search_and_relationship_traversal_do_not_touch_truth(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store, index = self.make_index(Path(directory))
            before = self.canonical_bytes(store)

            result = index.rebuild()

            self.assertEqual(len(VALID_RECORDS), result.records)
            self.assertEqual(1, result.relationships)
            self.assertEqual(["claim:need"], [hit.record_id for hit in index.search("traceability")])
            links = index.related("claim:need", direction="out", predicate="informs")
            self.assertEqual(["relationship:need-project"], [hit.relationship_id for hit in links])
            self.assertEqual(before, self.canonical_bytes(store))

    def test_delete_and_rebuild_yield_equivalent_queries_and_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store, index = self.make_index(Path(directory))
            first = index.rebuild()
            search = tuple(hit.to_dict() for hit in index.search("need OR project"))
            related = tuple(hit.to_dict() for hit in index.related("project:demo"))

            self.assertTrue(index.discard())
            self.assertFalse(index.path.exists())
            second = index.rebuild()

            self.assertEqual(first.fingerprint, second.fingerprint)
            self.assertEqual(search, tuple(hit.to_dict() for hit in index.search("need OR project")))
            self.assertEqual(related, tuple(hit.to_dict() for hit in index.related("project:demo")))
            self.assertEqual(len(VALID_RECORDS), len(self.canonical_bytes(store)))

    def test_missing_stale_and_corrupt_indexes_fail_with_rebuild_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store, index = self.make_index(Path(directory))
            with self.assertRaises(IndexError) as missing:
                index.search("need")
            self.assertEqual("ECHEL-INDEX-NOT-BUILT", missing.exception.code)

            index.rebuild()
            claim = store.load("claim", "claim:need")
            changed = deepcopy(claim.record)
            changed["revision"] += 1
            changed["statement"] = "A changed customer need"
            changed["updated_at"] = "2026-07-15T12:00:00Z"
            store.write(changed, claim.expectation)
            with self.assertRaises(IndexError) as stale:
                index.search("need")
            self.assertEqual("ECHEL-INDEX-STALE", stale.exception.code)

            index.path.write_bytes(b"not sqlite")
            with self.assertRaises(IndexError) as corrupt:
                index.search("need")
            self.assertEqual("ECHEL-INDEX-CORRUPT", corrupt.exception.code)

    def test_rebuild_failure_preserves_previous_queryable_index(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store, index = self.make_index(Path(directory))
            index.rebuild()
            existing = index.path.read_bytes()
            claim_path = store.load("claim", "claim:need").path
            claim_content = claim_path.read_bytes()
            claim_path.write_text("not json")

            with self.assertRaises(RuntimeError):
                index.rebuild()

            claim_path.write_bytes(claim_content)
            self.assertEqual(existing, index.path.read_bytes())
            self.assertEqual(["claim:need"], [hit.record_id for hit in index.search("traceability")])

    def test_filters_limits_and_invalid_queries_are_structured(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, index = self.make_index(Path(directory))
            index.rebuild()
            self.assertEqual(
                ["project:demo"],
                [hit.record_id for hit in index.search("project", record_type="project", limit=1)],
            )
            cases = (
                lambda: index.search(""),
                lambda: index.search("need", record_type="unknown"),
                lambda: index.search("need", limit=0),
                lambda: index.search('"unterminated'),
                lambda: index.related("claim:need", direction="sideways"),
            )
            for operation in cases:
                with self.subTest(operation=operation):
                    with self.assertRaises(IndexError) as caught:
                        operation()
                    self.assertEqual("ECHEL-INDEX-QUERY-INVALID", caught.exception.code)

    def test_cache_escape_is_denied_without_external_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as external:
            store, index = self.make_index(Path(directory))
            cache = store.repository.root / "cache"
            cache.rmdir()
            cache.symlink_to(Path(external), target_is_directory=True)

            with self.assertRaises(IndexError) as caught:
                index.rebuild()

            self.assertEqual("ECHEL-INDEX-PATH-UNSAFE", caught.exception.code)
            self.assertEqual([], list(Path(external).iterdir()))


if __name__ == "__main__":
    unittest.main()

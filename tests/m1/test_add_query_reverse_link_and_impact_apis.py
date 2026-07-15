from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from echel.queries import QueryError, QueryService
from echel.relationships import RelationshipService
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
PROVENANCE = {"actor": "user:architect", "origin": "impact review", "method": "human"}
CREATED_AT = "2026-07-15T13:00:00Z"


class QueryApiTests(unittest.TestCase):
    def make_service(self, workspace: Path) -> tuple[CanonicalRecordStore, DisposableIndex, QueryService]:
        (workspace / ".git").mkdir()
        store = CanonicalRecordStore(CanonicalRepository.create(workspace))
        for fixture in VALID_RECORDS:
            record = deepcopy(fixture)
            record["revision"] = 1
            store.write(record, RecordExpectation.absent())
        relationships = RelationshipService(store)
        relationships.apply(
            relationships.preview(
                "relationship:need-task",
                "claim:need",
                "informs",
                "task:E2-011-r1",
                "The product need shapes this implementation task.",
                PROVENANCE,
                CREATED_AT,
            )
        )
        relationships.apply(
            relationships.preview(
                "relationship:work-task",
                "work:E2-011",
                "depends_on",
                "task:E2-011-r1",
                "The work depends on this executable task specification.",
                PROVENANCE,
                CREATED_AT,
            )
        )
        index = DisposableIndex(store)
        index.rebuild()
        return store, index, QueryService(store, index)

    def test_search_rehydrates_canonical_record_and_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, _, service = self.make_service(Path(directory))
            results = service.search("traceability", record_type="claim")

            self.assertEqual(1, len(results))
            result = results[0].to_dict()
            self.assertEqual("claim:need", result["record_id"])
            self.assertEqual("user:owner", result["provenance"]["actor"])
            self.assertEqual("Users need traceability", result["record"]["statement"])
            self.assertEqual("records/claims/need.json", result["path"])

    def test_reverse_links_explain_authored_reason_direction_and_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, _, service = self.make_service(Path(directory))
            links = service.reverse_links("project:demo", predicate="informs")

            self.assertEqual(1, len(links))
            explanation = links[0].to_dict()
            self.assertEqual("incoming", explanation["direction"])
            self.assertEqual("relationship:need-project", explanation["relationship_id"])
            self.assertIn("why this project exists", explanation["reason"])
            self.assertEqual("user:owner", explanation["provenance"]["actor"])
            self.assertEqual("claim:need", explanation["related"]["record_id"])
            self.assertEqual("user:owner", explanation["related"]["provenance"]["actor"])

    def test_impact_returns_shortest_bounded_paths_with_step_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, _, service = self.make_service(Path(directory))
            result = service.impact("claim:need", max_depth=2).to_dict()
            paths = {path["target"]["record_id"]: path for path in result["paths"]}

            self.assertEqual("explicit-impact/v1", result["policy"])
            self.assertEqual({"project:demo", "task:E2-011-r1", "work:E2-011"}, set(paths))
            work_path = paths["work:E2-011"]
            self.assertEqual(2, work_path["depth"])
            self.assertEqual(
                ["source_to_target", "target_to_source"],
                [step["traversal"] for step in work_path["steps"]],
            )
            self.assertEqual("depends_on", work_path["steps"][1]["predicate"])
            self.assertEqual("user:architect", work_path["steps"][1]["provenance"]["actor"])
            self.assertEqual("user:owner", work_path["target"]["provenance"]["actor"])

    def test_impact_depth_is_enforced_and_cycles_do_not_repeat_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store, index, _ = self.make_service(Path(directory))
            relationships = RelationshipService(store)
            relationships.apply(
                relationships.preview(
                    "relationship:task-work",
                    "task:E2-011-r1",
                    "depends_on",
                    "work:E2-011",
                    "The task also depends on work-level coordination.",
                    PROVENANCE,
                    CREATED_AT,
                )
            )
            index.rebuild()
            service = QueryService(store, index)

            result = service.impact("claim:need", max_depth=1)
            ids = [path.target.record_id for path in result.paths]
            self.assertEqual(["project:demo", "task:E2-011-r1"], ids)
            self.assertEqual(len(ids), len(set(ids)))

    def test_invalid_identifiers_depth_and_missing_records_are_actionable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, _, service = self.make_service(Path(directory))
            cases = (
                (lambda: service.reverse_links("not-an-id"), "ECHEL-QUERY-ID-INVALID"),
                (lambda: service.reverse_links("claim:missing"), "ECHEL-QUERY-RECORD-NOT-FOUND"),
                (lambda: service.impact("claim:need", max_depth=0), "ECHEL-QUERY-INVALID"),
            )
            for operation, code in cases:
                with self.subTest(code=code):
                    with self.assertRaises(QueryError) as caught:
                        operation()
                    self.assertEqual(code, caught.exception.code)

    def test_stale_index_is_never_used_as_query_authority(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store, _, service = self.make_service(Path(directory))
            claim = store.load("claim", "claim:need")
            changed = deepcopy(claim.record)
            changed["revision"] += 1
            changed["statement"] = "Changed after indexing"
            changed["updated_at"] = "2026-07-15T14:00:00Z"
            store.write(changed, claim.expectation)

            with self.assertRaises(IndexError) as caught:
                service.impact("claim:need")

            self.assertEqual("ECHEL-INDEX-STALE", caught.exception.code)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sqlite3
import sys
from time import perf_counter
from typing import Callable

from echel.storage.index import DisposableIndex, INDEX_FORMAT


GATE_VERSION = "G-M1/v1"
GENERATOR_VERSION = "kernel-synthetic/v1"
QUERY_TARGET_MS = 200.0


@dataclass(frozen=True)
class Timing:
    operation: str
    samples: int
    median_ms: float
    p90_ms: float
    target_ms: float

    @property
    def passed(self) -> bool:
        return self.p90_ms < self.target_ms

    def to_dict(self) -> dict[str, str | int | float | bool]:
        return {
            "operation": self.operation,
            "samples": self.samples,
            "median_ms": round(self.median_ms, 3),
            "p90_ms": round(self.p90_ms, 3),
            "target_ms": self.target_ms,
            "passed": self.passed,
        }


@dataclass(frozen=True)
class KernelGateReport:
    database: Path
    record_count: int
    relationship_count: int
    dataset_digest: str
    build_seconds: float
    database_bytes: int
    timings: tuple[Timing, ...]

    @property
    def passed(self) -> bool:
        return (
            self.record_count >= 1_100_000
            and self.relationship_count >= 1_000_000
            and all(timing.passed for timing in self.timings)
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "gate": GATE_VERSION,
            "generator": GENERATOR_VERSION,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "environment": {
                "python": platform.python_version(),
                "sqlite": sqlite3.sqlite_version,
                "platform": platform.platform(),
            },
            "dataset": {
                "records": self.record_count,
                "relationships": self.relationship_count,
                "digest": self.dataset_digest,
            },
            "build_seconds": round(self.build_seconds, 3),
            "database_bytes": self.database_bytes,
            "timings": [timing.to_dict() for timing in self.timings],
            "passed": self.passed,
            "limitations": [
                "synthetic deterministic kernel dataset, not a product-scenario benchmark",
                "build duration is captured but not gated because hardware classes are not normalized",
                "context compilation and model execution are owned by downstream benchmark tasks",
            ],
        }


def run_kernel_gate(
    database: Path,
    *,
    record_count: int = 100_000,
    relationship_count: int = 1_000_000,
    timing_samples: int = 25,
) -> KernelGateReport:
    if record_count < 100_000 or relationship_count < 1_000_000 or timing_samples < 5:
        raise ValueError("G-M1 requires >=100k records, >=1M relationships, and >=5 timing samples")
    database.parent.mkdir(parents=True, exist_ok=True)
    database.unlink(missing_ok=True)
    started = perf_counter()
    connection = sqlite3.connect(database)
    try:
        DisposableIndex._create_schema(connection)
        connection.executemany(
            "INSERT INTO records VALUES (?, 'claim', 1, ?, ?)",
            (
                (f"claim:r{index}", f"records/claims/r{index}.json", "{}")
                for index in range(record_count)
            ),
        )
        connection.executemany(
            "INSERT INTO records_fts VALUES (?, 'claim', ?)",
            (
                (f"claim:r{index}", "kernel needle" if index % 1000 == 0 else "kernel record")
                for index in range(record_count)
            ),
        )
        connection.executemany(
            "INSERT INTO records VALUES (?, 'relationship', 1, ?, ?)",
            (
                (
                    f"relationship:r{index}",
                    f"records/relationships/r{index}.json",
                    "{}",
                )
                for index in range(relationship_count)
            ),
        )
        connection.executemany(
            "INSERT INTO records_fts VALUES (?, 'relationship', 'affects Synthetic scale edge')",
            ((f"relationship:r{index}",) for index in range(relationship_count)),
        )
        connection.executemany(
            "INSERT INTO relationships VALUES (?, ?, 'affects', ?, 'Synthetic scale edge')",
            (
                (
                    f"relationship:r{index}",
                    f"claim:r{index % record_count}",
                    f"claim:r{(index * 7919) % record_count}",
                )
                for index in range(relationship_count)
            ),
        )
        connection.executemany(
            "INSERT INTO metadata VALUES (?, ?)",
            (("format", INDEX_FORMAT), ("fingerprint", _dataset_digest(record_count, relationship_count))),
        )
        connection.commit()
        build_seconds = perf_counter() - started
        actual_records = connection.execute("SELECT count(*) FROM records").fetchone()[0]
        actual_relationships = connection.execute("SELECT count(*) FROM relationships").fetchone()[0]
        timings = (
            _measure(
                "indexed_status",
                timing_samples,
                lambda: connection.execute(
                    "SELECT (SELECT count(*) FROM records), (SELECT count(*) FROM relationships)"
                ).fetchone(),
            ),
            _measure(
                "full_text_search",
                timing_samples,
                lambda: connection.execute(
                    "SELECT record_id FROM records_fts WHERE records_fts MATCH 'needle' LIMIT 20"
                ).fetchall(),
            ),
            _measure(
                "reverse_link_query",
                timing_samples,
                lambda: connection.execute(
                    "SELECT relationship_id FROM relationships WHERE target = ? LIMIT 100",
                    ("claim:r7919",),
                ).fetchall(),
            ),
        )
    finally:
        connection.close()
    return KernelGateReport(
        database=database,
        record_count=actual_records,
        relationship_count=actual_relationships,
        dataset_digest=_dataset_digest(record_count, relationship_count),
        build_seconds=build_seconds,
        database_bytes=database.stat().st_size,
        timings=timings,
    )


def _measure(operation: str, samples: int, function: Callable[[], object]) -> Timing:
    values = []
    for _ in range(samples):
        started = perf_counter()
        function()
        values.append((perf_counter() - started) * 1000)
    values.sort()
    median = values[len(values) // 2]
    p90 = values[min(len(values) - 1, int(len(values) * 0.9))]
    return Timing(operation, samples, median, p90, QUERY_TARGET_MS)


def _dataset_digest(record_count: int, relationship_count: int) -> str:
    specification = {
        "generator": GENERATOR_VERSION,
        "knowledge_records": record_count,
        "relationships": relationship_count,
        "mapping": "source=i%records,target=(i*7919)%records",
    }
    content = json.dumps(specification, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(content).hexdigest()


def main() -> int:
    destination = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/echel-g-m1.sqlite3")
    report = run_kernel_gate(destination)
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

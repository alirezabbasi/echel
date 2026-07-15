from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import sqlite3
from typing import Any, Iterator
from uuid import uuid4

from echel.storage.records import CanonicalRecordStore, RECORD_LOCATIONS


INDEX_FORMAT = "echel-index/v1"


@dataclass
class IndexError(RuntimeError):
    code: str
    path: Path
    detail: str

    def __str__(self) -> str:
        return f"{self.code} at {self.path}: {self.detail}"

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": str(self.path), "detail": self.detail}


@dataclass(frozen=True)
class IndexBuildResult:
    path: Path
    fingerprint: str
    records: int
    relationships: int

    def to_dict(self) -> dict[str, str | int]:
        return {
            "path": str(self.path),
            "format": INDEX_FORMAT,
            "fingerprint": self.fingerprint,
            "records": self.records,
            "relationships": self.relationships,
        }


@dataclass(frozen=True)
class SearchHit:
    record_id: str
    record_type: str
    revision: int
    path: str

    def to_dict(self) -> dict[str, str | int]:
        return {
            "record_id": self.record_id,
            "record_type": self.record_type,
            "revision": self.revision,
            "path": self.path,
        }


@dataclass(frozen=True)
class RelationshipHit:
    relationship_id: str
    source: str
    predicate: str
    target: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {
            "relationship_id": self.relationship_id,
            "source": self.source,
            "predicate": self.predicate,
            "target": self.target,
            "reason": self.reason,
        }


class DisposableIndex:
    """Rebuildable search and traversal projection of canonical records."""

    def __init__(self, store: CanonicalRecordStore):
        self.store = store
        self.path = store.repository.root / "cache" / "index.sqlite3"

    def rebuild(self) -> IndexBuildResult:
        """Build a complete replacement without changing canonical state."""

        cache = self._safe_cache()
        snapshot = tuple(self._canonical_snapshot())
        fingerprint = self._fingerprint(snapshot)
        temporary = cache / f".index.{uuid4().hex}.tmp"
        relationship_count = 0
        try:
            connection = sqlite3.connect(temporary)
            try:
                self._create_schema(connection)
                for relative_path, content, record in snapshot:
                    searchable = self._searchable_text(record)
                    connection.execute(
                        "INSERT INTO records VALUES (?, ?, ?, ?, ?)",
                        (
                            record["id"],
                            record["record_type"],
                            record["revision"],
                            relative_path,
                            content.decode("utf-8"),
                        ),
                    )
                    connection.execute(
                        "INSERT INTO records_fts VALUES (?, ?, ?)",
                        (record["id"], record["record_type"], searchable),
                    )
                    if record["record_type"] == "relationship":
                        connection.execute(
                            "INSERT INTO relationships VALUES (?, ?, ?, ?, ?)",
                            (
                                record["id"],
                                record["source"],
                                record["predicate"],
                                record["target"],
                                record["reason"],
                            ),
                        )
                        relationship_count += 1
                connection.executemany(
                    "INSERT INTO metadata VALUES (?, ?)",
                    (("format", INDEX_FORMAT), ("fingerprint", fingerprint)),
                )
                connection.commit()
            finally:
                connection.close()
            os.replace(temporary, self.path)
        except (OSError, sqlite3.Error) as exc:
            temporary.unlink(missing_ok=True)
            code = "ECHEL-INDEX-UNSUPPORTED" if "fts5" in str(exc).lower() else "ECHEL-INDEX-BUILD"
            raise IndexError(code, self.path, f"cannot build disposable index: {exc}") from exc
        return IndexBuildResult(self.path, fingerprint, len(snapshot), relationship_count)

    def discard(self) -> bool:
        """Delete only the known disposable database; canonical files are untouched."""

        self._safe_cache()
        existed = self.path.is_file()
        try:
            self.path.unlink(missing_ok=True)
        except OSError as exc:
            raise IndexError("ECHEL-INDEX-DISCARD", self.path, str(exc)) from exc
        return existed

    def assert_current(self) -> None:
        """Validate that this projection still represents current canonical bytes."""

        with self._open_current():
            pass

    def search(
        self, query: str, *, record_type: str | None = None, limit: int = 20
    ) -> tuple[SearchHit, ...]:
        if not isinstance(query, str) or not query.strip():
            raise IndexError("ECHEL-INDEX-QUERY-INVALID", self.path, "query must not be blank")
        if record_type is not None and record_type not in RECORD_LOCATIONS:
            raise IndexError(
                "ECHEL-INDEX-QUERY-INVALID", self.path, f"unknown record type {record_type!r}"
            )
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
            raise IndexError(
                "ECHEL-INDEX-QUERY-INVALID", self.path, "limit must be an integer from 1 through 100"
            )
        with self._open_current() as connection:
            where = "records_fts MATCH ?"
            parameters: list[str | int] = [query.strip()]
            if record_type is not None:
                where += " AND r.record_type = ?"
                parameters.append(record_type)
            parameters.append(limit)
            try:
                rows = connection.execute(
                    f"""SELECT r.record_id, r.record_type, r.revision, r.path
                        FROM records_fts f JOIN records r USING (record_id)
                        WHERE {where}
                        ORDER BY bm25(records_fts), r.record_id LIMIT ?""",  # nosec B608
                    parameters,
                ).fetchall()
            except sqlite3.Error as exc:
                raise IndexError(
                    "ECHEL-INDEX-QUERY-INVALID", self.path, f"invalid full-text query: {exc}"
                ) from exc
        return tuple(SearchHit(*row) for row in rows)

    def related(
        self, record_id: str, *, direction: str = "both", predicate: str | None = None
    ) -> tuple[RelationshipHit, ...]:
        if direction not in {"in", "out", "both"}:
            raise IndexError(
                "ECHEL-INDEX-QUERY-INVALID", self.path, "direction must be 'in', 'out', or 'both'"
            )
        if not isinstance(record_id, str) or not record_id.strip():
            raise IndexError("ECHEL-INDEX-QUERY-INVALID", self.path, "record_id must not be blank")
        clauses = []
        parameters: list[str] = []
        if direction in {"out", "both"}:
            clauses.append("source = ?")
            parameters.append(record_id)
        if direction in {"in", "both"}:
            clauses.append("target = ?")
            parameters.append(record_id)
        where = "(" + " OR ".join(clauses) + ")"
        if predicate is not None:
            if not predicate.strip():
                raise IndexError(
                    "ECHEL-INDEX-QUERY-INVALID", self.path, "predicate must not be blank"
                )
            where += " AND predicate = ?"
            parameters.append(predicate)
        with self._open_current() as connection:
            rows = connection.execute(
                f"""SELECT relationship_id, source, predicate, target, reason
                    FROM relationships WHERE {where}
                    ORDER BY relationship_id""",  # nosec B608
                parameters,
            ).fetchall()
        return tuple(RelationshipHit(*row) for row in rows)

    def _canonical_snapshot(self) -> Iterator[tuple[str, bytes, dict[str, Any]]]:
        records = []
        for record_type in RECORD_LOCATIONS:
            for loaded in self.store.scan(record_type):
                content = loaded.path.read_bytes()
                try:
                    record = json.loads(content)
                    self.store.schemas.validate(record)
                except (UnicodeDecodeError, json.JSONDecodeError, RuntimeError) as exc:
                    raise IndexError(
                        "ECHEL-INDEX-SOURCE-INVALID",
                        loaded.path,
                        "canonical source cannot be indexed until it is repaired",
                    ) from exc
                if record.get("record_type") != record_type or record.get("id") != loaded.record["id"]:
                    raise IndexError(
                        "ECHEL-INDEX-SOURCE-INVALID",
                        loaded.path,
                        "canonical identity changed while the index snapshot was read; retry rebuild",
                    )
                relative = loaded.path.relative_to(self.store.repository.root).as_posix()
                records.append((relative, content, record))
        yield from sorted(records, key=lambda item: item[0])

    @staticmethod
    def _fingerprint(snapshot: tuple[tuple[str, bytes, dict[str, Any]], ...]) -> str:
        digest = hashlib.sha256()
        for relative_path, content, _ in snapshot:
            digest.update(relative_path.encode())
            digest.update(b"\0")
            digest.update(content)
            digest.update(b"\0")
        return "sha256:" + digest.hexdigest()

    @staticmethod
    def _searchable_text(record: dict[str, Any]) -> str:
        values: list[str] = []

        def collect(value: Any) -> None:
            if isinstance(value, str):
                values.append(value)
            elif isinstance(value, list):
                for item in value:
                    collect(item)
            elif isinstance(value, dict):
                for key in sorted(value):
                    if key != "extensions":
                        collect(value[key])

        collect(record)
        return "\n".join(values)

    def _safe_cache(self) -> Path:
        cache = self.store.repository.root / "cache"
        if not cache.is_dir() or not cache.resolve().is_relative_to(self.store.repository.root):
            raise IndexError(
                "ECHEL-INDEX-PATH-UNSAFE", cache, "cache must be a directory inside .echel"
            )
        return cache

    @contextmanager
    def _open_current(self) -> Iterator[sqlite3.Connection]:
        self._safe_cache()
        if not self.path.is_file():
            raise IndexError(
                "ECHEL-INDEX-NOT-BUILT", self.path, "build the disposable index before querying"
            )
        try:
            connection = sqlite3.connect(f"file:{self.path}?mode=ro", uri=True)
            metadata = dict(connection.execute("SELECT key, value FROM metadata"))
        except sqlite3.Error as exc:
            try:
                connection.close()
            except UnboundLocalError:
                pass
            raise IndexError(
                "ECHEL-INDEX-CORRUPT", self.path, "discard and rebuild the disposable index"
            ) from exc
        if metadata.get("format") != INDEX_FORMAT:
            connection.close()
            raise IndexError(
                "ECHEL-INDEX-FORMAT-UNSUPPORTED", self.path, "discard and rebuild the index"
            )
        current = self._fingerprint(tuple(self._canonical_snapshot()))
        if metadata.get("fingerprint") != current:
            connection.close()
            raise IndexError(
                "ECHEL-INDEX-STALE", self.path, "canonical records changed; rebuild the index"
            )
        try:
            yield connection
        finally:
            connection.close()

    @staticmethod
    def _create_schema(connection: sqlite3.Connection) -> None:
        connection.executescript(
            """
            PRAGMA journal_mode = DELETE;
            PRAGMA synchronous = FULL;
            CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE records (
                record_id TEXT PRIMARY KEY,
                record_type TEXT NOT NULL,
                revision INTEGER NOT NULL,
                path TEXT NOT NULL,
                content_json TEXT NOT NULL
            );
            CREATE VIRTUAL TABLE records_fts USING fts5(
                record_id UNINDEXED, record_type UNINDEXED, content
            );
            CREATE TABLE relationships (
                relationship_id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                predicate TEXT NOT NULL,
                target TEXT NOT NULL,
                reason TEXT NOT NULL
            );
            CREATE INDEX relationship_sources ON relationships(source, predicate);
            CREATE INDEX relationship_targets ON relationships(target, predicate);
            """
        )

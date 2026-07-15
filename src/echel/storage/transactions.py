from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
from typing import Any
from uuid import uuid4

from echel.domain import Identifier
from echel.storage.layout import RepositoryError
from echel.storage.records import CanonicalRecordStore, RecordExpectation, RecordWritePlan


@dataclass(frozen=True)
class TransactionPlan:
    transaction_id: str
    journal: Path
    record_ids: tuple[str, ...]
    changed_records: int

    def to_dict(self) -> dict[str, str | int | list[str]]:
        return {
            "transaction_id": self.transaction_id,
            "journal": str(self.journal),
            "record_ids": list(self.record_ids),
            "changed_records": self.changed_records,
        }


@dataclass(frozen=True)
class TransactionResult:
    transaction_id: str
    outcome: str
    record_count: int

    def to_dict(self) -> dict[str, str | int]:
        return {
            "transaction_id": self.transaction_id,
            "outcome": self.outcome,
            "record_count": self.record_count,
        }


class TransactionJournal:
    """Durable commit intent and deterministic recovery for multi-record writes."""

    VERSION = 1

    def __init__(self, store: CanonicalRecordStore):
        self.store = store
        self.root = store.repository.root / "transactions"

    def preview(self, transaction_id: str, records: list[dict[str, Any]]) -> TransactionPlan:
        identifier = self._identifier(transaction_id)
        plans = self._record_plans(records)
        return TransactionPlan(
            transaction_id=str(identifier),
            journal=self.root / identifier.local / "journal.json",
            record_ids=tuple(plan.record_id for plan in plans),
            changed_records=sum(plan.changed for plan in plans),
        )

    def prepare(self, transaction_id: str, records: list[dict[str, Any]]) -> TransactionPlan:
        """Durably stage valid intent without changing canonical records."""

        plan = self.preview(transaction_id, records)
        transaction = plan.journal.parent
        if transaction.exists():
            raise RepositoryError(
                "ECHEL-TRANSACTION-EXISTS", transaction, "recover or roll back the existing transaction"
            )
        record_plans = self._record_plans(records)
        temporary = self.root / f".{transaction.name}.{uuid4().hex}.tmp"
        try:
            staged = temporary / "staged"
            staged.mkdir(parents=True)
            entries = []
            for index, record_plan in enumerate(record_plans):
                staged_name = f"{index:04d}.json"
                staged_path = staged / staged_name
                self._write_new(staged_path, record_plan.content)
                entries.append(
                    {
                        "record_id": record_plan.record_id,
                        "path": str(record_plan.path.relative_to(self.store.repository.root)),
                        "digest": record_plan.digest,
                        "expected": record_plan.expectation.to_dict(),
                        "staged": staged_name,
                    }
                )
            self._write_new(
                temporary / "journal.json",
                self._json_bytes(
                    {
                        "version": self.VERSION,
                        "transaction_id": transaction_id,
                        "state": "prepared",
                        "records": entries,
                    }
                ),
            )
            self._sync_directory(staged)
            self._sync_directory(temporary)
            self.root.mkdir(exist_ok=True)
            os.replace(temporary, transaction)
            self._sync_directory(self.root)
        except OSError as exc:
            shutil.rmtree(temporary, ignore_errors=True)
            raise RepositoryError("ECHEL-TRANSACTION-PREPARE", transaction, str(exc)) from exc
        return plan

    def commit(self, transaction_id: str) -> TransactionResult:
        """Record the commit decision, apply all records, and clear the journal."""

        transaction = self._transaction_path(transaction_id)
        journal = self._load_journal(transaction)
        state = journal.get("state")
        if state not in {"prepared", "committing"}:
            raise RepositoryError(
                "ECHEL-TRANSACTION-STATE", transaction, f"cannot commit transaction in state {state!r}"
            )
        try:
            if state == "prepared":
                journal["state"] = "committing"
                self._replace_journal(transaction, journal)
            self._apply(transaction, journal)
            journal["state"] = "committed"
            self._replace_journal(transaction, journal)
        except (OSError, RepositoryError, ValueError) as exc:
            raise RepositoryError(
                "ECHEL-TRANSACTION-INCOMPLETE",
                transaction,
                "commit intent is durable; run recovery to finish: " + str(exc),
            ) from exc
        count = len(journal["records"])
        shutil.rmtree(transaction)
        self._sync_directory(self.root)
        return TransactionResult(transaction_id, "committed", count)

    def execute(self, transaction_id: str, records: list[dict[str, Any]]) -> TransactionResult:
        self.prepare(transaction_id, records)
        return self.commit(transaction_id)

    def rollback(self, transaction_id: str) -> TransactionResult:
        """Discard prepared intent; a durable commit decision is never reversed implicitly."""

        transaction = self._transaction_path(transaction_id)
        journal = self._load_journal(transaction)
        if journal.get("state") != "prepared":
            raise RepositoryError(
                "ECHEL-TRANSACTION-COMMIT-DECIDED",
                transaction,
                "committing transactions must roll forward through recovery",
            )
        count = len(journal["records"])
        shutil.rmtree(transaction)
        self._sync_directory(self.root)
        return TransactionResult(transaction_id, "rolled_back", count)

    def recover(self) -> list[TransactionResult]:
        """Rollback uncommitted preparation and roll forward durable commit decisions."""

        if not self.root.exists():
            return []
        results = []
        for transaction in sorted(path for path in self.root.iterdir() if path.is_dir()):
            if transaction.name.startswith("."):
                shutil.rmtree(transaction)
                self._sync_directory(self.root)
                continue
            journal = self._load_journal(transaction)
            transaction_id = str(journal.get("transaction_id", ""))
            state = journal.get("state")
            if state == "prepared":
                results.append(self.rollback(transaction_id))
            elif state == "committing":
                results.append(self.commit(transaction_id))
            elif state == "committed":
                count = len(journal["records"])
                shutil.rmtree(transaction)
                self._sync_directory(self.root)
                results.append(TransactionResult(transaction_id, "cleaned", count))
            else:
                raise RepositoryError(
                    "ECHEL-TRANSACTION-STATE", transaction, f"unknown transaction state {state!r}"
                )
        return results

    def _record_plans(self, records: list[dict[str, Any]]) -> list[RecordWritePlan]:
        if not records:
            raise RepositoryError(
                "ECHEL-TRANSACTION-EMPTY", self.root, "a transaction requires at least one record"
            )
        plans = [self.store.preview_write(record, self.store.observe(record)) for record in records]
        paths = [plan.path for plan in plans]
        if len(paths) != len(set(paths)):
            raise RepositoryError(
                "ECHEL-TRANSACTION-DUPLICATE", self.root, "a transaction cannot target one record twice"
            )
        return plans

    def _apply(self, transaction: Path, journal: dict[str, Any]) -> None:
        for entry in journal["records"]:
            staged = transaction / "staged" / entry["staged"]
            content = staged.read_bytes()
            digest = "sha256:" + hashlib.sha256(content).hexdigest()
            if digest != entry["digest"]:
                raise RepositoryError(
                    "ECHEL-TRANSACTION-STAGED-CORRUPT", staged, "staged content digest does not match"
                )
            record = json.loads(content)
            expected_data = entry.get("expected")
            if not isinstance(expected_data, dict):
                raise RepositoryError(
                    "ECHEL-TRANSACTION-JOURNAL", transaction / "journal.json", "missing precondition"
                )
            expectation = RecordExpectation(
                revision=expected_data.get("revision"), digest=expected_data.get("digest")
            )
            plan = self.store.preview_write(record, expectation)
            expected = self.store.repository.root / entry["path"]
            if plan.path != expected or plan.record_id != entry["record_id"]:
                raise RepositoryError(
                    "ECHEL-TRANSACTION-STAGED-CORRUPT", staged, "staged record identity or path changed"
                )
            self.store.write(record, expectation)

    def _transaction_path(self, transaction_id: str) -> Path:
        identifier = self._identifier(transaction_id)
        return self.root / identifier.local

    @staticmethod
    def _identifier(transaction_id: str) -> Identifier:
        identifier = Identifier(transaction_id)
        if identifier.namespace != "transaction":
            raise RepositoryError(
                "ECHEL-TRANSACTION-ID", Path(transaction_id), "must use transaction:local form"
            )
        return identifier

    @staticmethod
    def _json_bytes(payload: dict[str, Any]) -> bytes:
        return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()

    @staticmethod
    def _write_new(path: Path, content: bytes) -> None:
        with path.open("xb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())

    def _replace_journal(self, transaction: Path, journal: dict[str, Any]) -> None:
        temporary = transaction / f".journal.{uuid4().hex}.tmp"
        try:
            self._write_new(temporary, self._json_bytes(journal))
            os.replace(temporary, transaction / "journal.json")
            self._sync_directory(transaction)
        finally:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass

    @staticmethod
    def _load_journal(transaction: Path) -> dict[str, Any]:
        path = transaction / "journal.json"
        try:
            journal = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            raise RepositoryError("ECHEL-TRANSACTION-JOURNAL", path, str(exc)) from exc
        if (
            not isinstance(journal, dict)
            or journal.get("version") != 1
            or not isinstance(journal.get("records"), list)
            or journal.get("state") not in {"prepared", "committing", "committed"}
        ):
            raise RepositoryError("ECHEL-TRANSACTION-JOURNAL", path, "unsupported journal format")
        return journal

    @staticmethod
    def _sync_directory(path: Path) -> None:
        """Persist directory entries where the platform supports directory fsync."""

        descriptor: int | None = None
        try:
            descriptor = os.open(path, os.O_RDONLY)
            os.fsync(descriptor)
        except OSError:
            pass
        finally:
            if descriptor is not None:
                os.close(descriptor)

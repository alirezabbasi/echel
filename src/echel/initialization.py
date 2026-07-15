from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
from typing import Any, Callable
from uuid import uuid4

from echel.domain.value_objects import Identifier
from echel.profiles import ProfileError, get_profile
from echel.schemas import SchemaRegistry
from echel.storage import (
    CanonicalRecordStore,
    CanonicalRepository,
    RECORD_COLLECTIONS,
    RecordExpectation,
)


INIT_CONTRACT = "idea-init/v1"
CONFIG_KEY = re.compile(r"^[a-z][a-z0-9_.-]{0,63}$")
SECRET_KEYS = frozenset({"password", "passwd", "secret", "token", "api_key", "private_key"})
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
)


@dataclass
class InitializationError(RuntimeError):
    code: str
    field: str
    detail: str
    remedy: str

    def __str__(self) -> str:
        return f"{self.code} at /{self.field}: {self.detail}; remedy: {self.remedy}"

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "field": self.field,
            "detail": self.detail,
            "remedy": self.remedy,
        }


@dataclass(frozen=True)
class IdeaInitializationPlan:
    workspace: Path
    project: dict[str, Any]
    idea: dict[str, Any]
    digest: str

    def to_dict(self) -> dict[str, Any]:
        metadata = self.project["extensions"]["dev.echel.initialization"]
        return {
            "contract": INIT_CONTRACT,
            "workspace": str(self.workspace),
            "project_id": self.project["id"],
            "idea_id": self.idea["id"],
            "owner": metadata["owner"],
            "profile": self.project["profile"],
            "config": metadata["config"],
            "records": [self.project["id"], self.idea["id"]],
            "digest": self.digest,
            "mutation": "preview",
            "next_action": "Review the captured idea, then define the problem.",
        }


@dataclass(frozen=True)
class IdeaInitializationResult:
    project_id: str
    idea_id: str
    owner: str
    profile: str
    config: dict[str, str]
    digest: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract": INIT_CONTRACT,
            "project_id": self.project_id,
            "idea_id": self.idea_id,
            "owner": self.owner,
            "profile": self.profile,
            "config": self.config,
            "records_created": 2,
            "digest": self.digest,
            "mutation": "applied",
            "next_action": "Review the captured idea, then define the problem.",
        }


class IdeaInitializationService:
    """Atomically create only the truthful minimum for one raw idea."""

    def __init__(
        self,
        schemas: SchemaRegistry | None = None,
        clock: Callable[[], datetime] | None = None,
    ):
        self.schemas = schemas or SchemaRegistry()
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def preview(
        self,
        workspace: Path,
        name: str,
        idea: str,
        owner: str,
        profile: str = "prototype",
        config: dict[str, str] | None = None,
        project_id: str | None = None,
    ) -> IdeaInitializationPlan:
        root = self._workspace(workspace)
        project_name = self._text(name, "name", 200)
        idea_text = self._text(idea, "idea", 10_000)
        owner_id = self._owner(owner)
        try:
            get_profile(profile)
        except ProfileError as exc:
            raise InitializationError(
                "ECHEL-INIT-PROFILE-INVALID",
                "profile",
                exc.detail,
                "select prototype, product, production, or regulated",
            ) from exc
        safe_config = self._config(config or {})
        self._reject_secret("idea", idea_text)
        identifier = self._project_identifier(project_id, project_name)
        timestamp = self.clock().astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        provenance = {
            "actor": str(owner_id),
            "origin": "echel init --mode idea",
            "method": "human",
        }
        project: dict[str, Any] = {
            "schema_version": 1,
            "record_type": "project",
            "id": str(identifier),
            "revision": 1,
            "created_at": timestamp,
            "updated_at": timestamp,
            "provenance": provenance,
            "name": project_name,
            "mode": "idea",
            "maturity": "idea",
            "profile": profile,
            "extensions": {
                "dev.echel.initialization": {
                    "contract": INIT_CONTRACT,
                    "owner": str(owner_id),
                    "config": safe_config,
                }
            },
        }
        idea_record: dict[str, Any] = {
            "schema_version": 1,
            "record_type": "claim",
            "id": f"claim:{identifier.local}-idea",
            "revision": 1,
            "created_at": timestamp,
            "updated_at": timestamp,
            "provenance": provenance,
            "kind": "raw-idea",
            "stage": "idea",
            "statement": idea_text,
            "status": "proposed",
            "confidence": 1.0,
        }
        self.schemas.validate(project)
        self.schemas.validate(idea_record)
        digest = self._digest(project, idea_record)
        return IdeaInitializationPlan(root, project, idea_record, digest)

    def apply(self, plan: IdeaInitializationPlan) -> IdeaInitializationResult:
        workspace = self._workspace(plan.workspace)
        if self._digest(plan.project, plan.idea) != plan.digest:
            raise InitializationError(
                "ECHEL-INIT-PLAN-INVALID",
                "plan",
                "previewed initialization records were modified",
                "discard the plan and preview initialization again",
            )
        self.schemas.validate(plan.project)
        self.schemas.validate(plan.idea)
        temporary = workspace / f".echel.init-{uuid4().hex}.tmp"
        destination = workspace / ".echel"
        try:
            records = temporary / "records"
            for collection in RECORD_COLLECTIONS:
                (records / collection).mkdir(parents=True)
            (temporary / "cache").mkdir()
            repository = CanonicalRepository(workspace=workspace, root=temporary)
            store = CanonicalRecordStore(repository, self.schemas)
            store.write(plan.project, RecordExpectation.absent())
            store.write(plan.idea, RecordExpectation.absent())
            os.replace(temporary, destination)
            self._sync_directory(workspace)
        except (OSError, RuntimeError, ValueError) as exc:
            shutil.rmtree(temporary, ignore_errors=True)
            if isinstance(exc, InitializationError):
                raise
            raise InitializationError(
                "ECHEL-INIT-APPLY",
                "workspace",
                str(exc),
                "resolve the conflict or filesystem error and retry; no project state was published",
            ) from exc
        metadata = plan.project["extensions"]["dev.echel.initialization"]
        return IdeaInitializationResult(
            project_id=str(plan.project["id"]),
            idea_id=str(plan.idea["id"]),
            owner=str(metadata["owner"]),
            profile=str(plan.project["profile"]),
            config=dict(metadata["config"]),
            digest=plan.digest,
        )

    @staticmethod
    def parse_config(values: list[str]) -> dict[str, str]:
        config = {}
        for value in values:
            if "=" not in value:
                raise InitializationError(
                    "ECHEL-INIT-CONFIG-INVALID",
                    "config",
                    f"{value!r} must use key=value form",
                    "provide a non-secret setting such as locale=en",
                )
            key, item = value.split("=", 1)
            if key in config:
                raise InitializationError(
                    "ECHEL-INIT-CONFIG-INVALID",
                    "config",
                    f"duplicate configuration key {key!r}",
                    "provide each configuration key once",
                )
            config[key] = item
        return config

    @staticmethod
    def _workspace(workspace: Path) -> Path:
        root = workspace.expanduser().resolve()
        if not root.is_dir() or not ((root / ".git").is_dir() or (root / ".git").is_file()):
            raise InitializationError(
                "ECHEL-INIT-REPOSITORY-REQUIRED",
                "workspace",
                "idea initialization must run at an existing Git repository root",
                "create or select a Git repository and run the command at its root",
            )
        if (root / ".echel").exists() or (root / ".echel").is_symlink():
            raise InitializationError(
                "ECHEL-INIT-EXISTS",
                "workspace",
                "Echel is already initialized",
                "open the existing project instead of initializing again",
            )
        return root

    @staticmethod
    def _text(value: str, field: str, maximum: int) -> str:
        if not isinstance(value, str) or not value.strip() or len(value.strip()) > maximum:
            raise InitializationError(
                "ECHEL-INIT-INPUT-INVALID",
                field,
                f"must be non-empty and at most {maximum} characters",
                f"provide a concise {field}",
            )
        return value.strip()

    @staticmethod
    def _owner(value: str) -> Identifier:
        try:
            owner = Identifier(value)
        except (TypeError, ValueError) as exc:
            raise InitializationError(
                "ECHEL-INIT-OWNER-INVALID",
                "owner",
                str(exc),
                "provide the responsible person as user:local-id",
            ) from exc
        if owner.namespace != "user":
            raise InitializationError(
                "ECHEL-INIT-OWNER-INVALID",
                "owner",
                "initial decision authority must use the user namespace",
                "provide the responsible person as user:local-id",
            )
        return owner

    @staticmethod
    def _project_identifier(value: str | None, name: str) -> Identifier:
        candidate = value or "project:" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        try:
            identifier = Identifier(candidate)
        except (TypeError, ValueError) as exc:
            raise InitializationError(
                "ECHEL-INIT-ID-INVALID",
                "project_id",
                str(exc),
                "provide --id in project:local-id form",
            ) from exc
        if identifier.namespace != "project" or len(identifier.local) > 140:
            raise InitializationError(
                "ECHEL-INIT-ID-INVALID",
                "project_id",
                "project id must use project:local-id form with a local part of at most 140 characters",
                "provide a shorter --id in project:local-id form",
            )
        return identifier

    def _config(self, config: dict[str, str]) -> dict[str, str]:
        if len(config) > 50:
            raise InitializationError(
                "ECHEL-INIT-CONFIG-INVALID",
                "config",
                "at most 50 initial settings are allowed",
                "keep only settings required before problem discovery",
            )
        normalized = {}
        for key, value in sorted(config.items()):
            if not isinstance(key, str) or CONFIG_KEY.fullmatch(key) is None or not isinstance(value, str):
                raise InitializationError(
                    "ECHEL-INIT-CONFIG-INVALID",
                    "config",
                    "keys must be lowercase identifiers and values must be strings",
                    "use non-secret key=value settings with lowercase keys",
                )
            if key.replace("-", "_").split(".")[-1] in SECRET_KEYS:
                raise InitializationError(
                    "ECHEL-INIT-SECRET-DENIED",
                    "config",
                    f"configuration key {key!r} appears to contain secret material",
                    "store the secret in an external secret manager and keep only a safe reference",
                )
            self._reject_secret("config", value)
            normalized[key] = value
        return normalized

    @staticmethod
    def _reject_secret(field: str, value: str) -> None:
        if any(pattern.search(value) for pattern in SECRET_PATTERNS):
            raise InitializationError(
                "ECHEL-INIT-SECRET-DENIED",
                field,
                "input appears to contain secret material and was not persisted",
                "remove the secret and use an external secret-manager reference",
            )

    @staticmethod
    def _digest(project: dict[str, Any], idea: dict[str, Any]) -> str:
        content = json.dumps(
            [project, idea], sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
        return "sha256:" + hashlib.sha256(content).hexdigest()

    @staticmethod
    def _sync_directory(path: Path) -> None:
        descriptor: int | None = None
        try:
            descriptor = os.open(path, os.O_RDONLY)
            os.fsync(descriptor)
        except OSError:
            pass
        finally:
            if descriptor is not None:
                os.close(descriptor)

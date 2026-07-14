from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
from uuid import uuid4


RECORD_COLLECTIONS = (
    "claims",
    "decisions",
    "relationships",
    "findings",
    "work",
    "tasks",
    "runs",
    "evidence",
    "releases",
    "learnings",
)


@dataclass(frozen=True)
class RepositoryError(RuntimeError):
    code: str
    path: Path
    detail: str

    def __str__(self) -> str:
        return f"{self.code} at {self.path}: {self.detail}"


@dataclass(frozen=True)
class CanonicalRepository:
    """Resolved paths for one repository-owned canonical Echel store."""

    workspace: Path
    root: Path

    @property
    def records(self) -> Path:
        return self.root / "records"

    def collection(self, name: str) -> Path:
        if name not in RECORD_COLLECTIONS:
            raise RepositoryError(
                "ECHEL-COLLECTION-UNKNOWN", self.records / name, f"known collections: {RECORD_COLLECTIONS}"
            )
        return self.records / name

    @classmethod
    def discover(cls, start: Path) -> CanonicalRepository:
        """Open Echel state at the containing Git root without searching above it."""

        location = start.expanduser().resolve()
        if location.is_file():
            location = location.parent
        workspace = _find_git_root(location)
        root = workspace / ".echel"
        if not root.exists():
            raise RepositoryError(
                "ECHEL-PROJECT-NOT-FOUND",
                root,
                "initialize Echel at this repository root before opening it",
            )
        resolved_root = root.resolve()
        if not resolved_root.is_relative_to(workspace):
            raise RepositoryError(
                "ECHEL-REPOSITORY-ESCAPE",
                root,
                ".echel resolves outside its containing repository",
            )
        repository = cls(workspace=workspace, root=resolved_root)
        repository._validate_layout()
        return repository

    @classmethod
    def create(cls, workspace: Path) -> CanonicalRepository:
        """Create the deterministic directory contract, or leave no partial store."""

        resolved_workspace = workspace.expanduser().resolve()
        git_root = _find_git_root(resolved_workspace)
        if git_root != resolved_workspace:
            raise RepositoryError(
                "ECHEL-INIT-NOT-ROOT",
                resolved_workspace,
                f"initialize at repository root {git_root}",
            )
        root = git_root / ".echel"
        if root.exists() or root.is_symlink():
            raise RepositoryError("ECHEL-PROJECT-EXISTS", root, "Echel state already exists")

        temporary = git_root / f".echel.tmp-{uuid4().hex}"
        try:
            records = temporary / "records"
            for collection in RECORD_COLLECTIONS:
                (records / collection).mkdir(parents=True)
            (temporary / "cache").mkdir()
            temporary.replace(root)
        except OSError as exc:
            shutil.rmtree(temporary, ignore_errors=True)
            raise RepositoryError("ECHEL-LAYOUT-CREATE", root, str(exc)) from exc
        return cls(workspace=git_root, root=root)

    def _validate_layout(self) -> None:
        required = (self.records, *(self.records / name for name in RECORD_COLLECTIONS))
        missing = [path for path in required if not path.is_dir()]
        if missing:
            raise RepositoryError(
                "ECHEL-LAYOUT-INVALID",
                missing[0],
                "required canonical record directory is missing",
            )
        for path in required:
            if not path.resolve().is_relative_to(self.workspace):
                raise RepositoryError(
                    "ECHEL-REPOSITORY-ESCAPE",
                    path,
                    "canonical collection resolves outside its repository",
                )


def _find_git_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        marker = candidate / ".git"
        if marker.is_dir() or marker.is_file():
            return candidate
    raise RepositoryError(
        "ECHEL-REPOSITORY-NOT-FOUND",
        start,
        "no containing Git repository was found",
    )

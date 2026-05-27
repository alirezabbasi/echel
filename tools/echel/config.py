from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


CONFIG_FILE = "project.echel"
REQUIRED_ROOT_KEYS = ("SRC_ROOT", "LANG_ROOT", "MEMORY_ROOT")


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class ProjectConfig:
    version: int
    roots: dict[str, str]
    migration_map: dict[str, str]
    gate_policy: str
    evidence_registry: str

    @property
    def path(self) -> Path:
        return Path(CONFIG_FILE)


DEFAULT_CONFIG = {
    "version": 2,
    "roots": {
        "SRC_ROOT": ".",
        "LANG_ROOT": "tools",
        "MEMORY_ROOT": "docs/development/state",
        "WIKI_ROOT": "wiki",
    },
    "migration_map": {},
    "gate_policy": ".echel/gates.json",
    "evidence_registry": ".echel/evidence_registry.json",
}


def write_default_config(path: Path) -> None:
    path.write_text(json.dumps(DEFAULT_CONFIG, indent=2) + "\n", encoding="utf-8")


def _err(msg: str) -> ConfigError:
    return ConfigError(f"{CONFIG_FILE}: {msg}")


def load_config(root: Path | None = None) -> ProjectConfig:
    root_dir = root or Path.cwd()
    cfg_path = root_dir / CONFIG_FILE
    if not cfg_path.exists():
        write_default_config(cfg_path)

    try:
        raw = json.loads(cfg_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise _err(f"invalid JSON ({exc})") from exc

    if not isinstance(raw, dict):
        raise _err("top-level object must be a mapping")

    version = raw.get("version")
    if version != 2:
        raise _err("field 'version' must equal 2")

    roots = raw.get("roots")
    if not isinstance(roots, dict):
        raise _err("field 'roots' must be a mapping")

    for key in REQUIRED_ROOT_KEYS:
        val = roots.get(key)
        if not isinstance(val, str) or not val:
            raise _err(f"roots.{key} must be a non-empty string")
    if "WIKI_ROOT" not in roots:
        roots["WIKI_ROOT"] = "wiki"

    migration_map = raw.get("migration_map", {})
    if not isinstance(migration_map, dict):
        raise _err("field 'migration_map' must be a mapping")
    for k, v in migration_map.items():
        if not isinstance(k, str) or not isinstance(v, str):
            raise _err("migration_map keys and values must be strings")

    gate_policy = raw.get("gate_policy")
    if not isinstance(gate_policy, str) or not gate_policy:
        raise _err("field 'gate_policy' must be a non-empty string")

    evidence_registry = raw.get("evidence_registry")
    if not isinstance(evidence_registry, str) or not evidence_registry:
        raise _err("field 'evidence_registry' must be a non-empty string")

    return ProjectConfig(
        version=version,
        roots={k: str(v) for k, v in roots.items()},
        migration_map={str(k): str(v) for k, v in migration_map.items()},
        gate_policy=gate_policy,
        evidence_registry=evidence_registry,
    )


def resolve_root_map(cfg: ProjectConfig, base_dir: Path | None = None) -> dict[str, Path]:
    base = base_dir or Path.cwd()
    resolved: dict[str, Path] = {}
    for name, rel in cfg.roots.items():
        resolved[name] = (base / rel).resolve()
    return resolved


def resolve_symbolic_path(path_expr: str, cfg: ProjectConfig, base_dir: Path | None = None) -> Path:
    if not isinstance(path_expr, str):
        raise ValueError("path expression must be string")

    resolved_roots = resolve_root_map(cfg, base_dir=base_dir)
    for key, root in resolved_roots.items():
        token = f"${key}"
        if path_expr == token:
            return root
        if path_expr.startswith(token + "/"):
            suffix = path_expr[len(token) + 1 :]
            return (root / suffix).resolve()
    base = base_dir or Path.cwd()
    return (base / path_expr).resolve()


def apply_migration_map(text: str, cfg: ProjectConfig) -> str:
    out = text
    for old, new in cfg.migration_map.items():
        out = out.replace(old, new)
    return out


def to_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True)

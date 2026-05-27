from __future__ import annotations

import json
from pathlib import Path


def project_config(root: Path | None = None) -> dict:
    base = root or Path.cwd()
    path = base / "project.echel"
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return raw if isinstance(raw, dict) else {}


def configured_root(name: str, default: str, root: Path | None = None) -> Path:
    base = root or Path.cwd()
    cfg = project_config(base)
    roots = cfg.get("roots", {})
    rel = roots.get(name, default) if isinstance(roots, dict) else default
    return (base / str(rel)).resolve()

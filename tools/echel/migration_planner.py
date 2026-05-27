from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
import re

from .config import load_config, resolve_symbolic_path


TASK_REF_RE = re.compile(r'\bTASK-\d{4}\b')


@dataclass
class Wave:
    wave: int
    tasks: list[str]
    risk_score: int


def _task_id(path: Path) -> str | None:
    m = re.match(r'(TASK-\d{4})-', path.name)
    return m.group(1) if m else None


def _build_graph(task_files: list[Path]) -> tuple[dict[str, set[str]], dict[str, int]]:
    deps: dict[str, set[str]] = {}
    indeg: dict[str, int] = {}
    existing: set[str] = set()
    for p in task_files:
        tid = _task_id(p)
        if tid:
            existing.add(tid)
    for p in task_files:
        tid = _task_id(p)
        if not tid:
            continue
        refs = set(TASK_REF_RE.findall(p.read_text(encoding='utf-8')))
        refs.discard(tid)
        refs = {r for r in refs if r in existing}
        deps[tid] = refs
    for t in existing:
        indeg[t] = 0
    for t, rs in deps.items():
        for r in rs:
            indeg[t] += 1
    return deps, indeg


def plan_waves(repo_root: Path) -> list[Wave]:
    cfg = load_config(repo_root)
    wiki_root = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)
    files = sorted((wiki_root / 'work').glob('TASK-*.md'))
    deps, indeg = _build_graph(files)
    rev = defaultdict(set)
    for t, rs in deps.items():
        for r in rs:
            rev[r].add(t)

    q = deque(sorted([n for n, d in indeg.items() if d == 0]))
    done: set[str] = set()
    waves: list[Wave] = []
    wave_num = 1
    while q:
        current = list(q)
        q.clear()
        for n in current:
            done.add(n)
        for n in current:
            for out in rev[n]:
                indeg[out] -= 1
                if indeg[out] == 0:
                    q.append(out)
        q = deque(sorted(set(q)))
        risk = sum(len(rev[n]) + len(deps[n]) for n in current)
        waves.append(Wave(wave=wave_num, tasks=sorted(current), risk_score=risk))
        wave_num += 1

    remaining = sorted(set(indeg) - done)
    if remaining:
        waves.append(Wave(wave=wave_num, tasks=remaining, risk_score=100 + len(remaining)))
    return waves

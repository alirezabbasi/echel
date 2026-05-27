from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import subprocess

from .config import load_config, resolve_symbolic_path


FIXTURE_PATH = Path('.echel/fixtures.json')


@dataclass
class FixtureResult:
    name: str
    legacy_exit: int
    new_exit: int
    legacy_out: str
    new_out: str


def ensure_fixtures(repo_root: Path) -> list[dict]:
    p = repo_root / FIXTURE_PATH
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        default = {
            'version': 1,
            'fixtures': [
                {
                    'name': 'wiki-health-vs-doctor',
                    'legacy_cmd': 'python3 tools/wiki_lint.py',
                    'new_cmd': 'python3 tools/echel.py doctor',
                }
            ],
        }
        p.write_text(json.dumps(default, indent=2) + '\n', encoding='utf-8')
        return default['fixtures']
    raw = json.loads(p.read_text(encoding='utf-8'))
    return raw.get('fixtures', [])


def _run(cmd: str, cwd: Path) -> tuple[int, str]:
    proc = subprocess.run(cmd, shell=True, cwd=str(cwd), text=True, capture_output=True)
    out = (proc.stdout + '\n' + proc.stderr).strip()
    return proc.returncode, out[:2000]


def run_conformance(repo_root: Path) -> tuple[list[FixtureResult], Path]:
    cfg = load_config(repo_root)
    wiki_root = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)
    fixtures = ensure_fixtures(repo_root)
    results: list[FixtureResult] = []
    for fx in fixtures:
        l_exit, l_out = _run(fx['legacy_cmd'], repo_root)
        n_exit, n_out = _run(fx['new_cmd'], repo_root)
        results.append(
            FixtureResult(
                name=fx['name'],
                legacy_exit=l_exit,
                new_exit=n_exit,
                legacy_out=l_out,
                new_out=n_out,
            )
        )

    lines = ['---', 'type: analysis', 'status: active', '---', '', '# Conformance Report', '']
    for r in results:
        ok = r.legacy_exit == r.new_exit
        lines.append(f"## {r.name}")
        lines.append(f"- Exit parity: {'PASS' if ok else 'FAIL'}")
        lines.append(f"- Legacy exit: {r.legacy_exit}")
        lines.append(f"- New exit: {r.new_exit}")
        lines.append('')

    rp = wiki_root / 'reports/conformance-report.md'
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return results, rp

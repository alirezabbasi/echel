---
type: guide
status: active
---
# Phase 5 Readiness And Proof Packs

Phase 5 turns Echel progress into milestone and release readiness.

## Command Flow
```bash
python3 tools/echel.py milestone --name "MVP" --kind release --summary "First releasable product checkpoint"
python3 tools/echel.py readiness --target mvp
python3 tools/echel.py proof-pack --target mvp
python3 tools/echel.py proof-pack --target vnext
python3 tools/echel.py release-summary --target mvp
```

## What Readiness Checks
- Product graph integrity.
- Open clarification gaps.
- Open work.
- Done work missing registered evidence.
- Unmitigated risks.
- Missing or incomplete review reports.

## Generated Artifacts
- `wiki/milestones.md`
- `wiki/reports/readiness/{target}-readiness.md`
- `wiki/reports/proof-packs/{target}-proof-pack.md`
- `wiki/reports/releases/{target}-release-summary.md`

When the target is `vnext`, the proof pack also includes methodology coverage, command coverage, graph coverage, cockpit coverage, and remaining risks for final vNext certification.

## Cockpit
The cockpit includes a readiness view with status, blockers, readiness reports, proof packs, release summaries, and actions.

## Verification
```bash
make verify-phase5
```

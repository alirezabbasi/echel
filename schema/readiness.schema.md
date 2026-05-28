---
type: schema
status: active
---
# Readiness Schema

Readiness reports answer whether a target milestone, feature, MVP, or release is ready to move forward.

## File
- Path: `wiki/reports/readiness/{target}-readiness.md`
- Producer: `python3 tools/echel.py readiness --target <target>`

## Required Sections
- `Status`: ready, at risk, or blocked.
- `Scope`: target and readiness states.
- `Coverage`: graph and task coverage.
- `Blockers`: readiness issues.
- `Next Action`: recommended action.

## Readiness States
- idea clarified
- mvp scoped
- feature ready
- feature verified
- release candidate
- production ready

## Gates
- Critical graph issues block readiness.
- Done tasks without registered evidence block readiness.
- Unmitigated risks block readiness.
- Open review checks create readiness risk.


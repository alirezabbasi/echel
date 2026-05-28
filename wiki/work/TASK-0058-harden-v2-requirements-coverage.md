---
type: task
status: done
---
# TASK-0058 - Harden V2 Requirements Coverage

## Context
- [[../reports/v2-requirements-hardening-audit]]
- [[../reports/echel-v2-product-direction-review]]

## Objective
Audit and harden Echel against the seven requested V2 capabilities.

## Scope
- Product-first initialization.
- Product-owner command language.
- Product intelligence graph coverage.
- Agent work packet completeness.
- Product cockpit surfaces.
- Milestone/readiness gates.
- Product-root and `echel-core` boundary.

## Out of Scope
- Hosted SaaS deployment.

## Implementation Steps
1. Audit current implementation against the requested capabilities.
2. Patch missing product-owner and graph surfaces.
3. Update cockpit, schemas, docs, and generated verification.
4. Run full verification.

## Acceptance Criteria
- [x] `steer` command exists.
- [x] Initialization writes MVP, constraints, risks, and stack.
- [x] Graph supports workflow and evidence nodes.
- [x] Packets include likely files.
- [x] Cockpit includes architecture, contradictions, and agent activity.
- [x] Full verification passes.

## Definition of Done
- Requested V2 capabilities are present and verified.

## Verification Commands
```bash
make verify-phase1
make verify-phase2
make verify-phase3
make verify-phase4
make verify-phase5
make wiki-health
python3 tools/echel.py doctor
python3 tools/echel.py conformance run
python3 tools/echel.py graph validate
```

## Documentation Updates
- Added V2 requirements hardening audit.

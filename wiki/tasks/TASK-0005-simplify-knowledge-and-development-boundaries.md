---
type: task
status: planned
---
# TASK-0005 — Simplify Knowledge and Development Boundaries

## Context
- [[../systems/ai-native-engineering-os]]
- [[../systems/project-intelligence-compounding-model]]
- [[../project-brief]]

## Objective
Reduce repetition and complexity between `wiki/` and `docs/development/` while preserving Echel's core role as persistent project memory and AI-native development orchestration.

## Scope
- Audit overlapping concepts across wiki, development methodology, memory docs, governance docs, and README guidance.
- Define canonical ownership for repeated concepts.
- Collapse or cross-link duplicate content where one source of truth is sufficient.
- Preserve required bootstrap, task, evidence, and quality-gate behavior.

## Out of Scope
- Removing mandatory governance gates without an ADR.
- Rewriting the implementation architecture.
- Changing the platform product direction.

## Implementation Steps
1. Inventory duplicate concepts across `wiki/` and `docs/development/`.
2. Classify each concept as durable knowledge, operating procedure, execution state, or generated/reporting output.
3. Move or trim duplicate material so each concept has one canonical owner.
4. Update links, bootstrap docs, and README guidance to reflect the clarified boundary.
5. Run wiki and governance health checks.

## Acceptance Criteria
- The project brief clearly states Echel's domain-expert-guided AI-native development purpose.
- `wiki/` and `docs/development/` have explicit non-overlapping ownership rules.
- Repeated SDLC/memory concepts are either consolidated or linked to a canonical source.
- Existing session bootstrap and wiki-health workflows still pass.

## Definition of Done
- Simplification changes are documented and traceable.
- No required wiki links are broken.
- Required quality gates pass or any failures are explicitly documented.

## Verification Commands
```bash
make wiki-health
python3 tools/echel.py doctor
```

## Documentation Updates
- Update `wiki/project-brief.md`.
- Update affected system/concept pages.
- Update `docs/development/README.md` and any duplicated operating docs.
- Append `wiki/log.md`.

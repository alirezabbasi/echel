---
type: roadmap
status: draft
---
# Roadmap

## Expanded Roadmap Model

The vNext roadmap now lives in dedicated lifecycle artifacts:

- [[roadmap/master-roadmap]]
- [[roadmap/mvp-roadmap]]
- [[roadmap/architecture-roadmap]]
- [[roadmap/engineering-roadmap]]
- [[roadmap/release-plan]]

## Now

- Use `wiki/engineering/` as the product-owned contract for repository structure, coding, configuration, workflow, and exact local commands.
- Keep generated README, CI, and `scripts/verify.sh` synchronized through `echel repository-factory`.
- Use `wiki/agents/role-model.md` as the product-owned role contract for Echel's virtual delivery team.
- Use `prompts/playbooks/` as the canonical lifecycle prompt source for role execution.
- Use `wiki/agents/handoff-protocol.md` as the required inter-role handoff contract.
- Use `wiki/reports/traceability-matrix.md` to inspect lifecycle coverage and broken canon/evidence chains.
- Use `wiki/validation/` as the validation-stage mapping surface for requirements, tasks, domain concepts, and acceptance criteria.

## Next

- Add the validation command and evidence registration.
- Connect canon statements and registered evidence into graph-backed traceability.

## Later

- Add validation, release, operations, cockpit lifecycle, and governance readiness.

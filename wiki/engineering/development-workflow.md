---
type: engineering-guide
stage: repository-factory
status: active
owner: engineering
updated: 2026-07-10
---
# Development Workflow

## Purpose

This workflow turns an approved execution task into a small, verified repository change while preserving product memory. It applies to humans and AI implementation agents.

## Required Inputs

Before implementation, read:

- the selected `wiki/work/TASK-1xxx-*.md` task;
- relevant canon, requirements, domain, and architecture sources cited by the task;
- [[repository-structure]], [[coding-standards]], [[configuration-strategy]], and [[local-development]];
- current project state and unresolved blockers.

Do not begin product implementation from roadmap prose or conversational intent alone.

## Workflow

1. Confirm the task is unblocked and small enough for one implementation session.
2. State the files to modify, verification commands, and explicit out-of-scope items.
3. Make only the changes required by the task and preserve unrelated worktree changes.
4. Add or update tests for observable behavior and failure paths.
5. Run the generated repository gate from `generated/product-repository/`:

```bash
./scripts/verify.sh
```

6. When Echel Core or product memory changed, run from the Echel repository root:

```bash
python3 -m unittest discover -s tests
make wiki-health
python3 tools/echel.py graph validate
```

7. Review modified files for architecture drift, secret exposure, undocumented behavior, and unrelated changes.
8. Update project memory, decisions, task status, and cross-references affected by the implementation.
9. Mark the task done only when code, tests, runnable proof, architecture compliance, and memory updates are all present.

## Change Classification

| Change | Required Memory Update |
| --- | --- |
| Behavior or acceptance change | Requirement, acceptance criteria, task, and tests. |
| Module or ownership boundary change | Repository structure and architecture; ADR when major. |
| New configuration key | `.env.example` or checked-in example, configuration strategy, and tests. |
| Command or tool change | README, local development guide, CI, and verification script. |
| Known limitation or deferred risk | Current state, risk, or task follow-up. |

## Review Checklist

- Scope matches the task and no unrelated concerns were added.
- Required commands pass from a clean local shell with Python 3.11 or newer.
- No secrets or local-only files are staged.
- Generated outputs remain reproducible from their generator.
- Product-owned memory and generated convenience docs do not contradict each other.
- Rollback is possible by reverting the scoped change without corrupting product memory.

## Handoff

The implementation handoff must name modified files, commands run, outcomes, remaining risks, and any upstream artifact that became stale. TASK-0026 will assign this workflow to explicit AI-agent roles; this document defines the shared engineering contract those roles must obey.

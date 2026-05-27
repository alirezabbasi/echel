---
type: task
status: done
---
# TASK-0006 - Start V2 Phase 1 Product Flow

## Context
- [[../project]]
- [[../reports/echel-v2-product-direction-review]]
- [[../knowledge/ai-native-engineering-os]]

## Objective
Start V2 Phase 1 by making Echel initialization and command flow product-first.

## Scope
- Add product-owned wiki pages for project, problem, users, solution, scope, roadmap, and product architecture.
- Add initialization fields for problem, solution, direction, users, and success criteria.
- Add top-level product-owner commands: `define`, `clarify`, `plan`, `status`, and `next`.
- Preserve existing internal health, doctor, and generated project workflows.

## Out of Scope
- Full AI-assisted clarification.
- Full product cockpit UI.
- Typed graph storage beyond product wiki pages.

## Implementation Steps
1. Add product page generation.
2. Update initializer and wizard inputs.
3. Add product command handlers.
4. Update README, usage docs, state docs, and log.
5. Verify current and generated project workflows.

## Acceptance Criteria
- Generated projects include root-level product pages under `wiki/`.
- `echel define` updates product memory.
- `echel clarify` reports missing product intent.
- `echel plan` can create a product work item.
- `echel status` summarizes product state.
- `echel next` selects the next open task.

## Definition of Done
- Current repo gates pass.
- Generated project gates pass after product initialization and planning.
- Durable docs/logs are updated.

## Verification Commands
```bash
make wiki-health
python3 tools/echel.py doctor
python3 tools/project_init.py --name echel_phase1_test_528 --mode scratch --dest /tmp --problem "Teams lose product continuity between AI coding sessions" --solution "A product memory and orchestration layer for AI-native development" --direction "Guide domain experts from intent to verified software" --users "Business owners and domain experts" --success "A user can define an MVP and get the next verified work item"
cd /tmp/echel_phase1_test_528/echel-core && python3 tools/echel.py status
cd /tmp/echel_phase1_test_528/echel-core && python3 tools/echel.py plan --title "Define MVP" --goal "Clarify MVP scope and acceptance criteria"
cd /tmp/echel_phase1_test_528/echel-core && make wiki-health
cd /tmp/echel_phase1_test_528/echel-core && python3 tools/echel.py doctor
```

## Documentation Updates
- Update `README.md`.
- Update `docs/HOW_TO_USE_THIS_MODEL.md`.
- Update memory state docs.
- Append `wiki/log.md`.

# Operational Loop Methodology

## Purpose

Define a repeatable operating method that turns ideas into reliable outcomes while continuously improving system quality and team knowledge.

## The Full Compounding Loop

`idea -> structured knowledge -> task -> implementation -> verification -> bug management -> RCA -> updated knowledge`

This loop is mandatory as a full cycle. Skipping bug management or RCA reduces learning quality and causes repeated failures.

## Role of the Idea Owner

The idea owner is accountable for loop quality, not just output delivery. The owner does not need to implement everything directly, but must keep intent, scope, and acceptance clarity intact across the cycle.

The owner guides:

1. Why this idea matters now.
2. What success looks like.
3. What constraints cannot be violated.
4. How we evaluate quality and risk.
5. How we capture and reuse what we learned.

## Phase-by-Phase Operating Method

## 1) Idea

Goal: Define intent before execution starts.

Owner checklist:

- State the problem in one clear sentence.
- Define expected user or system impact.
- Set boundaries (in scope vs out of scope).
- Identify risk class (low, medium, high impact).

Quality criteria:

- Problem statement is testable.
- Value and urgency are explicit.
- Hidden assumptions are listed.

## 2) Structured Knowledge

Goal: Convert raw intent into durable context.

Actions:

- Link related wiki entities, concepts, standards, and previous decisions.
- Record assumptions and unknowns.
- Capture contradictions with existing artifacts if present.

Owner checklist:

- Confirm context quality is enough for tasking.
- Ensure no critical decision remains only in chat.

Quality criteria:

- Context is traceable.
- Links are valid.
- Dependencies and constraints are visible.

## 3) Task

Goal: Translate context into executable work.

Actions:

- Create or refine task artifact with context links.
- Add acceptance criteria, definition of done, verification commands, and documentation update scope.

Owner checklist:

- Validate that task scope is minimal but outcome-complete.
- Reject vague tasks with non-verifiable completion.

Quality criteria:

- Task has clear pass/fail conditions.
- Verification path is practical and reproducible.

## 4) Implementation

Goal: Produce smallest safe change that satisfies task intent.

Actions:

- Implement incrementally.
- Keep change set cohesive.
- Preserve architecture and standards alignment.

Owner checklist:

- Ensure implementation remains within declared scope.
- Confirm quality tradeoffs are explicit when made.

Quality criteria:

- Code/doc changes align with task objective.
- No unexplained side effects.

## 5) Verification

Goal: Prove behavior with objective evidence.

Actions:

- Run declared verification commands.
- Validate acceptance criteria one by one.
- Record evidence in relevant artifacts.

Owner checklist:

- Do not accept "works on my machine" as sufficient evidence.
- Require explicit evidence for each acceptance criterion.

Quality criteria:

- Verification is repeatable.
- Failures are documented, not hidden.

## 6) Bug Management

Goal: Treat defects as first-class operational inputs.

Actions:

- Register each discovered bug in `docs/development/bugs/BUG-*.md`.
- Log debugging commands in `docs/development/bugs/debug-commands.md` with timestamp, purpose, and status.
- Classify severity and user impact.
- Assign containment (temporary mitigation) and resolution owner.

Owner checklist:

- Confirm every defect has a tracked artifact.
- Prioritize by impact, not convenience.

Quality criteria:

- No critical bug remains untracked.
- Debug evidence is present and auditable.

## 7) RCA (Root Cause Analysis)

Goal: Remove defect sources, not only symptoms.

When mandatory:

- Production-impacting bugs.
- Recurring defects.
- Any failure that indicates process or standards weakness.

Minimum RCA structure:

1. Incident summary (what happened).
2. Impact summary (who/what was affected).
3. Trigger (immediate cause).
4. Root cause (systemic reason).
5. Contributing factors.
6. Corrective actions (fix now).
7. Preventive actions (stop recurrence).
8. Standards/tooling/docs updates required.

Owner checklist:

- Challenge symptom-level explanations.
- Ensure preventive action is specific, assigned, and verifiable.

Quality criteria:

- RCA identifies a process or system-level improvement.
- Follow-up actions are tasked and tracked.

## 8) Updated Knowledge

Goal: Feed outcomes back into the project memory so future work starts stronger.

Actions:

- Update affected wiki canonical pages.
- Add or update ADRs for major decisions.
- Update standards when repeated defects reveal ambiguity.
- Sync memory and execution docs (`CURRENT_STATE`, `SESSION_LEDGER`, `DECISION_LOG`, `RISKS_AND_ASSUMPTIONS`, `KANBAN`).
- Append `wiki/log.md` with meaningful session outcomes.

Owner checklist:

- Confirm learning is durable and discoverable.
- Verify that future sessions can resume with no hidden context.

Quality criteria:

- Knowledge artifacts reflect current reality.
- Links and traceability are intact.

## Operating Cadence

For each meaningful change:

1. Run one full loop cycle.
2. Close open bugs or leave explicit tracked state.
3. Complete RCA when required.
4. Update durable knowledge before closure.

Weekly improvement pass:

- Review recurring bug patterns.
- Update standards and templates where friction repeats.
- Tighten verification and quality gates.

## Outcome Guarantees (When Followed Correctly)

This method produces:

- Better delivery predictability.
- Lower defect recurrence.
- Stronger architectural consistency.
- Faster onboarding and session resume.
- Continuous quality improvement driven by evidence.

## Anti-Patterns to Avoid

- Closing tasks without verification evidence.
- Fixing bugs without creating bug artifacts.
- Writing RCA that only restates symptoms.
- Leaving key decisions in chat only.
- Updating code without updating linked knowledge.

## Quick Owner Ritual Before Closure

1. Did we verify outcomes against acceptance criteria?
2. Did we record and classify discovered bugs?
3. Did we perform RCA where required?
4. Did we update standards or process for recurrence prevention?
5. Did we file all durable learning into project knowledge?

If any answer is no, loop is incomplete.

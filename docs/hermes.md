# Hermes integration

Hermes is Echel's first agent runtime. It provides model selection, sessions, tools, context management, and subagent execution. Echel compiles authoritative product context and records the run.

The adapter invokes:

```text
hermes chat [--model MODEL] --toolsets terminal,file -q CONTEXT
```

`echel run WORK-001` records a safe preview. Add `--execute` to invoke Hermes.

## Memory boundary

- Hermes memory may retain user preferences and conversational continuity.
- Hermes skills contain reusable procedures.
- Echel records contain product truth and execution provenance.
- A Hermes discovery becomes product truth only through an explicit Echel knowledge proposal and approval.

## Future work

The adapter will later normalize streamed events, cancellation, resumption, tool approvals, isolated worktrees, and bounded subagent summaries. Those capabilities should be added against the runtime protocol rather than Hermes internals.

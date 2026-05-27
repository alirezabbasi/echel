# Debug Command Log

| Timestamp (UTC) | Command | Purpose | Status |
|---|---|---|---|
| 2026-05-06T00:00:00Z | seed | initialize log format | success |
| 2026-05-08T11:40:15Z | `rg -n --hidden --glob '!.git' 'Eshel|eshel|ESHEL'` | verify naming consistency and scan references before architecture edits | success |
| 2026-05-08T11:40:15Z | `sed -n '1,220p' ruleset.md` | reload top-priority project rules before planning/editing | success |
| 2026-05-08T11:40:15Z | `sed -n '1,260p' docs/ruleset.md` | validate stricter operational controls prior to implementation | success |
| 2026-05-08T11:40:15Z | `git status --short` | verify modified/new files after four-layer architecture rollout | success |
| 2026-05-10T20:47:23Z | `python3 tools/project_init.py --name echel_scratch_test --mode scratch --dest /tmp` | verify generated workspace uses project-root model with internal `echel-core/` | success |
| 2026-05-10T20:47:23Z | `python3 tools/project_init.py --name echel_existing_test --mode existing --dest /tmp --source /tmp/echel_existing_src` | verify existing-repo import plus root `.gitignore` injection for `echel-core/` | success |
| 2026-05-10T20:47:23Z | `make wiki-health` | run required quality and governance gates after generator/template changes | success |
| 2026-05-10T22:32:12Z | `python3 tools/echel.py start` | validate declarative contract loading and root resolution | success |
| 2026-05-10T22:32:12Z | `python3 tools/echel.py doctor` | run coherence/evidence/primitives/gate report against current repository state | success (drift detected) |
| 2026-05-10T22:32:12Z | `python3 tools/echel.py workspace move --dry-run` | verify migration rewrite planner and dry-run output | success |
| 2026-05-10T22:39:59Z | `python3 tools/echel.py memory add --type note --title \"phase3 kickoff\" --link wiki/log --payload \"initial phase 3 implementation\"` | verify durable memory kernel write path and typed record creation | success |
| 2026-05-10T22:39:59Z | `python3 tools/echel.py conformance run` | verify fixture-based differential conformance runner and report generation | success |
| 2026-05-10T22:39:59Z | `python3 tools/echel.py migration plan` | verify migration wave planner and risk scoring output | success |
| 2026-05-10T22:39:59Z | `python3 tools/echel.py workspace move --apply` | validate safe-apply rail blocks apply without prior impact preview | success (blocked as designed) |
| 2026-05-10T22:39:59Z | `python3 tools/echel.py contracts check --current plan --target implement` | validate LLM behavior contract transition checks with doctor gate guard | success |
| 2026-05-10T22:53:41Z | `python3 -m py_compile tools/echel.py tools/echel/platform/*.py` | validate platform sprint 1 modules and CLI wiring are syntactically valid | success |
| 2026-05-10T22:53:41Z | `python3 tools/echel.py platform init` | generate platform runtime config and verify platform command bootstrap | success |
| 2026-05-10T22:53:41Z | `python3 tools/echel.py doctor` | verify platform additions did not break core integrity checks | success |
| 2026-05-10T22:53:41Z | `make wiki-health` | run mandatory closure gates after platform sprint 1 changes | success |

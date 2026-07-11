---
type: tool-prompt-render-map
tool: codex
status: active
---
# Codex Prompt Render Map

Codex prompts should render lifecycle instructions from `prompts/playbooks/` and add only Codex-specific execution style.

| Codex prompt | Canonical playbook |
| --- | --- |
| `00-session-bootstrap.md` | `prompts/playbooks/govern.md` for context integrity and `prompts/playbooks/roadmap.md` for current-stage orientation |
| `01-ingest-existing-codebase.md` | `prompts/playbooks/govern.md` |
| `02-implement-task.md` | `prompts/playbooks/execute.md` |
| `03-create-adr.md` | `prompts/playbooks/architecture.md` |
| `04-run-wiki-lint.md` | `prompts/playbooks/govern.md` |
| `05-project-integration.md` | `prompts/playbooks/govern.md` |

Do not remove the playbook guardrails when adapting prompts for Codex.

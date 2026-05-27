.PHONY: session-bootstrap wiki-index wiki-lint wiki-health new-task file-query ingest-initial validate-governance wrw init-wizard init-project verify-phase1 verify-phase2 verify-phase3 verify-phase4 echel-start echel-define echel-clarify echel-plan echel-status echel-next echel-packet echel-build echel-review echel-graph-build echel-graph-validate echel-graph-report echel-feature-add echel-risk-add echel-link echel-doctor echel-close-task echel-sync-memory echel-workspace-move-dry-run echel-memory-query echel-conformance echel-migration-plan echel-contract-check echel-adapters echel-platform-init echel-platform-up

session-bootstrap:
	python3 tools/session_bootstrap.py

wiki-index:
	python3 tools/wiki_index.py

wiki-lint:
	python3 tools/wiki_lint.py

validate-governance:
	python3 tools/validate_governance.py

wiki-health: wiki-index wiki-lint validate-governance

new-task:
	python3 tools/new_task.py

file-query:
	python3 tools/file_query.py

ingest-initial:
	python3 tools/ingest.py raw/initial-source.md --title "Initial source import" --kind source

wrw:
	python3 tools/wrw.py

init-wizard:
	python3 tools/init_wizard.py

init-project:
	python3 tools/project_init.py --name "$${NAME:?Set NAME=<project-name>}" --mode "$${MODE:-scratch}" --dest "$${DEST:-.}" $${SOURCE:+--source "$$SOURCE"}

verify-phase1:
	python3 tools/verify_phase1.py

verify-phase2:
	python3 tools/verify_phase2.py

verify-phase3:
	python3 tools/verify_phase3.py

verify-phase4:
	python3 tools/verify_phase4.py

echel-start:
	python3 tools/echel.py start

echel-define:
	python3 tools/echel.py define $${NAME:+--name "$$NAME"} $${PROBLEM:+--problem "$$PROBLEM"} $${SOLUTION:+--solution "$$SOLUTION"} $${DIRECTION:+--direction "$$DIRECTION"} $${USERS:+--users "$$USERS"} $${SUCCESS:+--success "$$SUCCESS"}

echel-clarify:
	python3 tools/echel.py clarify $${FIELD:+--field "$$FIELD"} $${ANSWER:+--answer "$$ANSWER"}

echel-plan:
	python3 tools/echel.py plan $${TITLE:+--title "$$TITLE"} $${GOAL:+--goal "$$GOAL"}

echel-status:
	python3 tools/echel.py status

echel-next:
	python3 tools/echel.py next

echel-packet:
	python3 tools/echel.py packet $${TASK:+--task "$$TASK"}

echel-build:
	python3 tools/echel.py build $${TASK:+--task "$$TASK"}

echel-review:
	python3 tools/echel.py review $${TASK:+--task "$$TASK"}

echel-graph-build:
	python3 tools/echel.py graph build

echel-graph-validate:
	python3 tools/echel.py graph validate

echel-graph-report:
	python3 tools/echel.py graph report

echel-feature-add:
	python3 tools/echel.py feature add --title "$${TITLE:?Set TITLE=<feature-title>}" $${SUMMARY:+--summary "$$SUMMARY"}

echel-risk-add:
	python3 tools/echel.py risk add --title "$${TITLE:?Set TITLE=<risk-title>}" $${IMPACT:+--impact "$$IMPACT"} $${MITIGATION:+--mitigation "$$MITIGATION"}

echel-link:
	python3 tools/echel.py link --from "$${FROM:?Set FROM=<node-id>}" --to "$${TO:?Set TO=<node-id>}" $${REL:+--rel "$$REL"}

echel-doctor:
	python3 tools/echel.py doctor

echel-close-task:
	python3 tools/echel.py close-task "$${TASK:?Set TASK=TASK-XXXX}"

echel-sync-memory:
	python3 tools/echel.py sync-memory

echel-workspace-move-dry-run:
	python3 tools/echel.py workspace move --dry-run

echel-memory-query:
	python3 tools/echel.py memory query

echel-conformance:
	python3 tools/echel.py conformance run

echel-migration-plan:
	python3 tools/echel.py migration plan

echel-contract-check:
	python3 tools/echel.py contracts check --current "$${CURRENT:?Set CURRENT=<state>}" --target "$${TARGET:?Set TARGET=<state>}"

echel-adapters:
	python3 tools/echel.py adapters list

echel-platform-init:
	python3 tools/echel.py platform init

echel-platform-up:
	python3 tools/echel.py platform up

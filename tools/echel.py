#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import re
import sys

from echel.adapters import detect_adapters
from echel.coherence import detect_drift
from echel.conformance import run_conformance
from echel.config import ConfigError, load_config, resolve_root_map, resolve_symbolic_path
from echel.contracts import ensure_contracts, validate_transition
from echel.evidence import ensure_registry, validate_links, validate_registry
from echel.gates import run_gates, run_stage_gate
from echel.graph import (
    add_feature,
    add_manual_link,
    add_risk,
    build_graph,
    graph_status,
    graph_summary,
    validate_graph,
    write_graph,
    write_graph_report,
)
from echel.memory_kernel import append_record, contradiction_summary, query_records
from echel.migration_planner import plan_waves
from echel.platform.runtime import ensure_platform_config, load_platform_config
from echel.primitives import validate_decisions, validate_tasks
from echel.readiness import create_milestone, proof_pack, readiness_report, release_summary
from echel.product import (
    answer_clarification,
    clarification_questions,
    create_plan_task,
    generate_work_packet,
    generate_review_report,
    ensure_product_pages,
    next_task,
    product_status,
    steer_product,
    synthesize_mvp_plan,
    update_project_definition,
)
from echel.canon import canon_generate, canon_status, canon_drift_report, ensure_canon_files
from echel.discovery import discover_questions, discover_status, discover_update, ensure_discovery_files
from echel.domain import domain_generate, domain_status, ensure_domain_files
from echel.requirements import requirements_generate, requirements_status, ensure_requirements_files
from echel.strategy import strategy_generate, strategy_readiness, strategy_status, ensure_strategy_files
from echel.workspace import apply_workspace_move, plan_workspace_move, write_impact_preview


def _load(repo_root: Path):
    try:
        return load_config(repo_root)
    except ConfigError as exc:
        print(f"CONFIG_ERROR: {exc}", file=sys.stderr)
        sys.exit(2)


def _wiki_root(repo_root: Path, cfg) -> Path:
    return resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)


def _memory_root(repo_root: Path, cfg) -> Path:
    return resolve_symbolic_path("$MEMORY_ROOT", cfg, repo_root)


def cmd_start(repo_root: Path) -> int:
    cfg = _load(repo_root)
    roots = resolve_root_map(cfg, repo_root)
    print("Echel session start")
    print(f"- config: {cfg.path}")
    for k, v in roots.items():
        print(f"- ${k}: {v}")
    return 0


def cmd_define(
    repo_root: Path,
    name: str | None,
    problem: str | None,
    solution: str | None,
    direction: str | None,
    users: str | None,
    success: str | None,
) -> int:
    cfg = _load(repo_root)
    changed = update_project_definition(
        repo_root,
        cfg,
        name=name,
        problem=problem,
        solution=solution,
        direction=direction,
        users=users,
        success=success,
    )
    print("Product definition updated")
    for path in changed:
        print(f"- {path}")
    return 0


def cmd_clarify(repo_root: Path, field: str | None, answer: str | None) -> int:
    cfg = _load(repo_root)
    if field or answer:
        if not field or not answer:
            print("clarify requires both --field and --answer", file=sys.stderr)
            return 2
        try:
            path = answer_clarification(repo_root, cfg, field, answer)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(f"Updated clarification `{field}`: {path}")
        return 0
    questions = clarification_questions(repo_root, cfg)
    print("Clarification Queue")
    if not questions:
        print("- No obvious clarification gaps found.")
        return 0
    for idx, question in enumerate(questions, start=1):
        print(f"{idx}. {question}")
    return 0


def cmd_discover(repo_root: Path, field: str | None, value: str | None) -> int:
    cfg = _load(repo_root)
    if field or value:
        if not field or not value:
            print("discover requires both --field and --value", file=sys.stderr)
            return 2
        try:
            path = discover_update(repo_root, cfg, field, value)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(f"Updated discovery `{field}`: {path}")
        return 0
    ensure_discovery_files(repo_root, cfg)
    print(discover_status(repo_root, cfg))
    print()
    questions = discover_questions(repo_root, cfg)
    if questions:
        print("Open Discovery Questions")
        for idx, question in enumerate(questions, start=1):
            print(f"{idx}. {question}")
    else:
        print("No open discovery gaps found.")
    return 0


def cmd_canon(repo_root: Path, force: bool) -> int:
    cfg = _load(repo_root)
    ensure_canon_files(repo_root, cfg)
    print(canon_status(repo_root, cfg))
    if force:
        print("\nForcing canon generation (bypassing discovery gate).")
    try:
        changed = canon_generate(repo_root, cfg, force=force)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if changed:
        print(f"\nUpdated {len(changed)} canon file(s):")
        for path in changed:
            print(f"- {path}")
    else:
        print("\nCanon files are already up to date.")
    return 0


def cmd_canon_drift(repo_root: Path) -> int:
    cfg = _load(repo_root)
    print(canon_drift_report(repo_root, cfg))
    return 0


def cmd_strategy(repo_root: Path, force: bool) -> int:
    cfg = _load(repo_root)
    ensure_strategy_files(repo_root, cfg)
    print(strategy_status(repo_root, cfg))
    if force:
        print("\nForcing strategy generation (bypassing discovery gate).")
    try:
        changed = strategy_generate(repo_root, cfg, force=force)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if changed:
        print(f"\nUpdated {len(changed)} strategy file(s):")
        for path in changed:
            print(f"- {path}")
    else:
        print("\nStrategy files are already up to date.")
    return 0


def cmd_strategy_readiness(repo_root: Path) -> int:
    cfg = _load(repo_root)
    failures = strategy_readiness(repo_root, cfg)
    if failures:
        print("STRATEGY: BLOCKED")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("STRATEGY: PASS")
    return 0


def cmd_requirements(repo_root: Path, force: bool) -> int:
    cfg = _load(repo_root)
    ensure_requirements_files(repo_root, cfg)
    print(requirements_status(repo_root, cfg))
    if force:
        print("\nForcing requirements generation (bypassing strategy readiness).")
    try:
        changed = requirements_generate(repo_root, cfg, force=force)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if changed:
        print(f"\nUpdated {len(changed)} requirement artifact(s):")
        for path in changed:
            print(f"- {path}")
    else:
        print("\nNo requirement artifacts changed.")
    return 0


def cmd_domain(repo_root: Path, force: bool) -> int:
    cfg = _load(repo_root)
    ensure_domain_files(repo_root, cfg)
    print(domain_status(repo_root, cfg))
    if force:
        print("\nForcing domain generation (bypassing requirements readiness).")
    try:
        changed = domain_generate(repo_root, cfg, force=force)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if changed:
        print(f"\nUpdated {len(changed)} domain artifact(s):")
        for path in changed:
            print(f"- {path}")
    else:
        print("\nNo domain artifacts changed.")
    return 0


def cmd_plan(repo_root: Path, title: str | None, goal: str | None) -> int:
    cfg = _load(repo_root)
    if not title:
        roadmap, task = synthesize_mvp_plan(repo_root, cfg)
        report = write_graph_report(repo_root, cfg)
        print("Synthesized MVP plan")
        print(f"- Roadmap: {roadmap}")
        print(f"- Work item: {task}")
        print(f"- Graph report: {report}")
        return 0
    path = create_plan_task(repo_root, cfg, title=title, goal=goal)
    print(f"Created product work item: {path}")
    return 0


def cmd_status(repo_root: Path) -> int:
    cfg = _load(repo_root)
    print(product_status(repo_root, cfg))
    print()
    print(graph_status(repo_root, cfg))
    return 0


def cmd_next(repo_root: Path) -> int:
    cfg = _load(repo_root)
    task = next_task(repo_root, cfg)
    if task:
        print(task)
        return 0
    print("No open task found.")
    return 0


def cmd_packet(repo_root: Path, task_id: str | None) -> int:
    cfg = _load(repo_root)
    try:
        path = generate_work_packet(repo_root, cfg, task_id)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"Generated work packet: {path}")
    return 0


def cmd_build(repo_root: Path, task_id: str | None) -> int:
    cfg = _load(repo_root)
    try:
        path = generate_work_packet(repo_root, cfg, task_id)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"Prepared agent build packet: {path}")
    return 0


def cmd_review(repo_root: Path, task_id: str | None) -> int:
    cfg = _load(repo_root)
    try:
        path = generate_review_report(repo_root, cfg, task_id)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"Generated review report: {path}")
    return 0


def cmd_steer(repo_root: Path, field: str, value: str) -> int:
    cfg = _load(repo_root)
    try:
        path = steer_product(repo_root, cfg, field=field, value=value)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"Product direction updated: {path}")
    return 0


def cmd_graph(repo_root: Path, graph_cmd: str) -> int:
    cfg = _load(repo_root)
    if graph_cmd == "build":
        path = write_graph(repo_root, cfg)
        print(f"Product graph written: {path}")
        return 0
    if graph_cmd == "show":
        graph = build_graph(repo_root, cfg)
        print(graph_summary(graph, validate_graph(graph)))
        return 0
    if graph_cmd == "validate":
        graph = build_graph(repo_root, cfg)
        issues = validate_graph(graph)
        if not issues:
            print("Product graph validation passed")
            return 0
        for issue in issues:
            print(f"- {issue.severity}: {issue.message}")
        return 1 if any(issue.severity == "critical" for issue in issues) else 0
    if graph_cmd == "report":
        path = write_graph_report(repo_root, cfg)
        print(f"Product graph report written: {path}")
        return 0
    print("unknown graph command", file=sys.stderr)
    return 2


def cmd_feature_add(repo_root: Path, title: str, summary: str) -> int:
    cfg = _load(repo_root)
    path = add_feature(repo_root, cfg, title=title, summary=summary)
    print(f"Feature added: {path}")
    return 0


def cmd_risk_add(repo_root: Path, title: str, impact: str, mitigation: str) -> int:
    cfg = _load(repo_root)
    path = add_risk(repo_root, cfg, title=title, impact=impact, mitigation=mitigation)
    print(f"Risk added: {path}")
    return 0


def cmd_link(repo_root: Path, from_id: str, to_id: str, rel: str) -> int:
    cfg = _load(repo_root)
    path = add_manual_link(repo_root, cfg, from_id=from_id, to_id=to_id, edge_type=rel)
    print(f"Relationship added: {path}")
    return 0


def cmd_milestone(repo_root: Path, name: str, kind: str, summary: str) -> int:
    cfg = _load(repo_root)
    try:
        path = create_milestone(repo_root, cfg, name=name, kind=kind, summary=summary)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"Milestone updated: {path}")
    return 0


def cmd_readiness(repo_root: Path, target: str, stage: str | None) -> int:
    cfg = _load(repo_root)
    if stage:
        result = run_stage_gate(repo_root, cfg, stage)
        if result.passed:
            print(f"{result.gate_id}: PASS")
        else:
            print(f"{result.gate_id}: BLOCKED")
            for failure in result.failures:
                print(f"  - {failure}")
            return 1
        return 0
    path = readiness_report(repo_root, cfg, target=target)
    print(f"Readiness report written: {path}")
    return 0


def cmd_proof_pack(repo_root: Path, target: str) -> int:
    cfg = _load(repo_root)
    path = proof_pack(repo_root, cfg, target=target)
    print(f"Proof pack written: {path}")
    return 0


def cmd_release_summary(repo_root: Path, target: str) -> int:
    cfg = _load(repo_root)
    path = release_summary(repo_root, cfg, target=target)
    print(f"Release summary written: {path}")
    return 0


def cmd_doctor(repo_root: Path) -> int:
    cfg = _load(repo_root)
    code = 0

    print("## Doctor Report")
    print("\n### Primitive Validation")
    wiki_root = _wiki_root(repo_root, cfg)
    p_issues = []
    p_issues.extend(validate_tasks(sorted((wiki_root / "work").glob("TASK-*.md"))))
    p_issues.extend(validate_decisions(sorted((wiki_root / "decisions").glob("ADR-*.md"))))
    if not p_issues:
        print("- OK")
    else:
        code = max(code, 2)
        for i in p_issues:
            print(f"- {i.severity}: {i.message} [{i.source}]")

    print("\n### Evidence Registry")
    reg_path = repo_root / cfg.evidence_registry
    reg = ensure_registry(reg_path)
    r_issues = validate_registry(reg, str(reg_path))
    link_files = sorted((wiki_root / "work").glob("TASK-*.md")) + sorted((wiki_root / "decisions").glob("ADR-*.md"))
    l_issues = validate_links(link_files, reg)
    if not r_issues and not l_issues:
        print("- OK")
    else:
        code = max(code, 1)
        for i in [*r_issues, *l_issues]:
            print(f"- {i.severity}: {i.message} [{i.source}]")

    print("\n### Coherence Drift")
    drifts = detect_drift(repo_root)
    if not drifts:
        print("- OK")
    else:
        code = max(code, 1)
        for d in drifts:
            print(f"- {d.category}/{d.severity}: {d.message}")
            print(f"  source={d.source}")
            print(f"  fix={d.suggestion}")

    print("\n### Gates")
    results, errors = run_gates(repo_root, cfg)
    if errors:
        code = max(code, 2)
        for e in errors:
            print(f"- compile error: {e}")
    else:
        for res in results:
            if res.passed:
                print(f"- {res.gate_id}: PASS")
            else:
                code = max(code, 1)
                print(f"- {res.gate_id}: FAIL")
                for f in res.failures:
                    print(f"  - {f}")
    return code


def _set_task_status(path: Path, done: bool) -> None:
    text = path.read_text(encoding="utf-8")
    new_status = "status: done" if done else "status: planned"
    if re.search(r"^status:\s*\w+\s*$", text, re.MULTILINE):
        text = re.sub(r"^status:\s*\w+\s*$", new_status, text, flags=re.MULTILINE)
    else:
        text = text.replace("---\n", f"---\n{new_status}\n", 1)
    path.write_text(text, encoding="utf-8")


def _set_kanban_task(repo_root: Path, cfg, task_id: str, done: bool) -> None:
    p = _memory_root(repo_root, cfg).parent / "work.md"
    text = p.read_text(encoding="utf-8")
    mark = "x" if done else " "
    updated, count = re.subn(rf"- \[(?: |x)\] ({re.escape(task_id)})\b", rf"- [{mark}] \1", text)
    if count == 0:
        updated += f"\n- [{'x' if done else ' '}] {task_id}\n"
    p.write_text(updated, encoding="utf-8")


def cmd_close_task(repo_root: Path, task_id: str) -> int:
    cfg = _load(repo_root)
    matches = sorted((_wiki_root(repo_root, cfg) / "work").glob(f"{task_id}-*.md"))
    if not matches:
        print(f"task not found: {task_id}", file=sys.stderr)
        return 2
    task_path = matches[0]
    text = task_path.read_text(encoding="utf-8")
    evid_links = re.findall(r"\bEVID-[A-Z0-9\-]{3,}\b", text)
    if not evid_links:
        print("close-task blocked: task must reference at least one evidence ID", file=sys.stderr)
        return 1

    reg = ensure_registry(repo_root / cfg.evidence_registry)
    unknown = sorted({e for e in evid_links if e not in reg.get("artifacts", {})})
    if unknown:
        print(f"close-task blocked: unknown evidence IDs: {', '.join(unknown)}", file=sys.stderr)
        return 1

    _set_task_status(task_path, done=True)
    _set_kanban_task(repo_root, cfg, task_id, done=True)
    print(f"closed {task_id}")
    return 0


def _sync_last_updated(path: Path, target_date: str) -> None:
    text = path.read_text(encoding="utf-8")
    if re.search(r"^Last updated:\s*", text, re.MULTILINE):
        out = re.sub(r"^Last updated:\s*.*$", f"Last updated: {target_date}", text, flags=re.MULTILINE)
    else:
        out = text.rstrip() + f"\n\nLast updated: {target_date}\n"
    path.write_text(out, encoding="utf-8")


def cmd_sync_memory(repo_root: Path) -> int:
    cfg = _load(repo_root)
    today = date.today().isoformat()
    memory_root = _memory_root(repo_root, cfg)
    targets = [
        memory_root / "where-are-we.md",
        memory_root / "current-state.md",
    ]
    for p in targets:
        if p.exists():
            _sync_last_updated(p, today)
    print(f"memory synced to {today}")
    return 0


def cmd_workspace_move(repo_root: Path, dry_run: bool, force: bool) -> int:
    cfg = _load(repo_root)
    changes = plan_workspace_move(repo_root, cfg)
    if dry_run:
        print("workspace move dry-run")
        print(f"- files to rewrite: {len(changes)}")
        for c in changes[:50]:
            print(f"- {c.path} ({c.before_hash} -> {c.after_hash})")
        if len(changes) > 50:
            print(f"- ... and {len(changes) - 50} more")
        preview = write_impact_preview(repo_root, changes)
        print(f"- impact preview: {preview}")
        print("- apply requires fresh preview; use `--force` to bypass")
        return 0

    if not force:
        preview = repo_root / ".echel" / "workspace_move_impact.json"
        if not preview.exists():
            print(
                "workspace move blocked: run dry-run first to generate impact preview, or use --force",
                file=sys.stderr,
            )
            return 1
    manifest = apply_workspace_move(repo_root, cfg)
    print(f"workspace move applied, rollback manifest: {manifest}")
    return 0


def cmd_memory_add(repo_root: Path, record_type: str, title: str, links: list[str], contradiction: bool, payload: str) -> int:
    data = {"note": payload} if payload else {}
    rec = append_record(repo_root, record_type=record_type, title=title, links=links, contradiction=contradiction, payload=data)
    print(f"added memory record: {rec.record_id}")
    return 0


def cmd_memory_query(repo_root: Path, record_type: str | None, contradiction_only: bool, text: str | None) -> int:
    rows = query_records(repo_root, record_type=record_type, contradiction_only=contradiction_only, text=text)
    summary = contradiction_summary(rows)
    print(f"records={summary['total']} contradictions={summary['contradictions']} ratio={summary['ratio']}")
    for rec in rows[-50:]:
        print(f"- {rec.ts} {rec.record_id} {rec.record_type} contradiction={rec.contradiction} title={rec.title}")
    return 0


def cmd_conformance_run(repo_root: Path) -> int:
    results, report_path = run_conformance(repo_root)
    code = 0
    for r in results:
        parity = r.legacy_exit == r.new_exit
        print(f"{r.name}: {'PASS' if parity else 'FAIL'} (legacy={r.legacy_exit}, new={r.new_exit})")
        if not parity:
            code = 1
    print(f"report: {report_path}")
    return code


def cmd_migration_plan(repo_root: Path) -> int:
    waves = plan_waves(repo_root)
    print("migration waves")
    for w in waves:
        print(f"- wave {w.wave}: tasks={len(w.tasks)} risk={w.risk_score}")
        for t in w.tasks:
            print(f"  - {t}")
    return 0


def cmd_contract_check(repo_root: Path, current: str, target: str) -> int:
    contract = ensure_contracts(repo_root)
    doctor_pass = cmd_doctor(repo_root) == 0
    ok, msg = validate_transition(contract, current=current, target=target, doctor_pass=doctor_pass)
    if ok:
        print(f"contract: PASS ({msg})")
        return 0
    print(f"contract: FAIL ({msg})", file=sys.stderr)
    return 1


def cmd_adapters(repo_root: Path) -> int:
    found = detect_adapters(repo_root)
    if not found:
        print("no runtime adapters detected")
        return 0
    print("runtime adapters")
    for a in found:
        print(f"- {a.name}")
        print(f"  task-hook: {a.task_hook}")
        print(f"  evidence-hook: {a.evidence_hook}")
    return 0


def cmd_platform_init(repo_root: Path) -> int:
    path = ensure_platform_config(repo_root)
    print(f"platform config ready: {path}")
    return 0


def cmd_platform_up(repo_root: Path, host: str | None, port: int | None) -> int:
    cfg = load_platform_config(repo_root)
    listen_host = host or str(cfg.get("host", "127.0.0.1"))
    listen_port = int(port or cfg.get("port", 8787))
    try:
        import uvicorn
    except ImportError:
        print("platform up requires uvicorn and fastapi. Install with: pip install fastapi uvicorn", file=sys.stderr)
        return 2
    from echel.platform.app import create_app

    app = create_app(repo_root)
    uvicorn.run(app, host=listen_host, port=listen_port)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="echel")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("start")
    sub.add_parser("doctor")

    define = sub.add_parser("define")
    define.add_argument("--name")
    define.add_argument("--problem")
    define.add_argument("--solution")
    define.add_argument("--direction")
    define.add_argument("--users")
    define.add_argument("--success")

    clarify = sub.add_parser("clarify")
    clarify.add_argument("--field")
    clarify.add_argument("--answer")

    discover = sub.add_parser("discover")
    discover.add_argument("--field")
    discover.add_argument("--value")

    canon = sub.add_parser("canon")
    canon.add_argument("--force", action="store_true")

    sub.add_parser("canon-drift")

    strategy = sub.add_parser("strategy")
    strategy.add_argument("--force", action="store_true")

    sub.add_parser("strategy-readiness")

    requirements = sub.add_parser("requirements")
    requirements.add_argument("--force", action="store_true")

    domain = sub.add_parser("domain")
    domain.add_argument("--force", action="store_true")

    plan = sub.add_parser("plan")
    plan.add_argument("--title")
    plan.add_argument("--goal")

    sub.add_parser("status")
    sub.add_parser("next")
    packet = sub.add_parser("packet")
    packet.add_argument("--task")
    build = sub.add_parser("build")
    build.add_argument("--task")
    review = sub.add_parser("review")
    review.add_argument("--task")
    steer = sub.add_parser("steer")
    steer.add_argument("--field", required=True)
    steer.add_argument("--value", required=True)

    graph = sub.add_parser("graph")
    graph_sub = graph.add_subparsers(dest="graph_cmd", required=True)
    graph_sub.add_parser("build")
    graph_sub.add_parser("show")
    graph_sub.add_parser("validate")
    graph_sub.add_parser("report")

    feature = sub.add_parser("feature")
    feature_sub = feature.add_subparsers(dest="feature_cmd", required=True)
    feature_add = feature_sub.add_parser("add")
    feature_add.add_argument("--title", required=True)
    feature_add.add_argument("--summary", default="")

    risk = sub.add_parser("risk")
    risk_sub = risk.add_subparsers(dest="risk_cmd", required=True)
    risk_add = risk_sub.add_parser("add")
    risk_add.add_argument("--title", required=True)
    risk_add.add_argument("--impact", default="")
    risk_add.add_argument("--mitigation", default="")

    link = sub.add_parser("link")
    link.add_argument("--from", dest="from_id", required=True)
    link.add_argument("--to", dest="to_id", required=True)
    link.add_argument("--rel", default="related_to")

    milestone = sub.add_parser("milestone")
    milestone.add_argument("--name", required=True)
    milestone.add_argument("--kind", choices=["milestone", "release"], default="milestone")
    milestone.add_argument("--summary", default="")

    readiness = sub.add_parser("readiness")
    readiness.add_argument("--target", default="mvp")
    readiness.add_argument("--stage", default=None)

    proof = sub.add_parser("proof-pack")
    proof.add_argument("--target", default="mvp")

    release = sub.add_parser("release-summary")
    release.add_argument("--target", default="mvp")

    close = sub.add_parser("close-task")
    close.add_argument("task_id")

    sub.add_parser("sync-memory")

    ws = sub.add_parser("workspace")
    ws_sub = ws.add_subparsers(dest="workspace_cmd", required=True)
    move = ws_sub.add_parser("move")
    mode = move.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    move.add_argument("--force", action="store_true")

    memory = sub.add_parser("memory")
    memory_sub = memory.add_subparsers(dest="memory_cmd", required=True)
    madd = memory_sub.add_parser("add")
    madd.add_argument("--type", required=True)
    madd.add_argument("--title", required=True)
    madd.add_argument("--link", action="append", default=[])
    madd.add_argument("--contradiction", action="store_true")
    madd.add_argument("--payload", default="")
    mquery = memory_sub.add_parser("query")
    mquery.add_argument("--type")
    mquery.add_argument("--contradictions", action="store_true")
    mquery.add_argument("--text")

    conf = sub.add_parser("conformance")
    conf_sub = conf.add_subparsers(dest="conformance_cmd", required=True)
    conf_sub.add_parser("run")

    mig = sub.add_parser("migration")
    mig_sub = mig.add_subparsers(dest="migration_cmd", required=True)
    mig_sub.add_parser("plan")

    contracts = sub.add_parser("contracts")
    ctr_sub = contracts.add_subparsers(dest="contracts_cmd", required=True)
    check = ctr_sub.add_parser("check")
    check.add_argument("--current", required=True)
    check.add_argument("--target", required=True)

    adapters = sub.add_parser("adapters")
    adapters_sub = adapters.add_subparsers(dest="adapters_cmd", required=True)
    adapters_sub.add_parser("list")

    platform = sub.add_parser("platform")
    platform_sub = platform.add_subparsers(dest="platform_cmd", required=True)
    platform_sub.add_parser("init")
    up = platform_sub.add_parser("up")
    up.add_argument("--host")
    up.add_argument("--port", type=int)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path.cwd()

    if args.cmd == "start":
        return cmd_start(root)
    if args.cmd == "doctor":
        return cmd_doctor(root)
    if args.cmd == "define":
        return cmd_define(
            root,
            name=args.name,
            problem=args.problem,
            solution=args.solution,
            direction=args.direction,
            users=args.users,
            success=args.success,
        )
    if args.cmd == "clarify":
        return cmd_clarify(root, field=args.field, answer=args.answer)
    if args.cmd == "discover":
        return cmd_discover(root, field=args.field, value=args.value)
    if args.cmd == "canon":
        return cmd_canon(root, force=args.force)
    if args.cmd == "canon-drift":
        return cmd_canon_drift(root)
    if args.cmd == "strategy":
        return cmd_strategy(root, force=args.force)
    if args.cmd == "strategy-readiness":
        return cmd_strategy_readiness(root)
    if args.cmd == "requirements":
        return cmd_requirements(root, force=args.force)
    if args.cmd == "domain":
        return cmd_domain(root, force=args.force)
    if args.cmd == "plan":
        return cmd_plan(root, title=args.title, goal=args.goal)
    if args.cmd == "status":
        return cmd_status(root)
    if args.cmd == "next":
        return cmd_next(root)
    if args.cmd == "packet":
        return cmd_packet(root, task_id=args.task)
    if args.cmd == "build":
        return cmd_build(root, task_id=args.task)
    if args.cmd == "review":
        return cmd_review(root, task_id=args.task)
    if args.cmd == "steer":
        return cmd_steer(root, field=args.field, value=args.value)
    if args.cmd == "graph":
        return cmd_graph(root, args.graph_cmd)
    if args.cmd == "feature" and args.feature_cmd == "add":
        return cmd_feature_add(root, title=args.title, summary=args.summary)
    if args.cmd == "risk" and args.risk_cmd == "add":
        return cmd_risk_add(root, title=args.title, impact=args.impact, mitigation=args.mitigation)
    if args.cmd == "link":
        return cmd_link(root, from_id=args.from_id, to_id=args.to_id, rel=args.rel)
    if args.cmd == "milestone":
        return cmd_milestone(root, name=args.name, kind=args.kind, summary=args.summary)
    if args.cmd == "readiness":
        return cmd_readiness(root, target=args.target, stage=args.stage)
    if args.cmd == "proof-pack":
        return cmd_proof_pack(root, target=args.target)
    if args.cmd == "release-summary":
        return cmd_release_summary(root, target=args.target)
    if args.cmd == "close-task":
        return cmd_close_task(root, args.task_id)
    if args.cmd == "sync-memory":
        return cmd_sync_memory(root)
    if args.cmd == "workspace" and args.workspace_cmd == "move":
        dry_run = True if args.dry_run or not args.apply else False
        return cmd_workspace_move(root, dry_run=dry_run, force=args.force)
    if args.cmd == "memory" and args.memory_cmd == "add":
        return cmd_memory_add(root, record_type=args.type, title=args.title, links=args.link, contradiction=args.contradiction, payload=args.payload)
    if args.cmd == "memory" and args.memory_cmd == "query":
        return cmd_memory_query(root, record_type=args.type, contradiction_only=args.contradictions, text=args.text)
    if args.cmd == "conformance" and args.conformance_cmd == "run":
        return cmd_conformance_run(root)
    if args.cmd == "migration" and args.migration_cmd == "plan":
        return cmd_migration_plan(root)
    if args.cmd == "contracts" and args.contracts_cmd == "check":
        return cmd_contract_check(root, current=args.current, target=args.target)
    if args.cmd == "adapters" and args.adapters_cmd == "list":
        return cmd_adapters(root)
    if args.cmd == "platform" and args.platform_cmd == "init":
        return cmd_platform_init(root)
    if args.cmd == "platform" and args.platform_cmd == "up":
        return cmd_platform_up(root, host=args.host, port=args.port)

    print("unknown command", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

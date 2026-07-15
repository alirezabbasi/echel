from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from echel.context.compiler import ContextCompiler
from echel.initialization import IdeaInitializationService, InitializationError
from echel.model.records import Run
from echel.runtimes.base import RunRequest
from echel.runtimes.hermes import HermesRuntime
from echel.storage.files import FileStore, StoreError
from echel.verification.runner import VerificationRunner
from echel.workflow import LifecycleBlocked, WorkflowService, lifecycle_summary


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="echel", description="Progressive SDLC memory")
    root.add_argument("--root", type=Path, default=Path.cwd(), help="project repository")
    root.add_argument("--json", action="store_true", help="emit machine-readable output")
    commands = root.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="initialize the minimum truthful project state")
    init.add_argument("name")
    init.add_argument("--mode", choices=("idea",), default="idea")
    init.add_argument("--idea", required=True)
    init.add_argument("--owner", required=True, help="responsible person as user:local-id")
    init.add_argument("--id", dest="project_id", help="stable project:local-id")
    init.add_argument("--profile", choices=("prototype", "product", "production", "regulated"), default="prototype")
    init.add_argument("--config", action="append", default=[], metavar="KEY=VALUE")
    init.add_argument("--dry-run", action="store_true", help="validate and explain without writing")

    commands.add_parser("status", help="show current maturity and next action")
    commands.add_parser("lifecycle", help="show the progressive methodology")

    add = commands.add_parser("add", help="add product knowledge")
    add.add_argument("kind")
    add.add_argument("statement")
    add.add_argument("--stage")
    add.add_argument("--status", choices=("proposed", "accepted", "validated", "rejected", "stale"), default="proposed")
    add.add_argument("--confidence", choices=("low", "medium", "high"), default="medium")
    add.add_argument("--source", action="append", default=[])

    advance = commands.add_parser("advance", help="advance when current knowledge is usable")
    advance.add_argument("--force", action="store_true")

    work = commands.add_parser("work", help="create bounded implementation work")
    work.add_argument("title")
    work.add_argument("--objective", required=True)
    work.add_argument("--relates-to", action="append", default=[])
    work.add_argument("--accept", action="append", required=True)
    work.add_argument("--verify", action="append", required=True)

    context = commands.add_parser("context", help="compile minimal work context")
    context.add_argument("work_id")

    run = commands.add_parser("run", help="execute a work packet through Hermes")
    run.add_argument("work_id")
    run.add_argument("--model")
    run.add_argument("--execute", action="store_true", help="invoke Hermes; default is a safe preview")

    verify = commands.add_parser("verify", help="run and record work-item verification")
    verify.add_argument("work_id")
    return root


def _emit(payload, machine: bool) -> None:
    if machine:
        if hasattr(payload, "to_dict"):
            payload = payload.to_dict()
        print(json.dumps(payload, indent=2, default=lambda value: value.__dict__))
    elif isinstance(payload, str):
        print(payload)
    else:
        print(json.dumps(payload, indent=2, default=lambda value: value.__dict__))


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "init":
        try:
            service = IdeaInitializationService()
            plan = service.preview(
                args.root,
                args.name,
                args.idea,
                args.owner,
                args.profile,
                service.parse_config(args.config),
                args.project_id,
            )
            _emit(plan if args.dry_run else service.apply(plan), args.json)
            return 0
        except InitializationError as exc:
            if args.json:
                print(json.dumps({"error": exc.to_dict()}, indent=2), file=sys.stderr)
            else:
                print(f"echel: {exc}", file=sys.stderr)
            return 2
    store = FileStore(args.root)
    workflow = WorkflowService(store)
    try:
        if args.command == "status":
            state = workflow.status()
            if args.json:
                _emit(state, True)
            else:
                project = state["project"]
                missing = ", ".join(state["missing"]) or "none"
                print(f"{project['name']} — stage: {state['stage'].title}")
                print(f"Purpose: {state['stage'].purpose}")
                print(f"Missing accepted knowledge: {missing}")
                print("Records: " + ", ".join(f"{key}={value}" for key, value in state["record_counts"].items()))
        elif args.command == "lifecycle":
            _emit(lifecycle_summary(), args.json)
        elif args.command == "add":
            _emit(workflow.add_knowledge(args.kind, args.statement, stage=args.stage, status=args.status, confidence=args.confidence, sources=args.source), args.json)
        elif args.command == "advance":
            _emit(f"Advanced to {workflow.advance(args.force)}", args.json)
        elif args.command == "work":
            _emit(workflow.add_work(args.title, args.objective, args.relates_to, args.accept, args.verify), args.json)
        elif args.command == "context":
            compiled = ContextCompiler(store).compile(args.work_id)
            print(compiled.as_json() if args.json else compiled.as_text(), end="\n" if args.json else "")
        elif args.command == "run":
            compiled = ContextCompiler(store).compile(args.work_id)
            runtime = HermesRuntime()
            request = RunRequest(compiled.as_text(), store.workspace, args.model)
            command = runtime.command(request)
            run = Run(store.next_id("RUN"), args.work_id, runtime.name, args.model or "default", context_digest=compiled.digest(), command=command)
            if args.execute:
                result = runtime.execute(request)
                run.status = "completed" if result.exit_code == 0 else "failed"
                run.exit_code = result.exit_code
                run.summary = result.stdout[-4000:]
            store.put("runs", run.to_dict())
            _emit(run, args.json)
        elif args.command == "verify":
            _emit([item.to_dict() for item in VerificationRunner(store).verify(args.work_id)], args.json)
        return 0
    except (StoreError, LifecycleBlocked, RuntimeError, ValueError) as exc:
        print(f"echel: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

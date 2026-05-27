from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .cockpit import cockpit_snapshot, run_cockpit_command
from .providers import ProviderError, chat
from .storage import PlatformStore


@dataclass
class PlatformRuntime:
    repo_root: Path
    store: PlatformStore


class ConnectProviderIn(BaseModel):
    name: str
    provider_type: str
    base_url: str
    model: str
    api_key: str


class ThreadIn(BaseModel):
    title: str


class ChatIn(BaseModel):
    thread_id: int
    provider_id: int | None = None
    message: str


class CockpitCommandIn(BaseModel):
    action: str
    args: dict = {}


def _run_echel_command(repo_root: Path, command_line: str) -> tuple[int, str]:
    allowed_prefixes = [
        "start",
        "doctor",
        "sync-memory",
        "migration plan",
        "conformance run",
        "adapters list",
        "status",
        "next",
        "plan",
        "build",
        "review",
        "graph report",
    ]
    cmd = command_line.strip()
    if not any(cmd.startswith(prefix) for prefix in allowed_prefixes):
        return 1, "blocked command; allowed: start, doctor, sync-memory, migration plan, conformance run, adapters list"
    proc = subprocess.run(
        ["python3", "tools/echel.py", *cmd.split()],
        cwd=str(repo_root),
        text=True,
        capture_output=True,
    )
    out = (proc.stdout + "\n" + proc.stderr).strip()
    return proc.returncode, out[:12000]


def create_app(repo_root: Path) -> FastAPI:
    db_path = repo_root / ".echel" / "platform" / "platform.db"
    store = PlatformStore(db_path)
    runtime = PlatformRuntime(repo_root=repo_root, store=store)

    app = FastAPI(title="Echel Platform", version="0.1.0")
    ui_dir = repo_root / "tools" / "echel" / "platform" / "ui"
    app.mount("/assets", StaticFiles(directory=str(ui_dir)), name="assets")

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(ui_dir / "index.html")

    @app.get("/api/health")
    def health() -> dict:
        return {"ok": True}

    @app.get("/api/cockpit")
    def cockpit() -> dict:
        return cockpit_snapshot(runtime.repo_root)

    @app.post("/api/cockpit/command")
    def cockpit_command(payload: CockpitCommandIn) -> dict:
        result = run_cockpit_command(runtime.repo_root, payload.action, payload.args)
        return {"ok": result.ok, "code": result.code, "output": result.output}

    @app.get("/api/providers")
    def list_providers() -> list[dict]:
        return [
            {
                "id": p.id,
                "name": p.name,
                "provider_type": p.provider_type,
                "base_url": p.base_url,
                "model": p.model,
            }
            for p in runtime.store.list_providers()
        ]

    @app.post("/api/providers/connect")
    def connect_provider(payload: ConnectProviderIn) -> dict:
        provider_id = runtime.store.upsert_provider(
            name=payload.name,
            provider_type=payload.provider_type,
            base_url=payload.base_url,
            model=payload.model,
            api_key=payload.api_key,
        )
        return {"ok": True, "provider_id": provider_id}

    @app.get("/api/threads")
    def list_threads() -> list[dict]:
        return runtime.store.list_threads()

    @app.post("/api/threads")
    def create_thread(payload: ThreadIn) -> dict:
        thread_id = runtime.store.create_thread(payload.title)
        return {"ok": True, "thread_id": thread_id}

    @app.get("/api/threads/{thread_id}/messages")
    def messages(thread_id: int) -> list[dict]:
        return runtime.store.list_messages(thread_id)

    @app.post("/api/chat")
    def run_chat(payload: ChatIn) -> dict:
        runtime.store.append_message(thread_id=payload.thread_id, role="user", content=payload.message, provider_id=payload.provider_id)

        if payload.message.startswith("/echel "):
            code, output = _run_echel_command(runtime.repo_root, payload.message[len("/echel "):])
            content = f"[echel exit={code}]\n{output}"
            runtime.store.append_message(thread_id=payload.thread_id, role="assistant", content=content, provider_id=None)
            return {"ok": True, "content": content}

        if payload.provider_id is None:
            raise HTTPException(status_code=400, detail="provider_id required for model chat")
        provider = runtime.store.get_provider(payload.provider_id)
        if provider is None:
            raise HTTPException(status_code=404, detail="provider not found")

        try:
            response = chat(provider, payload.message)
        except ProviderError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        runtime.store.append_message(thread_id=payload.thread_id, role="assistant", content=response, provider_id=payload.provider_id)
        return {"ok": True, "content": response}

    return app

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import re

from .config import ProjectConfig, resolve_symbolic_path
from .evidence import ensure_registry


GRAPH_FILE = "graph.json"


@dataclass(frozen=True)
class GraphNode:
    id: str
    type: str
    title: str
    source: str
    summary: str = ""


@dataclass(frozen=True)
class GraphEdge:
    from_id: str
    to_id: str
    type: str


@dataclass(frozen=True)
class GraphIssue:
    severity: str
    message: str


def wiki_root(repo_root: Path, cfg: ProjectConfig) -> Path:
    return resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)


def graph_path(repo_root: Path, cfg: ProjectConfig) -> Path:
    return wiki_root(repo_root, cfg) / GRAPH_FILE


def build_graph(repo_root: Path, cfg: ProjectConfig) -> dict:
    root = wiki_root(repo_root, cfg)
    nodes: dict[str, GraphNode] = {}
    edges: set[tuple[str, str, str]] = set()

    def add_node(node: GraphNode) -> None:
        if node.id not in nodes:
            nodes[node.id] = node

    def add_edge(from_id: str, to_id: str, edge_type: str) -> None:
        if from_id in nodes and to_id in nodes:
            edges.add((from_id, to_id, edge_type))

    project_title = _title(root / "project.md") or "Product"
    add_node(GraphNode("product:root", "product", project_title, "project.md", _section(root / "project.md", "Product Direction")))

    problem = _section(root / "problem.md", "Problem Statement")
    if _meaningful(problem):
        add_node(GraphNode("problem:primary", "problem", _compact(problem, 80), "problem.md", problem))
        add_edge("product:root", "problem:primary", "defines")

    solution = _section(root / "solution.md", "Solution Concept")
    if _meaningful(solution):
        add_node(GraphNode("solution:primary", "solution", _compact(solution, 80), "solution.md", solution))
        add_edge("problem:primary", "solution:primary", "addressed_by")

    for user in _bullets(_section(root / "users.md", "Primary Users")):
        uid = f"user:{_slug(user)}"
        add_node(GraphNode(uid, "user", user, "users.md", user))
        add_edge("product:root", uid, "serves")

    for need in _bullets(_section(root / "users.md", "Needs")):
        nid = f"need:{_slug(need)}"
        add_node(GraphNode(nid, "need", need, "users.md", need))
        for user in [n.id for n in nodes.values() if n.type == "user"]:
            add_edge(user, nid, "has_need")

    for feature in _bullets(_section(root / "solution.md", "Core Capabilities")):
        fid = f"feature:{_slug(feature)}"
        add_node(GraphNode(fid, "feature", feature, "solution.md", feature))
        add_edge("solution:primary", fid, "includes")
        for need in [n.id for n in nodes.values() if n.type == "need"]:
            add_edge(fid, need, "satisfies")

    for req in _bullets(_section(root / "scope.md", "MVP")):
        rid = f"requirement:{_slug(req)}"
        add_node(GraphNode(rid, "requirement", req, "scope.md", req))
        add_edge("product:root", rid, "requires")
        for feature in [n.id for n in nodes.values() if n.type == "feature"]:
            add_edge(feature, rid, "implements")

    for component in _bullets(_section(root / "architecture.md", "Key Components")):
        cid = f"component:{_slug(component)}"
        add_node(GraphNode(cid, "component", component, "architecture.md", component))
        for feature in [n.id for n in nodes.values() if n.type == "feature"]:
            add_edge(cid, feature, "supports")

    for workflow in _bullets(_section(root / "workflows.md", "Core Workflows")):
        wid = f"workflow:{_slug(workflow)}"
        add_node(GraphNode(wid, "workflow", workflow, "workflows.md", workflow))
        for user in [n.id for n in nodes.values() if n.type == "user"]:
            add_edge(wid, user, "serves")
        for feature in [n.id for n in nodes.values() if n.type == "feature"]:
            add_edge(feature, wid, "enables")

    for task in sorted((root / "work").glob("TASK-*.md")):
        tid = _task_id(task)
        if not tid:
            continue
        add_node(GraphNode(f"task:{tid}", "task", _title(task) or tid, str(task.relative_to(root)), _section(task, "Objective")))
        add_edge("product:root", f"task:{tid}", "planned_as")
        for req in [n.id for n in nodes.values() if n.type == "requirement"]:
            add_edge(f"task:{tid}", req, "delivers")

    for decision in sorted((root / "decisions").glob("ADR-*.md")):
        did = _adr_id(decision)
        if not did:
            continue
        add_node(GraphNode(f"decision:{did}", "decision", _title(decision) or did, str(decision.relative_to(root)), _section(decision, "Decision")))
        add_edge("product:root", f"decision:{did}", "constrained_by")

    evidence_registry = ensure_registry(repo_root / cfg.evidence_registry)
    artifacts = evidence_registry.get("artifacts", {}) if isinstance(evidence_registry, dict) else {}
    for evid, payload in sorted(artifacts.items()):
        if not isinstance(payload, dict):
            continue
        title = str(payload.get("title") or evid)
        source = str(payload.get("path") or cfg.evidence_registry)
        add_node(GraphNode(f"evidence:{evid}", "evidence", title, source, str(payload.get("summary", ""))))
        add_edge("product:root", f"evidence:{evid}", "has_evidence")
        for task in [n.id for n in nodes.values() if n.type == "task"]:
            if evid in task or evid in json.dumps(payload):
                add_edge(f"evidence:{evid}", task, "verifies")

    for risk in _risk_nodes(root):
        add_node(risk)
        add_edge("product:root", risk.id, "has_risk")

    for milestone in _milestone_nodes(root):
        add_node(milestone)
        add_edge("product:root", milestone.id, "tracks")
        for task in [n.id for n in nodes.values() if n.type == "task"]:
            add_edge(milestone.id, task, "includes")
        for req in [n.id for n in nodes.values() if n.type == "requirement"]:
            add_edge(milestone.id, req, "depends_on")

    manual = _manual_graph(root)
    for raw in manual.get("nodes", []):
        if isinstance(raw, dict) and {"id", "type", "title"}.issubset(raw):
            add_node(GraphNode(str(raw["id"]), str(raw["type"]), str(raw["title"]), str(raw.get("source", "manual")), str(raw.get("summary", ""))))
    for raw in manual.get("edges", []):
        if isinstance(raw, dict):
            add_edge(str(raw.get("from_id", "")), str(raw.get("to_id", "")), str(raw.get("type", "related_to")))

    payload = {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "nodes": [asdict(node) for node in sorted(nodes.values(), key=lambda n: n.id)],
        "edges": [
            {"from_id": src, "to_id": dst, "type": typ}
            for src, dst, typ in sorted(edges)
        ],
    }
    return payload


def write_graph(repo_root: Path, cfg: ProjectConfig) -> Path:
    payload = build_graph(repo_root, cfg)
    path = graph_path(repo_root, cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def load_graph(repo_root: Path, cfg: ProjectConfig) -> dict:
    path = graph_path(repo_root, cfg)
    if not path.exists():
        write_graph(repo_root, cfg)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_graph(graph: dict) -> list[GraphIssue]:
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    raw_ids = [n.get("id") for n in nodes if isinstance(n, dict)]
    ids = set(raw_ids)
    types = [n.get("type") for n in nodes if isinstance(n, dict)]
    issues: list[GraphIssue] = []

    for node_id in sorted({node_id for node_id in raw_ids if raw_ids.count(node_id) > 1}):
        issues.append(GraphIssue("critical", f"duplicate node id {node_id}"))

    for required in ["product", "problem", "user", "solution"]:
        if required not in types:
            issues.append(GraphIssue("major", f"missing {required} node"))
    if "requirement" not in types:
        issues.append(GraphIssue("major", "missing MVP requirement nodes"))
    if "task" not in types:
        issues.append(GraphIssue("major", "missing task nodes"))

    for edge in edges:
        if not isinstance(edge, dict):
            issues.append(GraphIssue("critical", "edge must be object"))
            continue
        if edge.get("from_id") not in ids:
            issues.append(GraphIssue("critical", f"edge has unknown from_id {edge.get('from_id')}"))
        if edge.get("to_id") not in ids:
            issues.append(GraphIssue("critical", f"edge has unknown to_id {edge.get('to_id')}"))

    task_edges = {(e.get("from_id"), e.get("type")) for e in edges if isinstance(e, dict)}
    for node in nodes:
        if isinstance(node, dict) and node.get("type") == "task":
            if (node.get("id"), "delivers") not in task_edges:
                issues.append(GraphIssue("major", f"task {node.get('id')} is not linked to a requirement"))

    for node in nodes:
        if isinstance(node, dict) and node.get("type") == "risk":
            summary = str(node.get("summary", ""))
            if "Mitigation:" not in summary or "Mitigation: TBD" in summary:
                issues.append(GraphIssue("major", f"risk {node.get('id')} has no mitigation"))
    return issues


def graph_summary(graph: dict, issues: list[GraphIssue] | None = None) -> str:
    nodes = [n for n in graph.get("nodes", []) if isinstance(n, dict)]
    edges = [e for e in graph.get("edges", []) if isinstance(e, dict)]
    counts: dict[str, int] = {}
    for node in nodes:
        counts[str(node.get("type", "unknown"))] = counts.get(str(node.get("type", "unknown")), 0) + 1
    issue_counts: dict[str, int] = {}
    for issue in issues or []:
        issue_counts[issue.severity] = issue_counts.get(issue.severity, 0) + 1
    lines = [
        "# Product Graph",
        "",
        f"- Nodes: {len(nodes)}",
        f"- Edges: {len(edges)}",
        f"- Critical issues: {issue_counts.get('critical', 0)}",
        f"- Major issues: {issue_counts.get('major', 0)}",
        f"- Minor issues: {issue_counts.get('minor', 0)}",
        "",
        "## Node Types",
    ]
    for key in sorted(counts):
        lines.append(f"- {key}: {counts[key]}")
    return "\n".join(lines)


def graph_status(repo_root: Path, cfg: ProjectConfig) -> str:
    graph = build_graph(repo_root, cfg)
    issues = validate_graph(graph)
    lines = [graph_summary(graph, issues), "", "## Graph Integrity"]
    lines.extend([f"- **{i.severity}** {i.message}" for i in issues[:10]] or ["- No integrity issues found."])
    if len(issues) > 10:
        lines.append(f"- ...and {len(issues) - 10} more issues.")
    return "\n".join(lines)


def write_graph_report(repo_root: Path, cfg: ProjectConfig) -> Path:
    root = wiki_root(repo_root, cfg)
    graph = build_graph(repo_root, cfg)
    issues = validate_graph(graph)
    report = root / "reports" / "product-graph-report.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    lines = ["---", "type: analysis", "status: active", "---", "", "# Product Graph Report", "", graph_summary(graph, issues), "", "## Issues"]
    lines.extend([f"- **{i.severity}** {i.message}" for i in issues] or ["- None"])
    lines += ["", "## Coverage"]
    for node_type in ["problem", "user", "need", "solution", "feature", "requirement", "workflow", "component", "task", "evidence", "decision", "risk", "milestone", "release"]:
        count = sum(1 for n in graph.get("nodes", []) if isinstance(n, dict) and n.get("type") == node_type)
        lines.append(f"- {node_type}: {count}")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_graph(repo_root, cfg)
    return report


def add_feature(repo_root: Path, cfg: ProjectConfig, title: str, summary: str) -> Path:
    root = wiki_root(repo_root, cfg)
    path = root / "solution.md"
    text = path.read_text(encoding="utf-8")
    body = _section(path, "Core Capabilities")
    items = _bullets(body)
    if title not in items:
        items.append(title)
    text = _replace_section(text, "Core Capabilities", "\n".join(f"- {item}" for item in items))
    if summary:
        text = _replace_section(text, "Differentiation", summary)
    path.write_text(text, encoding="utf-8")
    write_graph(repo_root, cfg)
    return path


def add_risk(repo_root: Path, cfg: ProjectConfig, title: str, impact: str, mitigation: str) -> Path:
    root = wiki_root(repo_root, cfg)
    path = root / "risks.md"
    if not path.exists():
        path.write_text("---\ntype: risks\nstatus: active\n---\n# Risks\n", encoding="utf-8")
    text = path.read_text(encoding="utf-8").rstrip()
    text += f"\n\n## {title}\n\n- Impact: {impact or 'TBD'}\n- Mitigation: {mitigation or 'TBD'}\n"
    path.write_text(text + "\n", encoding="utf-8")
    write_graph(repo_root, cfg)
    return path


def add_manual_link(repo_root: Path, cfg: ProjectConfig, from_id: str, to_id: str, edge_type: str) -> Path:
    root = wiki_root(repo_root, cfg)
    path = root / "graph.manual.json"
    manual = _manual_graph(root)
    manual.setdefault("version", 1)
    manual.setdefault("nodes", [])
    manual.setdefault("edges", [])
    edge = {"from_id": from_id, "to_id": to_id, "type": edge_type}
    if edge not in manual["edges"]:
        manual["edges"].append(edge)
    path.write_text(json.dumps(manual, indent=2) + "\n", encoding="utf-8")
    write_graph(repo_root, cfg)
    return path


def add_milestone_node(repo_root: Path, cfg: ProjectConfig, name: str, kind: str, summary: str) -> Path:
    root = wiki_root(repo_root, cfg)
    path = root / "milestones.md"
    if not path.exists():
        path.write_text("---\ntype: milestones\nstatus: active\n---\n# Milestones\n", encoding="utf-8")
    text = path.read_text(encoding="utf-8").rstrip()
    heading = f"## {name}"
    block = f"{heading}\n\n- Type: {kind}\n- Summary: {summary or 'TBD'}\n- Status: planned\n"
    if heading in text:
        pattern = rf"{re.escape(heading)}\n(.*?)(?=\n## |\Z)"
        text = re.sub(pattern, block.rstrip(), text, count=1, flags=re.DOTALL)
    else:
        text += f"\n\n{block.rstrip()}"
    path.write_text(text + "\n", encoding="utf-8")
    write_graph(repo_root, cfg)
    return path


def _manual_graph(root: Path) -> dict:
    path = root / "graph.manual.json"
    if not path.exists():
        return {"version": 1, "nodes": [], "edges": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"version": 1, "nodes": [], "edges": []}
    return data if isinstance(data, dict) else {"version": 1, "nodes": [], "edges": []}


def _risk_nodes(root: Path) -> list[GraphNode]:
    path = root / "risks.md"
    if not path.exists():
        return []
    nodes = []
    current_title = ""
    current_lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if current_title:
                nodes.append(GraphNode(f"risk:{_slug(current_title)}", "risk", current_title, "risks.md", " ".join(current_lines)))
            current_title = line[3:].strip()
            current_lines = []
        elif current_title:
            current_lines.append(line.strip())
    if current_title:
        nodes.append(GraphNode(f"risk:{_slug(current_title)}", "risk", current_title, "risks.md", " ".join(current_lines)))
    return nodes


def _milestone_nodes(root: Path) -> list[GraphNode]:
    path = root / "milestones.md"
    if not path.exists():
        return []
    nodes = []
    current_title = ""
    current_lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if current_title:
                nodes.append(_milestone_node(current_title, current_lines))
            current_title = line[3:].strip()
            current_lines = []
        elif current_title:
            current_lines.append(line.strip())
    if current_title:
        nodes.append(_milestone_node(current_title, current_lines))
    return nodes


def _milestone_node(title: str, lines: list[str]) -> GraphNode:
    summary = " ".join(lines)
    node_type = "release" if "Type: release" in summary else "milestone"
    return GraphNode(f"{node_type}:{_slug(title)}", node_type, title, "milestones.md", summary)


def _section(path: Path, heading: str) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"## {re.escape(heading)}\n(.*?)(?=\n## |\Z)", text, flags=re.DOTALL)
    return match.group(1).strip() if match else ""


def _replace_section(text: str, heading: str, body: str) -> str:
    pattern = rf"(## {re.escape(heading)}\n)(.*?)(?=\n## |\Z)"
    if re.search(pattern, text, flags=re.DOTALL):
        return re.sub(pattern, lambda m: f"{m.group(1)}{body.rstrip()}\n", text, count=1, flags=re.DOTALL)
    return text.rstrip() + f"\n\n## {heading}\n{body.rstrip()}\n"


def _bullets(text: str) -> list[str]:
    out = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            item = stripped[2:].strip()
            if _meaningful(item):
                out.append(item)
        elif _meaningful(stripped) and stripped != "TBD":
            out.append(stripped)
    return out


def _title(path: Path) -> str:
    if not path.exists():
        return ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _task_id(path: Path) -> str:
    match = re.match(r"(TASK-\d{4})-", path.name)
    return match.group(1) if match else ""


def _adr_id(path: Path) -> str:
    match = re.search(r"(ADR-\d{4})", path.name)
    return match.group(1) if match else ""


def _compact(text: str, limit: int = 120) -> str:
    cleaned = " ".join(line.strip("- ").strip() for line in text.splitlines() if line.strip())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rstrip() + "..."


def _meaningful(value: str) -> bool:
    return bool(value.strip()) and value.strip() not in {"TBD", "- TBD"}


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:80] or "item"

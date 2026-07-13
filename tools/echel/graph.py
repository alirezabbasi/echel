from __future__ import annotations

from dataclasses import dataclass, asdict, replace
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
    trace_id: str = ""
    statement_type: str = ""
    confidence: str = ""
    source_stage: str = ""
    verification_status: str = ""


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
            nodes[node.id] = _with_metadata(node)

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

    for lifecycle_node in _lifecycle_nodes(repo_root, root):
        add_node(lifecycle_node)
        add_edge("product:root", lifecycle_node.id, "has_lifecycle_artifact")

    manual = _manual_graph(root)
    for raw in manual.get("nodes", []):
        if isinstance(raw, dict) and {"id", "type", "title"}.issubset(raw):
            add_node(
                GraphNode(
                    str(raw["id"]),
                    str(raw["type"]),
                    str(raw["title"]),
                    str(raw.get("source", "manual")),
                    str(raw.get("summary", "")),
                    str(raw.get("trace_id", "")),
                    str(raw.get("statement_type", "")),
                    str(raw.get("confidence", "")),
                    str(raw.get("source_stage", raw.get("stage", ""))),
                    str(raw.get("verification_status", "")),
                )
            )
    for raw in manual.get("edges", []):
        if isinstance(raw, dict):
            add_edge(str(raw.get("from_id", "")), str(raw.get("to_id", "")), str(raw.get("type", "related_to")))

    for source, target, edge_type in _lifecycle_edges(nodes):
        add_edge(source, target, edge_type)

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
        if isinstance(node, dict):
            for required_metadata in ["statement_type", "confidence", "source_stage", "verification_status"]:
                if not str(node.get(required_metadata, "")).strip():
                    issues.append(GraphIssue("major", f"node {node.get('id')} is missing {required_metadata}"))
        if isinstance(node, dict) and node.get("type") == "risk":
            summary = str(node.get("summary", ""))
            if "Mitigation:" not in summary or "Mitigation: TBD" in summary:
                issues.append(GraphIssue("major", f"risk {node.get('id')} has no mitigation"))
        if isinstance(node, dict) and node.get("type") == "assumption":
            confidence = str(node.get("confidence", "")).lower()
            status = str(node.get("verification_status", "")).lower()
            if confidence == "low" and status not in {"verified", "accepted", "resolved"}:
                issues.append(GraphIssue("critical", f"assumption {node.get('id')} has low confidence and is not verified"))
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
    for node_type in _report_node_types():
        count = sum(1 for n in graph.get("nodes", []) if isinstance(n, dict) and n.get("type") == node_type)
        lines.append(f"- {node_type}: {count}")
    lines += ["", "## Metadata Coverage"]
    nodes = [n for n in graph.get("nodes", []) if isinstance(n, dict)]
    for field in ["statement_type", "confidence", "source_stage", "verification_status"]:
        populated = sum(1 for n in nodes if str(n.get(field, "")).strip())
        lines.append(f"- {field}: {populated}/{len(nodes)}")
    traceable = sum(1 for n in nodes if str(n.get("trace_id", "")).strip())
    lines.append(f"- trace_id: {traceable}/{len(nodes)}")
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


def _lifecycle_nodes(repo_root: Path, root: Path) -> list[GraphNode]:
    nodes: list[GraphNode] = []

    def add(
        node_id: str,
        node_type: str,
        title: str,
        source: str,
        summary: str = "",
        trace_id: str = "",
        statement_type: str = "",
        confidence: str = "",
        verification_status: str = "",
    ) -> None:
        nodes.append(GraphNode(node_id, node_type, title, source, summary or title, trace_id, statement_type, confidence, "", verification_status))

    def add_document(node_type: str, path: Path, title: str | None = None, summary: str = "") -> None:
        if not path.exists():
            return
        rel = _source_path(path, repo_root, root)
        add(f"{node_type}:{_slug(title or _title(path) or path.stem)}", node_type, title or _title(path) or path.stem, rel, summary or _compact(_section(path, "Purpose") or _title(path)))

    pds = root / "discovery" / "product-discovery-spec.md"
    if pds.exists():
        add("discovery-item:product-discovery-spec", "discovery-item", "Product Discovery Specification", "discovery/product-discovery-spec.md", _compact(_section(pds, "01 Executive Summary") or _title(pds)))
        for row in _table_rows(pds):
            trace_id = _trace_id(row)
            if trace_id and trace_id.startswith(("P-", "U-", "O-", "WF-", "PP-", "S-", "NC-", "C-", "R-", "CMP-")):
                title = _row_title(row, trace_id)
                add(
                    f"discovery-item:{trace_id}",
                    "discovery-item",
                    title,
                    "discovery/product-discovery-spec.md",
                    " | ".join(row),
                    trace_id,
                    _row_statement_type(row, "observation"),
                    _row_confidence(row),
                    _row_verification_status(row),
                )
            if trace_id and trace_id.startswith("B-"):
                add(
                    f"buyer:{trace_id}",
                    "buyer",
                    _row_title(row, trace_id),
                    "discovery/product-discovery-spec.md",
                    " | ".join(row),
                    trace_id,
                    _row_statement_type(row, "observation"),
                    _row_confidence(row),
                    _row_verification_status(row),
                )

    assumptions = root / "discovery" / "assumptions.md"
    assumption_seen = False
    hypothesis_seen = False
    if assumptions.exists():
        for row in _table_rows(assumptions):
            trace_id = _trace_id(row)
            if not trace_id:
                continue
            if trace_id.startswith("A-"):
                assumption_seen = True
                add(
                    f"assumption:{trace_id}",
                    "assumption",
                    _row_title(row, trace_id),
                    "discovery/assumptions.md",
                    " | ".join(row),
                    trace_id,
                    "assumption",
                    _row_confidence(row),
                    _row_verification_status(row),
                )
            elif trace_id.startswith("H-"):
                hypothesis_seen = True
                add(
                    f"hypothesis:{trace_id}",
                    "hypothesis",
                    _row_title(row, trace_id),
                    "discovery/assumptions.md",
                    " | ".join(row),
                    trace_id,
                    "hypothesis",
                    _row_confidence(row),
                    _row_verification_status(row),
                )
        if not assumption_seen:
            add("assumption:register", "assumption", "Assumption Register", "discovery/assumptions.md", "Lifecycle register for assumptions; no non-template assumption rows have been captured yet.")
        if not hypothesis_seen:
            add("hypothesis:register", "hypothesis", "Hypothesis Register", "discovery/assumptions.md", "Lifecycle register for hypotheses; no non-template hypothesis rows have been captured yet.")

    buyer_model = root / "strategy" / "buyer-user-model.md"
    if buyer_model.exists():
        add("buyer:economic-buyer", "buyer", "Economic Buyer", "strategy/buyer-user-model.md", _compact(_section(buyer_model, "Stakeholder Roles")))
        stakeholder_count = 0
        for row in _table_rows(buyer_model):
            if len(row) >= 1 and row[0] in {"Economic Buyer", "User", "Approver", "Influencer", "Blocker", "Operator"}:
                stakeholder_count += 1
                add(f"stakeholder:{_slug(row[0])}", "stakeholder", row[0], "strategy/buyer-user-model.md", " | ".join(row))
        if stakeholder_count == 0:
            for role in ["Economic Buyer", "User", "Operator"]:
                if _meaningful(_section(buyer_model, role)):
                    add(f"stakeholder:{_slug(role)}", "stakeholder", role, "strategy/buyer-user-model.md", _compact(_section(buyer_model, role)))

    for strategy_doc in sorted((root / "strategy").glob("*.md")):
        add_document("strategy", strategy_doc, summary=_compact(_section(strategy_doc, "Purpose") or _section(strategy_doc, "Primary ICP") or _title(strategy_doc)))

    add_document("business-rule", root / "domain" / "policies-and-rules.md", "Business Rule Register")
    add_document("domain-concept", root / "domain" / "ubiquitous-language.md", "Domain Concept Register")
    add_document("bounded-context", root / "domain" / "bounded-contexts.md", "Bounded Context Register")

    component_doc = root / "architecture" / "component-architecture.md"
    if component_doc.exists():
        for row in _table_rows(component_doc):
            trace_id = _trace_id(row)
            if trace_id and trace_id.startswith("ARCH-"):
                add(f"architecture-component:{trace_id}", "architecture-component", _row_title(row, trace_id), "architecture/component-architecture.md", " | ".join(row))
        if not any(node.type == "architecture-component" for node in nodes):
            add_document("architecture-component", component_doc, "Architecture Component Register")

    for test_path in sorted((repo_root / "generated" / "product-repository" / "tests").glob("test*.py")):
        add(f"test:{_slug(test_path.stem)}", "test", test_path.name, _source_path(test_path, repo_root, root), "Generated repository validation test.")
    repo_test = repo_root / "tests" / "test_vnext_lifecycle.py"
    if repo_test.exists():
        add("test:vnext-lifecycle", "test", "vNext Lifecycle Regression Tests", _source_path(repo_test, repo_root, root), "Regression tests for lifecycle graph, gates, and generated artifacts.")

    deployment_paths = [
        repo_root / "generated" / "product-repository" / ".github" / "workflows" / "ci.yml",
        root / "roadmap" / "release-plan.md",
        *sorted((root / "deployment").glob("*.md")),
    ]
    for deployment_path in deployment_paths:
        add_document("deployment-artifact", deployment_path)

    operation_paths = [
        repo_root / "prompts" / "playbooks" / "operate.md",
        root / "agents" / "handoff-protocol.md",
        root / "execution" / "phase-3-production.md",
        *sorted((root / "operations").glob("*.md")),
    ]
    for operation_path in operation_paths:
        add_document("operation-artifact", operation_path)

    contradictions = root / "governance" / "contradictions.md"
    if contradictions.exists():
        for row in _contradiction_rows(contradictions):
            add(
                f"contradiction:{row['id']}",
                "contradiction",
                row["title"],
                "governance/contradictions.md",
                row["summary"],
                row["id"],
                "observation",
                "medium",
                row["status"].lower() or "open",
            )

    governance_paths = [
        repo_root / "prompts" / "playbooks" / "govern.md",
        root / "agents" / "role-model.md",
        root / "execution" / "phase-4-evolution.md",
        *sorted((root / "governance").glob("*.md")),
    ]
    for governance_path in governance_paths:
        add_document("governance-artifact", governance_path)

    learning_records = root / "operations" / "learning-records.md"
    if learning_records.exists():
        for row in _table_rows(learning_records):
            trace_id = _trace_id(row)
            if trace_id and trace_id.startswith("LEARN-"):
                add(
                    f"learning:{trace_id}",
                    "learning",
                    _row_title(row, trace_id),
                    "operations/learning-records.md",
                    " | ".join(row),
                    trace_id,
                    "observation",
                    "medium",
                    _row_verification_status(row) or "captured",
                )

    add_document("contradiction", root / "knowledge" / "contradiction-management.md", "Contradiction Management")
    add_document("contradiction", root / "canon" / "canon-drift.md", "Canon Drift")
    add_document("learning", root / "log.md", "Lifecycle Log")
    add_document("learning", root / "knowledge" / "project-intelligence-compounding-model.md", "Project Intelligence Compounding Model")

    return nodes


def _lifecycle_edges(nodes: dict[str, GraphNode]) -> list[tuple[str, str, str]]:
    by_type: dict[str, list[str]] = {}
    for node in nodes.values():
        by_type.setdefault(node.type, []).append(node.id)

    edges: list[tuple[str, str, str]] = []
    for discovery in by_type.get("discovery-item", []):
        for target_type in ["assumption", "hypothesis", "buyer", "stakeholder", "strategy"]:
            for target in by_type.get(target_type, [])[:20]:
                edges.append((discovery, target, "informs"))
    for strategy in by_type.get("strategy", []):
        for requirement in by_type.get("requirement", [])[:40]:
            edges.append((strategy, requirement, "refines"))
    for requirement in by_type.get("requirement", []):
        for target_type in ["domain-concept", "bounded-context", "business-rule"]:
            for target in by_type.get(target_type, [])[:40]:
                edges.append((requirement, target, "constrains"))
    for domain in by_type.get("domain-concept", []):
        for component in by_type.get("architecture-component", []):
            edges.append((domain, component, "realized_by"))
    for component in by_type.get("architecture-component", []):
        for task in by_type.get("task", [])[:80]:
            edges.append((component, task, "planned_as"))
    for test in by_type.get("test", []):
        for requirement in by_type.get("requirement", [])[:40]:
            edges.append((test, requirement, "verifies"))
    for deployment in by_type.get("deployment-artifact", []):
        for test in by_type.get("test", []):
            edges.append((deployment, test, "runs"))
    for operation in by_type.get("operation-artifact", []):
        for deployment in by_type.get("deployment-artifact", []):
            edges.append((operation, deployment, "operates"))
    for contradiction in by_type.get("contradiction", []):
        for learning in by_type.get("learning", []):
            edges.append((contradiction, learning, "feeds"))
    return edges


def _report_node_types() -> list[str]:
    return [
        "product",
        "problem",
        "user",
        "need",
        "solution",
        "feature",
        "discovery-item",
        "assumption",
        "hypothesis",
        "buyer",
        "stakeholder",
        "strategy",
        "requirement",
        "domain-concept",
        "bounded-context",
        "business-rule",
        "workflow",
        "component",
        "architecture",
        "architecture-component",
        "task",
        "test",
        "evidence",
        "decision",
        "risk",
        "milestone",
        "release",
        "deployment-artifact",
        "operation-artifact",
        "governance-artifact",
        "contradiction",
        "learning",
    ]


def _with_metadata(node: GraphNode) -> GraphNode:
    summary = node.summary or ""
    return replace(
        node,
        trace_id=node.trace_id or _trace_id_from_node_id(node.id),
        statement_type=_normalize_metadata(node.statement_type) or _infer_statement_type(node.type, summary),
        confidence=_normalize_metadata(node.confidence) or _extract_confidence(summary) or "unknown",
        source_stage=_normalize_metadata(node.source_stage) or _infer_source_stage(node.source, node.type),
        verification_status=_normalize_metadata(node.verification_status) or _infer_verification_status(node.type, summary),
    )


def _infer_statement_type(node_type: str, summary: str = "") -> str:
    explicit = _extract_statement_type(summary)
    if explicit:
        return explicit
    mapping = {
        "assumption": "assumption",
        "hypothesis": "hypothesis",
        "risk": "risk",
        "decision": "decision",
        "release": "decision",
        "milestone": "decision",
        "requirement": "decision",
        "business-rule": "constraint",
        "bounded-context": "decision",
        "architecture": "decision",
        "architecture-component": "decision",
        "deployment-artifact": "decision",
        "operation-artifact": "decision",
        "governance-artifact": "decision",
        "contradiction": "observation",
        "learning": "observation",
        "evidence": "fact",
        "test": "fact",
    }
    return mapping.get(node_type, "observation")


def _infer_source_stage(source: str, node_type: str) -> str:
    first = source.split("/", 1)[0]
    stage_by_prefix = {
        "discovery": "discovery",
        "canon": "canon",
        "strategy": "strategy",
        "requirements": "requirements",
        "domain": "domain",
        "architecture": "architecture",
        "roadmap": "roadmap",
        "execution": "execution",
        "deployment": "deployment",
        "operations": "operations",
        "governance": "governance",
        "work": "execution",
        "decisions": "governance",
        "reports": "validation",
        "milestones.md": "release",
        "risks.md": "governance",
        "log.md": "evolution",
        "manual": "manual",
    }
    if first in stage_by_prefix:
        return stage_by_prefix[first]
    if source in stage_by_prefix:
        return stage_by_prefix[source]
    stage_by_type = {
        "component": "architecture",
        "workflow": "domain",
        "requirement": "requirements",
        "business-rule": "domain",
        "domain-concept": "domain",
        "bounded-context": "domain",
        "architecture": "architecture",
        "architecture-component": "architecture",
        "test": "validation",
        "evidence": "validation",
        "deployment-artifact": "deployment",
        "operation-artifact": "operations",
        "governance-artifact": "governance",
        "learning": "evolution",
        "contradiction": "governance",
        "task": "execution",
    }
    return stage_by_type.get(node_type, "product-memory")


def _infer_verification_status(node_type: str, summary: str) -> str:
    lowered = summary.lower()
    if "validated" in lowered or "verified" in lowered or node_type in {"evidence", "test"}:
        return "verified"
    if "resolved" in lowered:
        return "resolved"
    if "accepted" in lowered or node_type in {"decision", "release"}:
        return "accepted"
    if "done" in lowered or "status: done" in lowered:
        return "done"
    if "active" in lowered:
        return "active"
    if "draft" in lowered:
        return "draft"
    return "unverified"


def _extract_statement_type(text: str) -> str:
    allowed = ["fact", "observation", "assumption", "hypothesis", "decision", "constraint", "risk", "question"]
    cleaned = text.strip().strip("`").lower()
    if cleaned in allowed:
        return cleaned
    match = re.search(r"\b(?:statement type|statement_type)\s*[:|]\s*`?(fact|observation|assumption|hypothesis|decision|constraint|risk|question)\b", text, flags=re.IGNORECASE)
    if match:
        return match.group(1).lower()
    return ""


def _extract_confidence(text: str) -> str:
    allowed = ["high", "medium", "low"]
    cleaned = text.strip().strip("`").lower()
    if cleaned in allowed:
        return cleaned
    match = re.search(r"\bconfidence\s*[:|]\s*`?(high|medium|low)\b", text, flags=re.IGNORECASE)
    if match:
        return match.group(1).lower()
    return ""


def _normalize_metadata(value: str) -> str:
    cleaned = value.strip().lower()
    return "" if cleaned in {"", "tbd", "none", "n/a", "-"} else cleaned


def _section(path: Path, heading: str) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"## {re.escape(heading)}\n(.*?)(?=\n## |\Z)", text, flags=re.DOTALL)
    return match.group(1).strip() if match else ""


def _table_rows(path: Path) -> list[list[str]]:
    if not path.exists():
        return []
    rows: list[list[str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cells = [cell.strip().strip("`") for cell in stripped.strip("|").split("|")]
        if cells and cells[0].lower() != "id":
            rows.append(cells)
    return rows


def _trace_id(row: list[str]) -> str:
    for cell in row:
        match = re.search(r"\b(?:P|U|B|O|WF|PP|S|NC|C|R|CMP|A|H|REQ|NFR|AC|BR|DM|BC|AGG|DE|ARCH|LEARN|CONTR)-\d{3,4}\b", cell)
        if match:
            return match.group(0)
    return ""


def _trace_id_from_node_id(node_id: str) -> str:
    match = re.search(r"\b(?:P|U|B|O|WF|PP|S|NC|C|R|CMP|A|H|REQ|NFR|AC|BR|DM|BC|AGG|DE|ARCH|ADR|TASK|TEST|EVID|LEARN|CONTR)-\d{3,4}\b", node_id)
    return match.group(0) if match else ""


def _row_statement_type(row: list[str], fallback: str = "") -> str:
    for cell in row:
        value = _extract_statement_type(cell)
        if value:
            return value
    return fallback


def _row_confidence(row: list[str]) -> str:
    for cell in row:
        value = _extract_confidence(cell)
        if value:
            return value
    return ""


def _row_verification_status(row: list[str]) -> str:
    for cell in row:
        cleaned = cell.strip().lower()
        if cleaned in {"validated", "verified", "accepted", "resolved", "active", "draft", "open", "done", "generated", "captured"}:
            return cleaned
    return ""


def _row_title(row: list[str], fallback: str) -> str:
    for cell in row[1:]:
        if _meaningful(cell):
            return f"{fallback} {cell}"
    return fallback


def _contradiction_rows(path: Path) -> list[dict[str, str]]:
    rows = []
    for row in _table_rows(path):
        if not row or not re.match(r"^CONTR-\d{3}$", row[0]) or row[0] == "CONTR-000":
            continue
        status = row[1] if len(row) > 1 else "Open"
        title = row[2] if len(row) > 2 else row[0]
        source = row[3] if len(row) > 3 else "unknown"
        links = row[5] if len(row) > 5 else "Unlinked"
        impact = row[6] if len(row) > 6 else ""
        task = row[7] if len(row) > 7 else ""
        rows.append(
            {
                "id": row[0],
                "status": status,
                "title": title,
                "summary": f"Status: {status}. Source: {source}. Links: {links}. Impact: {impact}. Resolution task: {task}.",
            }
        )
    return rows


def _source_path(path: Path, repo_root: Path, wiki_root_path: Path) -> str:
    try:
        return str(path.relative_to(wiki_root_path))
    except ValueError:
        try:
            return str(path.relative_to(repo_root))
        except ValueError:
            return str(path)


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

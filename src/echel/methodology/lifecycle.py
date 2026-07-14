from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Stage:
    id: str
    title: str
    purpose: str
    required_kinds: tuple[str, ...] = ()


STAGES: tuple[Stage, ...] = (
    Stage("idea", "Raw idea", "Capture the smallest useful expression of intent."),
    Stage("problem", "Problem definition", "Define the affected people, present workflow, pain, and evidence.", ("problem", "user")),
    Stage("vision", "Vision and opportunity", "Define the desired transformation, opportunity, success, and non-goals.", ("vision", "success")),
    Stage("strategy", "Product strategy", "Choose target market, value proposition, wedge, and business assumptions.", ("strategy",)),
    Stage("requirements", "Requirements", "Express testable outcomes and explicit scope.", ("requirement",)),
    Stage("domain", "Domain model", "Stabilize language, rules, concepts, and boundaries needed by the product.", ("domain",)),
    Stage("architecture", "Architecture", "Choose the simplest system shape that satisfies current constraints.", ("architecture",)),
    Stage("roadmap", "Implementation roadmap", "Order outcomes by value, risk, and dependency.", ("roadmap",)),
    Stage("execution-plan", "Phased execution plan", "Turn roadmap outcomes into coherent delivery phases.", ("phase",)),
    Stage("tasks", "Detailed tasks", "Create bounded, verifiable units of agent work.", ("task",)),
    Stage("repository", "Repository structure", "Establish only the code structure required for planned work.", ("repository",)),
    Stage("implementation", "Implementation", "Execute work while preserving decisions and discoveries.", ("implementation",)),
    Stage("validation", "Testing and validation", "Verify outcomes and capture reproducible evidence.", ("validation",)),
    Stage("deployment", "Deployment", "Release safely with rollback and operational ownership.", ("deployment",)),
    Stage("operations", "Operations and evolution", "Learn from production and continuously revise product knowledge.", ("operation",)),
)


def get_stage(stage_id: str) -> Stage:
    for stage in STAGES:
        if stage.id == stage_id:
            return stage
    raise ValueError(f"unknown lifecycle stage: {stage_id}")


def next_stage(stage_id: str) -> Stage | None:
    for index, stage in enumerate(STAGES):
        if stage.id == stage_id:
            return STAGES[index + 1] if index + 1 < len(STAGES) else None
    raise ValueError(f"unknown lifecycle stage: {stage_id}")

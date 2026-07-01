---
type: schema
status: active
---
# Traceability Schema

This schema defines the methodology ID system for Echel vNext. It establishes stable traceability identifiers for every important artifact item, maps IDs to lifecycle stages, specifies naming rules, and plans the validation logic that ensures downstream artifacts preserve links to upstream sources.

## Purpose

Traceability IDs prevent silent intent loss as a product moves from raw idea through discovery, canon, strategy, requirements, domain modeling, architecture, execution, validation, release, and operations. Every important item receives a stable identifier that downstream artifacts can reference. When an upstream assumption changes, its ID becomes the anchor for propagating that change through every dependent stage.

## ID Families

Each artifact category has a dedicated prefix and zero-padded numeric suffix.

| Prefix | Category | Example | Lifecycle Stage |
| --- | --- | --- | --- |
| `P-###` | Problem or pain point | `P-001` | discovery |
| `U-###` | User | `U-001` | discovery |
| `B-###` | Buyer or business stakeholder | `B-001` | discovery |
| `O-###` | Operator or support role | `O-001` | discovery |
| `WF-###` | Current or target workflow | `WF-001` | discovery |
| `PP-###` | Pain point | `PP-001` | discovery |
| `A-###` | Assumption | `A-001` | discovery |
| `H-###` | Hypothesis | `H-001` | discovery |
| `R-###` | Risk | `R-001` | discovery, canon, strategy |
| `S-###` | Success criterion | `S-001` | discovery |
| `Q-###` | Open question | `Q-001` | discovery |
| `C-###` | Constraint | `C-001` | discovery, canon |
| `NC-###` | Non-goal or explicit exclusion | `NC-001` | discovery |
| `BR-###` | Business rule | `BR-001` | discovery, domain |
| `DM-###` | Domain concept or entity | `DM-001` | domain |
| `BC-###` | Bounded context | `BC-001` | domain |
| `DE-###` | Domain event | `DE-001` | domain |
| `REQ-###` | Requirement | `REQ-001` | requirements |
| `NFR-###` | Non-functional requirement | `NFR-001` | requirements |
| `AC-###` | Acceptance criterion | `AC-001` | requirements |
| `ICP-###` | Ideal customer profile entry | `ICP-001` | strategy |
| `PW-###` | Positioning or market wedge | `PW-001` | strategy |
| `CMP-###` | Competitive alternative | `CMP-001` | strategy |
| `PMF-###` | PMF evidence item | `PMF-001` | strategy |
| `ADR-####` | Architectural decision record | `ADR-0001` | architecture |
| `ARCH-###` | Architecture component or choice | `ARCH-001` | architecture |
| `TASK-####` | Execution task | `TASK-0001` | execution-planning, implementation |
| `TEST-###` | Test or validation case | `TEST-001` | validation |
| `EVID-###` | Evidence artifact | `EVID-001` | implementation, validation |
| `GATE-###` | Gate definition | `GATE-001` | governance-integrity |
| `HANDOFF-###` | Stage handoff summary | `HANDOFF-001` | any stage transition |
| `INC-###` | Incident | `INC-001` | operations-evolution |
| `RCA-###` | Root cause analysis | `RCA-001` | operations-evolution |
| `EVOL-###` | Evolution backlog item | `EVOL-001` | operations-evolution |
| `DEC-###` | Governance decision | `DEC-001` | governance-integrity |
| `MEM-###` | Memory record | `MEM-0001` | any stage |

## Naming Rules

### Format

All IDs follow the pattern: `{PREFIX}-{SUFFIX}`

- Prefix: uppercase letters, may include hyphens for multi-letter codes (e.g., `NFR`, `ADR`).
- Separator: single hyphen.
- Suffix: minimum three digits, zero-padded. `ADR` and `TASK` use four digits because they are high-volume.

### Uniqueness

- Every ID must be globally unique across the entire product repository.
- No two artifacts of any type may share the same ID.
- When an artifact is superseded, the old ID is marked `superseded_by` and a new ID is assigned. The old ID must not be reused.

### Case Sensitivity

- ID prefixes are case-insensitive for lookup but must be stored in uppercase.
- Slug components derived from titles use lowercase alphanumeric characters and hyphens.

### Assignment

- IDs are assigned at artifact creation time.
- The creator is responsible for selecting the next available numeric suffix within the prefix family.
- Sequential assignment is preferred. Gaps are allowed but must be justified in the governance audit.

## Artifact Object Shape

Every traceable artifact should support these metadata fields:

```json
{
  "id": "REQ-001",
  "type": "requirement",
  "title": "User authentication",
  "statement_type": "decision",
  "confidence": "high",
  "stage": "requirements",
  "source_ids": ["A-001", "BR-003"],
  "supersedes": null,
  "superseded_by": null,
  "created_at": "2026-07-02",
  "updated_at": "2026-07-02"
}
```

Required fields:

- `id`: the traceability identifier.
- `type`: artifact category matching the ID prefix.
- `title`: human-readable name.
- `statement_type`: one of `fact`, `observation`, `assumption`, `hypothesis`, `decision`, `constraint`, `risk`, `question`.
- `confidence`: one of `high`, `medium`, `low`.
- `stage`: lifecycle stage where the artifact was created or is primarily maintained.
- `source_ids`: list of upstream IDs that this artifact references or refines.

Optional fields:

- `supersedes`: ID of an earlier artifact this one replaces.
- `superseded_by`: ID of a later artifact that replaces this one.
- `created_at`: ISO date of creation.
- `updated_at`: ISO date of last meaningful update.

## Stage Mapping

Traceability IDs are assigned within lifecycle stages but may be referenced across stages. The following table shows where each ID family originates and where it is commonly referenced.

| ID Family | Origin Stage | Referenced By |
| --- | --- | --- |
| `P-###` | discovery | canon, strategy, requirements, domain, tasks |
| `U-###` | discovery | canon, strategy, requirements, domain |
| `B-###` | discovery | strategy, requirements |
| `O-###` | discovery | operations-evolution |
| `WF-###` | discovery | domain, architecture |
| `PP-###` | discovery | requirements, domain |
| `A-###` | discovery | canon, strategy, requirements, architecture, tasks |
| `H-###` | discovery | strategy, requirements, validation |
| `R-###` | discovery, canon, strategy | requirements, architecture, tasks, validation, release |
| `S-###` | discovery | requirements, validation, release |
| `Q-###` | discovery | any stage until resolved |
| `C-###` | discovery, canon | requirements, architecture |
| `NC-###` | discovery | requirements, tasks |
| `BR-###` | discovery, domain | requirements, domain, architecture, tasks |
| `DM-###` | domain | architecture, tasks, tests |
| `BC-###` | domain | architecture |
| `DE-###` | domain | architecture, tasks |
| `REQ-###` | requirements | domain, architecture, tasks, tests, validation |
| `NFR-###` | requirements | architecture, tests, validation |
| `AC-###` | requirements | tasks, tests, validation |
| `ICP-###` | strategy | requirements, canon |
| `PW-###` | strategy | requirements, canon |
| `CMP-###` | strategy | architecture, requirements |
| `PMF-###` | strategy | validation, release |
| `ADR-####` | architecture | tasks, governance |
| `ARCH-###` | architecture | tasks, tests |
| `TASK-####` | execution-planning | implementation, tests, evidence, validation |
| `TEST-###` | validation | evidence, release |
| `EVID-###` | implementation, validation | tasks, release, governance |
| `GATE-###` | governance-integrity | any stage gate |
| `HANDOFF-###` | any transition | governance |
| `INC-###` | operations-evolution | discovery, canon, requirements, tasks |
| `RCA-###` | operations-evolution | discovery, requirements, tasks |
| `EVOL-###` | operations-evolution | execution-planning, roadmap |
| `DEC-###` | governance-integrity | any stage |
| `MEM-###` | any stage | governance |

## Traceability Chain

A complete traceability chain connects a discovery item all the way through to evidence and release. The canonical chain is:

```text
discovery item (P, U, B, A, H, R, S, BR, Q, C)
  -> canon statement
    -> strategy choice (ICP, PW, CMP, PMF)
      -> requirement (REQ, NFR, AC)
        -> domain concept (DM, BC, DE, BR)
          -> architecture decision (ADR, ARCH)
            -> task (TASK)
              -> test (TEST)
                -> evidence (EVID)
                  -> release or operations record
```

Every link in this chain must be representable as a directed edge in the product graph. The graph should support edges between any two ID families where the downstream artifact declares the upstream ID in its `source_ids`.

## Validation Logic Plan

### Phase 1: ID Format Validation

Check that every ID in the repository matches its expected pattern.

Rules:

- Every ID must match the regex for its prefix family.
- Prefix must be uppercase in storage.
- Suffix must be numeric with the correct zero-padding width.
- No duplicate IDs across the entire repository.

Implementation approach:

- Scan all markdown files in `wiki/` for ID patterns.
- Scan `wiki/graph.json` node IDs and edge endpoints.
- Scan `.echel/evidence_registry.json` artifact keys.
- Scan `.echel/memory_records.jsonl` record IDs.
- Report violations with file path, line number, and the invalid ID.

### Phase 2: Reference Integrity

Check that every referenced ID actually exists as a declared artifact.

Rules:

- Every `source_ids` entry must resolve to an existing artifact.
- Every graph edge `from_id` and `to_id` must resolve to an existing graph node.
- Every evidence link in a task must resolve to a registered evidence artifact.
- Every task must reference at least one upstream ID (requirement, domain concept, or architecture decision).

Implementation approach:

- Build an ID registry by scanning all artifacts.
- For each artifact with `source_ids`, verify every referenced ID is in the registry.
- For each graph edge, verify both endpoints exist as nodes.
- For each task, verify at least one `delivers` or `implements` edge exists.
- Report broken references with source artifact, referenced ID, and suggested remediation.

### Phase 3: Stage Coverage

Check that every lifecycle stage has the expected artifact coverage.

Rules:

- Every required artifact for a stage must exist.
- Every artifact must be assigned to a valid stage.
- Artifacts must not exist in stages they do not belong to without an explicit cross-reference.

Implementation approach:

- Use the lifecycle stage schema to determine required artifacts per stage.
- Scan the repository for expected artifact paths.
- Report missing artifacts as stage blockers.
- Report artifacts in unexpected locations as warnings.

### Phase 4: Chain Completeness

Check that the traceability chain is unbroken from discovery through evidence.

Rules:

- Every requirement must trace back to at least one discovery artifact.
- Every task must trace forward to at least one test or evidence artifact for done tasks.
- Every evidence artifact must trace to a task.
- Broken chains are reported with the specific missing link.

Implementation approach:

- Starting from each requirement, walk backward through `source_ids` to find discovery artifacts.
- Starting from each done task, walk forward through graph edges to find tests and evidence.
- Starting from each evidence artifact, walk backward to find the producing task.
- Report any chain that cannot be traversed.

### Phase 5: Statement Discipline

Check that artifacts properly declare their statement type and confidence.

Rules:

- Every artifact must have a `statement_type`.
- Every artifact must have a `confidence`.
- Assumptions and hypotheses must not be treated as facts in downstream artifacts.
- Low-confidence items that affect scope or architecture must be flagged.

Implementation approach:

- Scan all artifacts for missing `statement_type` or `confidence`.
- For each assumption or hypothesis, check whether downstream artifacts treat it as fact.
- Flag low-confidence items that appear in architecture or release decisions.
- Report violations with the artifact ID and the specific discipline failure.

### Phase 6: Supersession Integrity

Check that superseded artifacts are properly linked.

Rules:

- If an artifact has `supersedes`, the referenced artifact must exist.
- If an artifact has `superseded_by`, the referenced artifact must exist.
- Superseded artifacts must not be the active source for downstream references.
- The active version of an artifact must be the one not marked as superseded.

Implementation approach:

- Build a supersession graph.
- Detect cycles.
- Detect orphaned superseded artifacts.
- Detect downstream references to superseded artifacts.
- Report with the artifact ID and the recommended action.

## Graph Integration

The product graph must support traceability IDs as node identifiers. Graph node IDs should follow the `{type}:{slug}` convention, but the traceability ID must be stored as a node property for lookup.

Extended node shape for traceability:

```json
{
  "id": "requirement:user-authentication",
  "type": "requirement",
  "title": "User authentication",
  "source": "wiki/requirements/functional-requirements.md",
  "summary": "User authentication requirement",
  "trace_id": "REQ-001",
  "statement_type": "decision",
  "confidence": "high",
  "stage": "requirements"
}
```

The graph should support a `trace_id` index for fast lookup by methodology ID. This index enables:

- Forward traversal: given a discovery ID, find all downstream requirements, tasks, tests, and evidence.
- Backward traversal: given an evidence ID, find the producing task, the satisfied requirement, the addressed discovery item, and the originating assumption or risk.
- Impact analysis: given a changed discovery ID, list all downstream artifacts that may need updating.
- Coverage reporting: given a stage, list all artifacts with and without traceability links.

## Matrix Structure

The traceability matrix is a cross-reference table that shows coverage across lifecycle stages. The matrix is generated as `wiki/reports/traceability-matrix.md`.

Matrix columns:

- Discovery items (P, U, B, A, H, R, S, BR, Q, C, NC, WF, PP)
- Canon statements
- Strategy choices (ICP, PW, CMP, PMF)
- Requirements (REQ, NFR, AC)
- Domain concepts (DM, BC, DE)
- Architecture decisions (ADR, ARCH)
- Tasks (TASK)
- Tests (TEST)
- Evidence (EVID)

Matrix rows represent individual artifacts. A cell is filled when the row artifact references the column artifact. Empty cells indicate broken traceability chains.

The matrix report must include:

- Total artifacts per family.
- Artifacts with complete upstream traceability.
- Artifacts with complete downstream traceability.
- Broken chains with specific missing links.
- Coverage percentage per stage.

## Relationship To Other Schemas

- `schema/lifecycle-stage.schema.md` defines the stages where traceability IDs originate and the gate conditions that require traceability coverage.
- `schema/product-graph.schema.md` defines the graph structure where traceability IDs are stored as node properties and traversed as edges.
- `schema/evidence.schema.md` defines the evidence artifact shape that traceability IDs reference.
- `schema/task.schema.md` defines the task artifact shape that includes upstream and downstream traceability links.
- `docs/development/methodology.md` defines the narrative traceability contract that this schema implements.

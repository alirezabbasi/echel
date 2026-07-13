---
type: schema
status: active
---
# Cockpit API Schema

The cockpit API exposes product-owned Echel memory as a stable local product steering surface.

## Snapshot Endpoint
- Route: `GET /api/cockpit`
- Producer: `tools/echel/platform/cockpit.py`

Required top-level keys:
- `project`
- `readiness`
- `clarifications`
- `roadmap`
- `work`
- `graph`
- `architecture`
- `contradictions`
- `agent_activity`
- `risks`
- `decisions`
- `lifecycle`
- `readiness_detail`
- `status_markdown`

## Lifecycle Model

`lifecycle` is the primary cockpit navigation contract. It represents the ordered Echel software-delivery lifecycle instead of artifact tabs.

```json
{
  "current": {
    "id": "discovery",
    "title": "Discovery",
    "status": "blocked",
    "role": "Founder Interviewer",
    "blockers": ["..."],
    "next_action": "...",
    "safe_action": {"label": "Check Discovery", "action": "readiness", "args": {"stage": "discovery"}},
    "safe_actions": [
      {
        "label": "Answer Discovery Field",
        "action": "discover",
        "args": {},
        "description": "Write a discovery answer into the PDS.",
        "fields": [
          {"name": "field", "label": "Field", "type": "text", "required": true},
          {"name": "value", "label": "Answer", "type": "textarea", "required": true}
        ]
      }
    ],
    "artifacts": ["discovery/product-discovery-spec.md"]
  },
  "stages": []
}
```

Required stages:
- `discovery`
- `canon`
- `strategy`
- `requirements`
- `domain`
- `architecture`
- `roadmap`
- `execution`
- `build`
- `validate`
- `release`
- `operate`
- `governance`

Every stage must expose `status`, `role`, `blockers`, `next_action`, `safe_action`, `safe_actions`, and `artifacts` so the UI can always show the current lifecycle state, responsible AI role, blocking conditions, and guided command-backed actions.

Each `safe_actions` entry may include:
- `label`: button or form title.
- `action`: command bridge action name.
- `args`: static arguments supplied by the lifecycle stage.
- `description`: operator-facing action summary.
- `fields`: optional form schema with `name`, `label`, `type`, `required`, `default`, `placeholder`, and `options`.

## Command Endpoint
- Route: `POST /api/cockpit/command`

Request:
```json
{
  "action": "build",
  "args": {}
}
```

Safe actions:
- `clarify`
- `discover`
- `canon`
- `canon-drift`
- `strategy`
- `strategy-readiness`
- `requirements`
- `domain`
- `architecture`
- `execution-tasks`
- `repository-factory`
- `steer`
- `plan`
- `packet`
- `build`
- `review`
- `graph-report`
- `traceability`
- `integrity-audit`
- `validate`
- `evidence-add`
- `learning`
- `learning-add`
- `readiness`
- `proof-pack`
- `release-summary`
- `status`
- `next`

Response:
```json
{
  "ok": true,
  "code": 0,
  "output": "..."
}
```

## Boundary
The cockpit reads and writes product memory through Echel commands and structured helpers. It should not become an independent source of product truth.

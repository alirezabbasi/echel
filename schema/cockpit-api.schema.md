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

Every stage must expose `status`, `role`, `blockers`, `next_action`, `safe_action`, and `artifacts` so the UI can always show the current lifecycle state, responsible AI role, blocking conditions, and next safe action.

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
- `steer`
- `plan`
- `build`
- `review`
- `graph-report`
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

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
- `status_markdown`

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

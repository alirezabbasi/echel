# Evidence OS Specification (v1)

## Artifact Registry

The registry tracks durable non-wiki outputs used to verify work and release claims.

### Supported artifact kinds (v1)

- `test_result`
- `schema_contract`
- `runbook`
- `sql_check`
- `ci_log`
- `slo_snapshot`
- `security_scan`
- `release_note`

### Minimum registry record

- `artifact_id`
- `kind`
- `producer`
- `created_at`
- `subject_ref` (task/story/epic/release)
- `location`
- `checksum` (or equivalent immutability marker)
- `summary`

## Proof Pack

Proof packs bundle closure evidence for a task or release.

### Types

- `task_proof_pack`
- `release_proof_pack`

### Required sections

- `metadata` (id, scope, owner, timestamp)
- `claims` (what is asserted complete)
- `evidence` (artifact references)
- `gate_results` (pass/fail per gate)
- `exceptions` (approved deviations)
- `human_summary` (short narrative)

## Deterministic evidence policy

- Gate evaluation must depend on declared inputs only.
- Missing required artifacts is a hard failure.
- Each gate result must be reproducible from the same registry/proof-pack inputs.

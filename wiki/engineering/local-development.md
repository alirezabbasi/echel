---
type: engineering-guide
stage: repository-factory
status: active
owner: engineering
updated: 2026-07-10
---
# Local Development

## Prerequisites

- Python 3.11 or newer.
- POSIX shell for `scripts/verify.sh`.
- No third-party Python dependencies are required by the current baseline.

## Generate Or Refresh The Baseline

From the Echel repository root:

```bash
python3 tools/echel.py readiness --stage architecture
python3 tools/echel.py execution-tasks
python3 tools/echel.py repository-factory
```

The generator is idempotent. Changes inside `generated/product-repository/` that must survive regeneration also require a matching change to `tools/echel/repository_factory.py`.

## Environment Setup

```bash
cd generated/product-repository
python -m venv .venv
. .venv/bin/activate
python --version
```

There is no dependency installation command because `pyproject.toml` currently declares no runtime dependencies. Creating the virtual environment is the complete setup step.

## Start And Health Check

```bash
python app/main.py
```

Expected output is a JSON object containing `"status": "ok"` and `"service": "generated-product"`.

## Lint And Syntax Check

```bash
python -m compileall -q app tests
```

## Tests

```bash
python -m unittest discover -s tests
```

## Complete Verification

```bash
./scripts/verify.sh
```

The script runs the lint baseline, unit tests, and application health check. CI runs the same three checks.

## Product Memory Verification

After changing `wiki/`, Echel Core, or factory templates, return to the Echel repository root and run:

```bash
python3 -m unittest discover -s tests
make wiki-health
python3 tools/echel.py graph validate
```

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `python` is not found or is older than 3.11 | Install or select Python 3.11+, then recreate `.venv`. |
| `Permission denied` for `verify.sh` | Run `chmod +x scripts/verify.sh`; the factory normally sets this bit. |
| Imports fail when tests run | Run commands from `generated/product-repository/`. |
| Generated edits disappear | Apply the same change to `tools/echel/repository_factory.py`, then regenerate. |
| `.env` changes have no effect | Runtime configuration loading is not implemented in the baseline. |

## Exit Criteria

- `python app/main.py` reports healthy JSON.
- `python -m compileall -q app tests` exits successfully.
- `python -m unittest discover -s tests` passes.
- `./scripts/verify.sh` exits successfully.
- Relevant product memory is synchronized with the implementation.

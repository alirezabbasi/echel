# Local Development

## Setup

```bash
python -m venv .venv
. .venv/bin/activate
```

## Verify

```bash
python -m compileall -q app tests
python -m unittest discover -s tests
python app/main.py
./scripts/verify.sh
```

## Configuration

Copy `.env.example` to `.env` for local-only settings. Do not commit `.env`.

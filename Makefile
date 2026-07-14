.PHONY: test unit scenarios typing lint package-check security verify quality lifecycle

test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v

unit:
	PYTHONPATH=src python3 -m unittest discover -s tests/unit -v

scenarios:
	PYTHONPATH=src python3 -m unittest discover -s tests/integration -v
	PYTHONPATH=src python3 -m unittest discover -s tests/m0 -v

typing:
	python3 -m mypy src/echel

lint:
	python3 -m ruff check src tests

package-check:
	python3 -m build
	python3 -m twine check dist/*

security:
	python3 -m bandit -c pyproject.toml -r src --severity-level medium --confidence-level medium
	python3 -m pip check

verify: test
	PYTHONPATH=src python3 -m compileall -q src tests
	PYTHONPATH=src python3 -m echel.cli.main lifecycle >/dev/null

quality: verify typing lint security

lifecycle:
	PYTHONPATH=src python3 -m echel.cli.main lifecycle

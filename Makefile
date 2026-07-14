.PHONY: test verify lifecycle

test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v

verify: test
	PYTHONPATH=src python3 -m compileall -q src tests
	PYTHONPATH=src python3 -m echel.cli.main lifecycle >/dev/null

lifecycle:
	PYTHONPATH=src python3 -m echel.cli.main lifecycle

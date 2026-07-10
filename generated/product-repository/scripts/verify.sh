#!/usr/bin/env sh
set -eu
python -m compileall -q app tests
python -m unittest discover -s tests
python app/main.py

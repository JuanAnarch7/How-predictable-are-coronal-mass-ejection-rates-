#!/usr/bin/env bash
# Build everything from the raw files and run the tests.
set -euo pipefail
cd "$(dirname "$0")"

# Use $PYTHON if set; otherwise python3 (Debian/Ubuntu ship no plain "python" command).
PY="${PYTHON:-python3}"
"$PY" scripts/build_dataset.py
"$PY" -m unittest discover -s tests

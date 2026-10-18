#!/usr/bin/env bash
# Build everything from the raw files and run the tests.
set -euo pipefail
cd "$(dirname "$0")"

python scripts/build_dataset.py
python -m unittest discover -s tests

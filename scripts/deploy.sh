#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if command -v uv >/dev/null 2>&1; then
  uv run learn init
  uv run --extra test pytest -q
else
  python3 -m venv .venv
  . .venv/bin/activate
  pip install -e ".[test]"
  learn init
  pytest -q
fi


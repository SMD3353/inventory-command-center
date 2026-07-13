#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
trap 'kill 0' EXIT
(cd "$ROOT/backend" && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000) &
(cd "$ROOT/frontend" && npm run dev -- --host 0.0.0.0 --port 5173) &
wait

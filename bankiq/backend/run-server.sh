#!/usr/bin/env bash
# Start Daphne using the project venv.
set -euo pipefail
cd "$(dirname "$0")"
exec .venv/bin/daphne -b 0.0.0.0 -p 8000 config.asgi:application

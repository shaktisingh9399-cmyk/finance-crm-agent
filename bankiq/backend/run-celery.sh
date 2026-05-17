#!/usr/bin/env bash
# Always use the project venv (avoids conda/system celery missing decouple).
set -euo pipefail
cd "$(dirname "$0")"
exec .venv/bin/python -m celery -A config worker -l info "$@"

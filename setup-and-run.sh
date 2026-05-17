#!/usr/bin/env bash
# One-command local setup and run for BankIQ CRM.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$ROOT_DIR/bankiq"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"

RUN_SETUP=1
RUN_SERVERS=1
INSTALL_DEPS=1
START_INFRA=1
PIDS=()

usage() {
  cat <<'EOF'
Usage: ./setup-and-run.sh [options]

Options:
  --setup-only    Create env files, install deps, migrate, seed, then exit
  --run-only      Skip setup and start backend, Celery, and frontend
  --no-install    Skip pip/npm install
  --no-infra      Do not start Postgres/Redis with Docker Compose
  -h, --help      Show this help

Default:
  Runs setup, starts Postgres/Redis via Docker Compose, then starts:
    - Backend API/WebSocket on http://localhost:8000
    - Celery worker
    - Frontend on http://localhost:5173
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --setup-only)
      RUN_SERVERS=0
      ;;
    --run-only)
      RUN_SETUP=0
      ;;
    --no-install)
      INSTALL_DEPS=0
      ;;
    --no-infra)
      START_INFRA=0
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
  shift
done

log() {
  printf '\n==> %s\n' "$1"
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

ensure_env() {
  log "Preparing environment files"
  if [[ ! -f "$APP_DIR/.env" ]]; then
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    echo "Created bankiq/.env from .env.example"
  fi

  if [[ ! -L "$BACKEND_DIR/.env" ]]; then
    rm -f "$BACKEND_DIR/.env"
    ln -s ../.env "$BACKEND_DIR/.env"
    echo "Linked bankiq/backend/.env -> ../.env"
  fi
}

start_infra() {
  if [[ "$START_INFRA" -eq 0 ]]; then
    return
  fi

  require_cmd docker
  log "Starting Postgres and Redis"
  (cd "$APP_DIR" && docker compose up -d postgres redis)
}

setup_backend() {
  require_cmd python3
  log "Setting up backend"
  cd "$BACKEND_DIR"

  if [[ ! -d .venv ]]; then
    python3 -m venv .venv
  fi

  if [[ "$INSTALL_DEPS" -eq 1 ]]; then
    .venv/bin/python -m pip install --upgrade pip
    .venv/bin/python -m pip install -r requirements.txt
  fi

  .venv/bin/python manage.py migrate
  .venv/bin/python manage.py seed_demo
}

setup_frontend() {
  require_cmd npm
  log "Setting up frontend"
  cd "$FRONTEND_DIR"

  if [[ "$INSTALL_DEPS" -eq 1 ]]; then
    npm install
  fi
}

cleanup() {
  if [[ ${#PIDS[@]} -gt 0 ]]; then
    log "Stopping app processes"
    for pid in "${PIDS[@]}"; do
      kill "$pid" >/dev/null 2>&1 || true
    done
    wait >/dev/null 2>&1 || true
  fi
}

run_apps() {
  log "Starting app processes"
  PIDS=()
  trap cleanup EXIT
  trap 'cleanup; exit 130' INT
  trap 'cleanup; exit 143' TERM

  (cd "$BACKEND_DIR" && ./run-server.sh) &
  PIDS+=("$!")

  (cd "$BACKEND_DIR" && ./run-celery.sh) &
  PIDS+=("$!")

  (cd "$FRONTEND_DIR" && npm run dev -- --host 0.0.0.0) &
  PIDS+=("$!")

  cat <<'EOF'

BankIQ is starting:
  API docs:  http://localhost:8000/api/v1/docs/
  Frontend:  http://localhost:5173
  Login:     rm_demo / demo1234

Press Ctrl+C to stop backend, Celery, and frontend.
EOF

  wait
}

main() {
  if [[ "$RUN_SETUP" -eq 1 ]]; then
    ensure_env
    start_infra
    setup_backend
    setup_frontend
  elif [[ "$START_INFRA" -eq 1 ]]; then
    start_infra
  fi

  if [[ "$RUN_SERVERS" -eq 1 ]]; then
    run_apps
  fi
}

main

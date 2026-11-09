#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
action="${1:-start}"
case "$action" in
  start|stop|down|logs|status|config|build) ;;
  *) echo 'Usage: bash scripts/server.sh [start|stop|down|logs|status|config|build]' >&2; exit 2 ;;
esac
command -v docker >/dev/null || { echo 'Enable Docker Desktop WSL integration for this Ubuntu.' >&2; exit 1; }
docker compose version >/dev/null
case "$action" in
  start) docker compose up -d --build; echo 'Follow startup with: bash scripts/server.sh logs' ;;
  build) docker compose build ;;
  stop) docker compose stop ;;
  down) docker compose down ;;
  logs) docker compose logs -f --tail=80 tts ;;
  status) docker compose ps -a ;;
  config) docker compose config ;;
esac

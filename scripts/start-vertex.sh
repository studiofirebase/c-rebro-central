#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -d ".venv" ]]; then
  source .venv/bin/activate
fi

export LLM_PROVIDER="${LLM_PROVIDER:-vertex}"
export VERTEX_AUTH_MODE="${VERTEX_AUTH_MODE:-auto}"
export VERTEX_LOCATION="${VERTEX_LOCATION:-us-central1}"
export VERTEX_MODEL="${VERTEX_MODEL:-gemini-1.5-flash}"

if [[ -z "${VERTEX_PROJECT_ID:-}" && -n "${GOOGLE_CLOUD_PROJECT:-}" ]]; then
  export VERTEX_PROJECT_ID="$GOOGLE_CLOUD_PROJECT"
fi

if [[ -z "${VERTEX_PROJECT_ID:-}" ]]; then
  echo "[erro] Defina VERTEX_PROJECT_ID ou GOOGLE_CLOUD_PROJECT"
  exit 1
fi

if [[ "${VERTEX_AUTH_MODE}" == "gcloud" || "${VERTEX_AUTH_MODE}" == "auto" ]]; then
  if command -v gcloud >/dev/null 2>&1; then
    export VERTEX_ACCESS_TOKEN="$(gcloud auth application-default print-access-token 2>/dev/null || true)"
  fi
fi

echo "[ok] Provider: $LLM_PROVIDER"
echo "[ok] Projeto: $VERTEX_PROJECT_ID"
echo "[ok] Modelo: $VERTEX_MODEL"

./cerebro central

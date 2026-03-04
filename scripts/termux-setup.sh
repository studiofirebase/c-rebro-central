#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

pkg update -y
pkg upgrade -y
pkg install -y python git curl

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-termux.txt

echo ""
echo "[ok] Ambiente Termux preparado"
echo "Próximo passo:"
echo "  export LLM_PROVIDER=vertex"
echo "  export VERTEX_AUTH_MODE=env"
echo "  export VERTEX_PROJECT_ID=seu-projeto"
echo "  export VERTEX_LOCATION=us-central1"
echo "  export VERTEX_MODEL=gemini-1.5-flash"
echo "  export VERTEX_ACCESS_TOKEN=seu-token"
echo "  ./scripts/start-vertex.sh"

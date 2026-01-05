#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$PROJECT_ROOT"
source venv/bin/activate

echo ""
echo "🚀 Iniciando serviços Saúdelog..."
echo ""

PIDS=()

if command -v ollama &> /dev/null; then
    echo "  [1/3] Iniciando Ollama..."
    ollama serve > /dev/null 2>&1 &
    PIDS+=($!)
    sleep 2
else
    echo "  [1/3] Ollama não instalado"
fi

echo "  [2/3] Iniciando API..."
mkdir -p logs
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
PIDS+=($!)
sleep 3

echo "  [3/3] Iniciando Dashboard..."
streamlit run src/web/app.py --server.port 8501 --server.address 0.0.0.0 > logs/web.log 2>&1 &
PIDS+=($!)

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              ✅ SERVIÇOS INICIADOS                          ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  🔹 API:        http://localhost:8000                        ║"
echo "║  🔹 Swagger:    http://localhost:8000/docs                   ║"
echo "║  🔹 Dashboard:  http://localhost:8501                        ║"
echo "║  🔹 Ollama:     http://localhost:11434                       ║"
echo "║                                                              ║"
echo "║  Pressione Ctrl+C para encerrar                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"

cleanup() {
    echo -e "\nEncerrando..."
    for pid in "${PIDS[@]}"; do kill "$pid" 2>/dev/null; done
    pkill -x "ollama" 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM
wait

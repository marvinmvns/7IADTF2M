#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$PROJECT_ROOT"
source venv/bin/activate

echo ""
echo "🚀 Iniciando todos os serviços Saúdelog..."
echo ""

# Array para PIDs
PIDS=()

# Iniciar Ollama (se disponível)
if command -v ollama &> /dev/null; then
    echo "  [1/3] Iniciando Ollama..."
    ollama serve > /dev/null 2>&1 &
    PIDS+=($!)
    sleep 2
else
    echo "  [1/3] Ollama não instalado (opcional)"
fi

# Iniciar API
echo "  [2/3] Iniciando API FastAPI..."
mkdir -p logs
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
PIDS+=($!)
sleep 3

# Iniciar Web
echo "  [3/3] Iniciando Streamlit Dashboard..."
streamlit run src/web/app.py --server.port 8501 --server.address 0.0.0.0 > logs/web.log 2>&1 &
PIDS+=($!)

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              ✅ SERVIÇOS INICIADOS COM SUCESSO              ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║                                                              ║"
echo "║  🔹 API FastAPI:    http://localhost:8000                    ║"
echo "║  🔹 Swagger Docs:   http://localhost:8000/docs               ║"
echo "║  🔹 Dashboard Web:  http://localhost:8501                    ║"
echo "║  🔹 Ollama LLM:     http://localhost:11434                   ║"
echo "║                                                              ║"
echo "║  Logs em: logs/api.log e logs/web.log                        ║"
echo "║                                                              ║"
echo "║  Pressione Ctrl+C para encerrar todos os serviços            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Função para encerrar processos
cleanup() {
    echo ""
    echo "Encerrando serviços..."
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null
    done
    pkill -f "ollama serve" 2>/dev/null
    pkill -x "ollama" 2>/dev/null
    echo "Serviços encerrados."
    exit 0
}

trap cleanup SIGINT SIGTERM

# Aguardar
wait

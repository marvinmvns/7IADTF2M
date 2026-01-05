#!/bin/bash
echo "Encerrando serviços Saúdelog..."
echo ""

# ============================================================================
# Parar processos nativos (instalação local)
# ============================================================================

# Encerrar API (uvicorn)
if pgrep -f "uvicorn src.api.main:app" > /dev/null 2>&1; then
    pkill -f "uvicorn src.api.main:app" 2>/dev/null
    echo "  ✔ API (uvicorn) encerrada"
else
    echo "  - API (uvicorn) não estava rodando"
fi

# Encerrar Streamlit
if pgrep -f "streamlit run" > /dev/null 2>&1; then
    pkill -f "streamlit run" 2>/dev/null
    echo "  ✔ Streamlit encerrado"
else
    echo "  - Streamlit não estava rodando"
fi

# Encerrar Ollama (múltiplas formas para garantir)
OLLAMA_KILLED=0
if pgrep -x "ollama" > /dev/null 2>&1; then
    pkill -x "ollama" 2>/dev/null
    OLLAMA_KILLED=1
fi
if pgrep -f "ollama serve" > /dev/null 2>&1; then
    pkill -f "ollama serve" 2>/dev/null
    OLLAMA_KILLED=1
fi
if pgrep -f "Ollama" > /dev/null 2>&1; then
    pkill -f "Ollama" 2>/dev/null
    OLLAMA_KILLED=1
fi

if [ $OLLAMA_KILLED -eq 1 ]; then
    echo "  ✔ Ollama encerrado"
else
    echo "  - Ollama não estava rodando"
fi

# ============================================================================
# Parar containers Docker (se existirem)
# ============================================================================

if command -v docker &> /dev/null; then
    DOCKER_CONTAINERS=$(docker ps -q --filter "name=ga-vrp" 2>/dev/null)
    
    if [ -n "$DOCKER_CONTAINERS" ]; then
        echo ""
        echo "  Parando containers Docker..."
        docker stop $DOCKER_CONTAINERS 2>/dev/null
        echo "  ✔ Containers Docker parados"
    fi
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
    
    if [ -f "$PROJECT_ROOT/docker-compose.yml" ] || [ -f "$PROJECT_ROOT/docker-compose.yaml" ]; then
        if command -v docker-compose &> /dev/null; then
            cd "$PROJECT_ROOT"
            docker-compose down 2>/dev/null && echo "  ✔ docker-compose down executado"
        elif docker compose version &> /dev/null 2>&1; then
            cd "$PROJECT_ROOT"
            docker compose down 2>/dev/null && echo "  ✔ docker compose down executado"
        fi
    fi
fi

# ============================================================================
# Verificar portas ainda em uso
# ============================================================================

echo ""
echo "  Verificando portas..."

kill_port() {
    local PORT=$1
    local NAME=$2
    local PID=$(lsof -ti:$PORT 2>/dev/null)
    if [ -n "$PID" ]; then
        kill -9 $PID 2>/dev/null
        echo "  ✔ Processo na porta $PORT ($NAME) forçado a encerrar"
        return 0
    fi
    return 1
}

PORTS_IN_USE=0
for PORT in 8000 8501 11434; do
    if lsof -i:$PORT > /dev/null 2>&1; then
        case $PORT in
            8000) NAME="API" ;;
            8501) NAME="Streamlit" ;;
            11434) NAME="Ollama" ;;
        esac
        echo "  ⚠ Porta $PORT ($NAME) ainda em uso"
        PORTS_IN_USE=1
    fi
done

if [ $PORTS_IN_USE -eq 1 ]; then
    echo ""
    read -p "  Forçar encerramento? [S/n]: " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Ss]$ ]] || [[ -z $REPLY ]]; then
        kill_port 8000 "API"
        kill_port 8501 "Streamlit"
        kill_port 11434 "Ollama"
    fi
fi

echo ""
echo "Todos os serviços foram encerrados."

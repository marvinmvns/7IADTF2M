#!/bin/bash
echo "Encerrando serviços Saúdelog..."
echo ""

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

# Encerrar Ollama - AGRESSIVAMENTE
OLLAMA_KILLED=0

# 1. Parar serviço systemd (se existir e estiver ativo)
if systemctl is-active --quiet ollama 2>/dev/null; then
    echo "  ⚠ Ollama rodando como serviço systemd, parando..."
    sudo systemctl stop ollama 2>/dev/null && OLLAMA_KILLED=1
fi

# 2. Matar todos os processos ollama
for pattern in "ollama serve" "ollama runner"; do
    if pgrep -f "$pattern" > /dev/null 2>&1; then
        pkill -9 -f "$pattern" 2>/dev/null
        OLLAMA_KILLED=1
    fi
done

# 3. Matar por nome exato
if pgrep -x "ollama" > /dev/null 2>&1; then
    pkill -9 -x "ollama" 2>/dev/null
    OLLAMA_KILLED=1
fi

if [ $OLLAMA_KILLED -eq 1 ]; then
    echo "  ✔ Ollama encerrado"
else
    echo "  - Ollama não estava rodando"
fi

# Parar containers Docker
if command -v docker &> /dev/null; then
    DOCKER_CONTAINERS=$(docker ps -q --filter "name=ga-vrp" 2>/dev/null)
    if [ -n "$DOCKER_CONTAINERS" ]; then
        echo ""
        echo "  Parando containers Docker..."
        docker stop $DOCKER_CONTAINERS 2>/dev/null
        echo "  ✔ Containers Docker parados"
    fi
fi

# Forçar liberação de portas
echo ""
echo "  Liberando portas..."
for PORT in 8000 8501 11434; do
    if ss -tlnp 2>/dev/null | grep -q ":$PORT "; then
        fuser -k $PORT/tcp 2>/dev/null && echo "  ✔ Porta $PORT liberada"
    fi
done

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✅ Todos os serviços foram encerrados."
echo "═══════════════════════════════════════════════════════════"

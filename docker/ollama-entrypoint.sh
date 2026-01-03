#!/bin/bash
# Entrypoint script para Ollama com Gemma3

set -e

echo "🤖 Starting Ollama server..."

# Inicia servidor Ollama em background
ollama serve &
OLLAMA_PID=$!

# Aguarda servidor estar pronto
echo "⏳ Waiting for Ollama server to be ready..."
sleep 5

# Verifica se o modelo já está baixado
if ollama list | grep -q "gemma3:latest"; then
    echo "✅ Gemma3 model already downloaded"
else
    echo "📥 Downloading Gemma3 model (this may take a while)..."
    ollama pull gemma3:latest || ollama pull llama3.2:latest # Fallback se gemma3 não existir
    echo "✅ Model downloaded successfully"
fi

echo "🎉 Ollama server ready"
echo "📍 Endpoint: http://0.0.0.0:11434"

# Mantém processo em foreground
wait $OLLAMA_PID

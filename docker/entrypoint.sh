#!/bin/bash
# Entrypoint script para aplicação principal

set -e

echo "🚀 Starting GA VRP Optimization Application..."

# Verifica se o banco de dados existe, senão cria
if [ ! -f "/app/data/experiments.db" ]; then
    echo "📊 Initializing database..."
    python -c "from src.database.database import init_db; init_db()"
fi

# Decide qual serviço iniciar baseado na variável de ambiente
case "$SERVICE_TYPE" in
    "api")
        echo "🌐 Starting FastAPI server on port 8000..."
        exec uvicorn src.api.main:app --host 0.0.0.0 --port 8000
        ;;
    "web")
        echo "🖥️  Starting Streamlit web interface on port 8501..."
        exec streamlit run src/web/app.py --server.port 8501 --server.address 0.0.0.0
        ;;
    "all")
        echo "🔄 Starting both API and Web interface..."
        # Inicia API em background
        uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &
        # Inicia Streamlit em foreground
        exec streamlit run src/web/app.py --server.port 8501 --server.address 0.0.0.0
        ;;
    *)
        echo "❌ Invalid SERVICE_TYPE: $SERVICE_TYPE"
        echo "   Valid options: api, web, all"
        exit 1
        ;;
esac

@echo off
cd /d "%~dp0..\.."
call venv\Scripts\activate.bat

echo.
echo ========================================
echo   Iniciando Servicos Saudelog
echo ========================================
echo.

REM Iniciar Ollama
echo [1/3] Iniciando Ollama...
start "Ollama" cmd /c "ollama serve"
timeout /t 2 /nobreak > nul

REM Iniciar API
echo [2/3] Iniciando API...
start "API FastAPI" cmd /c "call venv\Scripts\activate.bat && uvicorn src.api.main:app --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak > nul

REM Iniciar Web
echo [3/3] Iniciando Dashboard...
start "Streamlit" cmd /c "call venv\Scripts\activate.bat && streamlit run src/web/app.py --server.port 8501 --server.address 0.0.0.0"

echo.
echo ========================================
echo   Servicos iniciados em janelas separadas
echo ========================================
echo.
echo   API:       http://localhost:8000
echo   Swagger:   http://localhost:8000/docs
echo   Dashboard: http://localhost:8501
echo   Ollama:    http://localhost:11434
echo.
echo   Feche as janelas para encerrar os servicos
echo.
pause

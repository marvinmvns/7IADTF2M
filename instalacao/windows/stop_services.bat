@echo off
echo Encerrando servicos Saudelog...
echo.

REM Encerrar por nome de processo
taskkill /f /im ollama.exe 2>nul && echo   [OK] Ollama encerrado

REM Encerrar janelas por titulo
taskkill /f /fi "WINDOWTITLE eq API FastAPI" 2>nul && echo   [OK] API encerrada
taskkill /f /fi "WINDOWTITLE eq Streamlit" 2>nul && echo   [OK] Streamlit encerrado
taskkill /f /fi "WINDOWTITLE eq Ollama" 2>nul

REM Fallback: encerrar processos Python que estejam usando as portas
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000"') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8501"') do taskkill /f /pid %%a 2>nul

echo.
echo Servicos encerrados.
pause

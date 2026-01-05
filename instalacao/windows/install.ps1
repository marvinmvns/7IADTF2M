#Requires -Version 5.1
<#
.SYNOPSIS
    Saúdelog - Script de Instalação para Windows
    Projeto: Otimização de Rotas VRP com Algoritmos Genéticos
    FIAP Tech Challenge - Fase 2

.DESCRIPTION
    Este script instala e configura todas as dependências necessárias
    para executar o projeto Saúdelog no Windows.

.NOTES
    Execute como Administrador para melhor compatibilidade.
#>

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Diretórios (dois níveis acima de instalacao/windows/)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$InstalacaoDir = Split-Path -Parent $ScriptDir
$ProjectRoot = Split-Path -Parent $InstalacaoDir

# Funções de Output
function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host ("=" * 65) -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor Cyan
    Write-Host ("=" * 65) -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success { param([string]$Message) Write-Host "  [OK] $Message" -ForegroundColor Green }
function Write-Warning { param([string]$Message) Write-Host "  [!] $Message" -ForegroundColor Yellow }
function Write-Error { param([string]$Message) Write-Host "  [X] $Message" -ForegroundColor Red }
function Write-Info { param([string]$Message) Write-Host "  [i] $Message" -ForegroundColor Cyan }

# Banner
Clear-Host
Write-Host @"

   ____              __      _      _
  / ___|  __ _ _   _/ _| ___| | ___| | ___   __ _
  \___ \ / _` | | | | |_ / _ \ |/ _ \ |/ _ \ / _` |
   ___) | (_| | |_| |  _|  __/ |  __/ | (_) | (_| |
  |____/ \__,_|\__,_|_|  \___|_|\___|_|\___/ \__, |
                                              |___/
  ============================================================
  Instalacao Local - Windows - VRP Optimizer
  FIAP Tech Challenge - Fase 2
  ============================================================

"@ -ForegroundColor Green

Start-Sleep -Seconds 1

# ============================================================================
# 1. Verificar Privilégios
# ============================================================================

Write-Header "1/8 - Verificando Sistema"

$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if ($isAdmin) {
    Write-Success "Executando como Administrador"
} else {
    Write-Warning "Executando sem privilegios de Administrador"
}

Write-Success "Sistema: Windows $([System.Environment]::OSVersion.Version)"
Write-Success "PowerShell: $($PSVersionTable.PSVersion)"

# ============================================================================
# 2. Verificar/Instalar Python
# ============================================================================

Write-Header "2/8 - Verificando Python 3.9+"

$PythonCmd = $null
$PythonPaths = @("python", "python3", "py -3")

foreach ($cmd in $PythonPaths) {
    try {
        $version = & $cmd.Split()[0] $cmd.Split()[1..99] -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
        if ($version) {
            $major, $minor = $version.Split('.')
            if ([int]$major -eq 3 -and [int]$minor -ge 9) {
                $PythonCmd = $cmd
                Write-Success "Python encontrado: $cmd (versao $version)"
                break
            }
        }
    } catch { continue }
}

if (-not $PythonCmd) {
    Write-Warning "Python 3.9+ nao encontrado!"
    Write-Info "Instalando via winget..."
    try {
        winget install Python.Python.3.11 --accept-package-agreements --accept-source-agreements
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        $PythonCmd = "python"
        Write-Success "Python instalado"
    } catch {
        Write-Error "Falha ao instalar Python"
        Write-Info "Instale manualmente: https://www.python.org/downloads/"
        Read-Host "Pressione Enter para sair"
        exit 1
    }
}

# ============================================================================
# 3. Chocolatey
# ============================================================================

Write-Header "3/8 - Gerenciador de Pacotes"

$hasChoco = Get-Command choco -ErrorAction SilentlyContinue

if ($hasChoco) {
    Write-Success "Chocolatey instalado"
} else {
    $response = Read-Host "  Instalar Chocolatey? [S/n]"
    if ($response -eq "" -or $response -match "^[Ss]") {
        if ($isAdmin) {
            Set-ExecutionPolicy Bypass -Scope Process -Force
            [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
            Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
            Write-Success "Chocolatey instalado"
        } else {
            Write-Warning "Requer privilegios de Administrador"
        }
    }
}

# ============================================================================
# 4. Ollama
# ============================================================================

Write-Header "4/8 - Ollama (LLM Local)"

$hasOllama = Get-Command ollama -ErrorAction SilentlyContinue

if ($hasOllama) {
    Write-Success "Ollama ja instalado"
} else {
    $response = Read-Host "  Instalar Ollama? [S/n]"
    if ($response -eq "" -or $response -match "^[Ss]") {
        try {
            winget install Ollama.Ollama --accept-package-agreements --accept-source-agreements
            Write-Success "Ollama instalado"
            
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            
            $response = Read-Host "  Baixar modelo gemma3:4b (~2.5GB)? [S/n]"
            if ($response -eq "" -or $response -match "^[Ss]") {
                ollama pull gemma3:4b
            }
        } catch {
            Write-Warning "Instale Ollama manualmente: https://ollama.com"
        }
    }
}

# ============================================================================
# 5. Ambiente Virtual
# ============================================================================

Write-Header "5/8 - Ambiente Virtual Python"

Set-Location $ProjectRoot
$VenvDir = Join-Path $ProjectRoot "venv"

if (Test-Path $VenvDir) {
    Write-Info "Ambiente virtual ja existe"
    $response = Read-Host "  Recriar? [s/N]"
    if ($response -match "^[Ss]") {
        Remove-Item -Recurse -Force $VenvDir
        & $PythonCmd.Split()[0] $PythonCmd.Split()[1..99] -m venv $VenvDir
        Write-Success "Ambiente virtual recriado"
    }
} else {
    & $PythonCmd.Split()[0] $PythonCmd.Split()[1..99] -m venv $VenvDir
    Write-Success "Ambiente virtual criado"
}

$ActivateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
. $ActivateScript
Write-Success "Ambiente virtual ativado"

# ============================================================================
# 6. Dependências Python
# ============================================================================

Write-Header "6/8 - Dependencias Python"

python -m pip install --upgrade pip setuptools wheel --quiet
pip install -r (Join-Path $ProjectRoot "requirements.txt")
pip install pytz httpx aiofiles --quiet 2>$null

Write-Success "Dependencias instaladas"

# ============================================================================
# 7. Estrutura
# ============================================================================

Write-Header "7/8 - Estrutura do Projeto"

$directories = @("data", "assets", "logs", "output")
foreach ($dir in $directories) {
    $path = Join-Path $ProjectRoot $dir
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }
}
Write-Success "Diretorios criados"

$dbPath = Join-Path $ProjectRoot "data\experiments.db"
if (Test-Path $dbPath) {
    Write-Success "Banco de dados existente preservado"
}

# ============================================================================
# Criar Scripts de Execução
# ============================================================================

# start_services.bat
@"
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
"@ | Set-Content (Join-Path $ScriptDir "start_services.bat") -Encoding ASCII

# stop_services.bat
@"
@echo off
echo Encerrando servicos Saudelog...
echo.

taskkill /f /im python.exe /fi "WINDOWTITLE eq API*" 2>nul && echo   [OK] API encerrada
taskkill /f /im python.exe /fi "WINDOWTITLE eq Streamlit*" 2>nul && echo   [OK] Streamlit encerrado
taskkill /f /im ollama.exe 2>nul && echo   [OK] Ollama encerrado

REM Fallback mais agressivo
taskkill /f /fi "WINDOWTITLE eq API FastAPI" 2>nul
taskkill /f /fi "WINDOWTITLE eq Streamlit" 2>nul
taskkill /f /fi "WINDOWTITLE eq Ollama" 2>nul

echo.
echo Servicos encerrados.
pause
"@ | Set-Content (Join-Path $ScriptDir "stop_services.bat") -Encoding ASCII

# start_api.bat
@"
@echo off
cd /d "%~dp0..\.."
call venv\Scripts\activate.bat
echo.
echo [API] Iniciando FastAPI em http://localhost:8000
echo [API] Documentacao: http://localhost:8000/docs
echo.
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
"@ | Set-Content (Join-Path $ScriptDir "start_api.bat") -Encoding ASCII

# start_web.bat
@"
@echo off
cd /d "%~dp0..\.."
call venv\Scripts\activate.bat
echo.
echo [WEB] Iniciando Streamlit em http://localhost:8501
echo.
streamlit run src/web/app.py --server.port 8501 --server.address 0.0.0.0
"@ | Set-Content (Join-Path $ScriptDir "start_web.bat") -Encoding ASCII

# start_ollama.bat
@"
@echo off
echo.
echo [LLM] Iniciando Ollama em http://localhost:11434
echo.
ollama serve
"@ | Set-Content (Join-Path $ScriptDir "start_ollama.bat") -Encoding ASCII

# run_tests.bat
@"
@echo off
cd /d "%~dp0..\.."
call venv\Scripts\activate.bat
echo.
echo [TEST] Executando testes...
echo.
pytest tests/ -v --tb=short
pause
"@ | Set-Content (Join-Path $ScriptDir "run_tests.bat") -Encoding ASCII

Write-Success "Scripts criados em instalacao\windows\"

# ============================================================================
# 8. Validação
# ============================================================================

Write-Header "8/8 - Validacao Final"

$validationScript = @"
import sys
modules = [('numpy','numpy'),('pandas','pandas'),('fastapi','fastapi'),('streamlit','streamlit'),('pydantic','pydantic')]
failed = []
for name, mod in modules:
    try:
        __import__(mod)
        print(f'    [OK] {name}')
    except:
        print(f'    [X] {name}')
        failed.append(name)
sys.exit(len(failed))
"@

python -c $validationScript

if ($LASTEXITCODE -eq 0) {
    Write-Success "Validacoes passaram!"
} else {
    Write-Warning "Algumas validacoes falharam"
}

# ============================================================================
# Conclusão
# ============================================================================

Write-Host ""
Write-Host @"
+==================================================================+
|                                                                  |
|          INSTALACAO CONCLUIDA COM SUCESSO!                       |
|                                                                  |
+==================================================================+
"@ -ForegroundColor Green

Write-Host @"

  COMO USAR:

  1. Iniciar TODOS os servicos:
     .\instalacao\windows\start_services.bat

  2. Ou iniciar separadamente:
     .\instalacao\windows\start_api.bat
     .\instalacao\windows\start_web.bat
     .\instalacao\windows\start_ollama.bat

  3. Parar todos os servicos:
     .\instalacao\windows\stop_services.bat

  URLs:
     Dashboard:  http://localhost:8501
     API:        http://localhost:8000
     Swagger:    http://localhost:8000/docs
     Ollama:     http://localhost:11434

"@ -ForegroundColor White

Read-Host "Pressione Enter para finalizar"

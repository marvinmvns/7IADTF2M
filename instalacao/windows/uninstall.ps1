#Requires -Version 5.1
<#
.SYNOPSIS
    Saúdelog - Script de Desinstalação para Windows
    Remove apenas: ambiente virtual (venv) e Ollama
    NÃO remove: código fonte, banco de dados, logs ou scripts
#>

$ErrorActionPreference = "Continue"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$InstalacaoDir = Split-Path -Parent $ScriptDir
$ProjectRoot = Split-Path -Parent $InstalacaoDir

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host ("=" * 65) -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor Cyan
    Write-Host ("=" * 65) -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success { param([string]$Message) Write-Host "  [OK] $Message" -ForegroundColor Green }
function Write-Info { param([string]$Message) Write-Host "  [i] $Message" -ForegroundColor Cyan }

Clear-Host
Write-Host @"

   ____              __      _      _
  / ___|  __ _ _   _/ _| ___| | ___| | ___   __ _
  \___ \ / _` | | | | |_ / _ \ |/ _ \ |/ _ \ / _` |
   ___) | (_| | |_| |  _|  __/ |  __/ | (_) | (_| |
  |____/ \__,_|\__,_|_|  \___|_|\___|_|\___/ \__, |
                                              |___/
  ============================================================
  Desinstalacao - Windows - VRP Optimizer
  ============================================================

"@ -ForegroundColor Red

Write-Host "  Este script remove apenas:" -ForegroundColor Yellow
Write-Host "    - Ambiente virtual Python (venv)"
Write-Host "    - Ollama (se instalado)"
Write-Host ""
Write-Host "  NAO serao removidos:" -ForegroundColor Green
Write-Host "    - Codigo fonte do projeto"
Write-Host "    - Banco de dados (experiments.db)"
Write-Host "    - Logs e arquivos de saida"
Write-Host "    - Scripts de instalacao"
Write-Host ""

# 1. Parar Serviços
Write-Header "1/3 - Parando Servicos"

$processes = @("uvicorn", "streamlit", "ollama")
foreach ($proc in $processes) {
    $running = Get-Process -Name $proc -ErrorAction SilentlyContinue
    if ($running) {
        Stop-Process -Name $proc -Force -ErrorAction SilentlyContinue
        Write-Success "$proc encerrado"
    } else {
        Write-Info "$proc nao estava rodando"
    }
}

# 2. Ambiente Virtual
Write-Header "2/3 - Ambiente Virtual"

$VenvDir = Join-Path $ProjectRoot "venv"
if (Test-Path $VenvDir) {
    $venvSize = [math]::Round((Get-ChildItem $VenvDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
    $response = Read-Host "  Remover ambiente virtual ($venvSize MB)? [S/n]"
    if ($response -eq "" -or $response -match "^[Ss]") {
        Remove-Item -Recurse -Force $VenvDir
        Write-Success "Ambiente virtual removido"
    } else {
        Write-Info "Ambiente virtual mantido"
    }
} else {
    Write-Info "Ambiente virtual nao encontrado"
}

# 3. Ollama
Write-Header "3/3 - Ollama"

if (Get-Command ollama -ErrorAction SilentlyContinue) {
    $response = Read-Host "  Desinstalar Ollama e modelos? [s/N]"
    if ($response -match "^[Ss]") {
        try {
            winget uninstall Ollama.Ollama --silent 2>$null
            Write-Success "Ollama desinstalado"
        } catch {
            Write-Info "Desinstale Ollama manualmente via Configuracoes > Apps"
        }
        
        $ollamaData = "$env:USERPROFILE\.ollama"
        if (Test-Path $ollamaData) {
            Remove-Item -Recurse -Force $ollamaData -ErrorAction SilentlyContinue
            Write-Success "Dados do Ollama removidos"
        }
    } else {
        Write-Info "Ollama mantido"
    }
} else {
    Write-Info "Ollama nao estava instalado"
}

Write-Host ""
Write-Host @"
+==================================================================+
|           DESINSTALACAO CONCLUIDA!                               |
+==================================================================+
"@ -ForegroundColor Green

Write-Host ""
Write-Host "  Para remover manualmente:" -ForegroundColor Cyan
Write-Host "    - Banco de dados: Remove-Item `"$ProjectRoot\data\experiments.db`"" -ForegroundColor Yellow
Write-Host "    - Logs:           Remove-Item -Recurse `"$ProjectRoot\logs`"" -ForegroundColor Yellow
Write-Host "    - Todo o projeto: Remove-Item -Recurse `"$ProjectRoot`"" -ForegroundColor Yellow
Write-Host ""

Read-Host "Pressione Enter para finalizar"

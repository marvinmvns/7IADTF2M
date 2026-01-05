#!/bin/bash

#===============================================================================
# Saúdelog - Script de Instalação para macOS
# Projeto: Otimização de Rotas VRP com Algoritmos Genéticos
# FIAP Tech Challenge - Fase 2
#===============================================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Diretório raiz do projeto (dois níveis acima de instalacao/macos/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALACAO_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$INSTALACAO_DIR")"

#===============================================================================
# Funções auxiliares
#===============================================================================

print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}\n"
}

print_success() { echo -e "${GREEN}  ✔ $1${NC}"; }
print_warning() { echo -e "${YELLOW}  ⚠ $1${NC}"; }
print_error() { echo -e "${RED}  ✖ $1${NC}"; }
print_info() { echo -e "${CYAN}  ℹ $1${NC}"; }

check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

#===============================================================================
# Banner
#===============================================================================

clear
echo -e "${GREEN}"
cat << "EOF"
   ____              __      _      _
  / ___|  __ _ _   _/ _| ___| | ___| | ___   __ _
  \___ \ / _` | | | | |_ / _ \ |/ _ \ |/ _ \ / _` |
   ___) | (_| | |_| |  _|  __/ |  __/ | (_) | (_| |
  |____/ \__,_|\__,_|_|  \___|_|\___|_|\___/ \__, |
                                              |___/
  ══════════════════════════════════════════════════
  Instalação Local - macOS - VRP Optimizer
  FIAP Tech Challenge - Fase 2
  ══════════════════════════════════════════════════
EOF
echo -e "${NC}"

sleep 1

#===============================================================================
# 1. Detectar Sistema e Arquitetura
#===============================================================================

print_header "1/8 - Detectando Sistema"

if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "Este script é exclusivo para macOS!"
    print_info "Para Linux, use: instalacao/linux/install.sh"
    print_info "Para Windows, use: instalacao/windows/install.ps1"
    exit 1
fi

# Detectar arquitetura (Intel vs Apple Silicon)
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    print_success "Sistema: macOS (Apple Silicon - $ARCH)"
    HOMEBREW_PREFIX="/opt/homebrew"
else
    print_success "Sistema: macOS (Intel - $ARCH)"
    HOMEBREW_PREFIX="/usr/local"
fi

MACOS_VERSION=$(sw_vers -productVersion)
print_success "Versão: macOS $MACOS_VERSION"

#===============================================================================
# 2. Verificar/Instalar Homebrew
#===============================================================================

print_header "2/8 - Verificando Homebrew"

if check_command brew; then
    BREW_VERSION=$(brew --version | head -1)
    print_success "Homebrew já instalado: $BREW_VERSION"
else
    echo ""
    echo "  Homebrew é o gerenciador de pacotes recomendado para macOS."
    echo ""
    read -p "  Instalar Homebrew? [S/n]: " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Ss]$ ]] || [[ -z $REPLY ]]; then
        print_info "Instalando Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        if [[ "$ARCH" == "arm64" ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        else
            eval "$(/usr/local/bin/brew shellenv)"
        fi
        
        print_success "Homebrew instalado com sucesso"
    else
        print_error "Homebrew é necessário para continuar."
        exit 1
    fi
fi

#===============================================================================
# 3. Verificar/Instalar Python
#===============================================================================

print_header "3/8 - Verificando Python 3.9+"

PYTHON_CMD=""

for cmd in python3.11 python3.10 python3.9 python3; do
    if check_command "$cmd"; then
        version=$($cmd -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)

        if [[ "$major" -eq 3 && "$minor" -ge 9 ]]; then
            PYTHON_CMD="$cmd"
            print_success "Python encontrado: $cmd (versão $version)"
            break
        fi
    fi
done

if [[ -z "$PYTHON_CMD" ]]; then
    print_warning "Python 3.9+ não encontrado!"
    print_info "Instalando Python 3.11 via Homebrew..."
    
    brew install python@3.11
    export PATH="$HOMEBREW_PREFIX/opt/python@3.11/bin:$PATH"
    PYTHON_CMD="python3.11"
    print_success "Python 3.11 instalado"
fi

#===============================================================================
# 4. Instalar Dependências do Sistema
#===============================================================================

print_header "4/8 - Instalando Dependências do Sistema"

echo ""
echo "  Dependências para pygame: SDL2, freetype, portmidi"
echo ""
read -p "  Instalar dependências via Homebrew? [S/n]: " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Ss]$ ]] || [[ -z $REPLY ]]; then
    print_info "Instalando dependências..."
    brew install sdl2 sdl2_image sdl2_mixer sdl2_ttf freetype portmidi wget
    print_success "Dependências instaladas"
else
    print_warning "Pulando instalação de dependências"
fi

#===============================================================================
# 5. Instalar Ollama
#===============================================================================

print_header "5/8 - Instalando Ollama (LLM Local)"

if check_command ollama; then
    OLLAMA_VERSION=$(ollama --version 2>/dev/null | head -1)
    print_success "Ollama já instalado: $OLLAMA_VERSION"
else
    echo ""
    read -p "  Instalar Ollama? [S/n]: " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Ss]$ ]] || [[ -z $REPLY ]]; then
        print_info "Instalando Ollama via Homebrew..."
        brew install ollama
        
        if check_command ollama; then
            print_success "Ollama instalado"
            echo ""
            read -p "  Baixar modelo gemma3:4b (~2.5GB)? [S/n]: " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Ss]$ ]] || [[ -z $REPLY ]]; then
                ollama pull gemma3:4b || print_warning "Falha ao baixar modelo"
            fi
        fi
    fi
fi

#===============================================================================
# 6. Criar Ambiente Virtual Python
#===============================================================================

print_header "6/8 - Configurando Ambiente Virtual"

cd "$PROJECT_ROOT"
VENV_DIR="$PROJECT_ROOT/venv"

if [[ -d "$VENV_DIR" ]]; then
    print_info "Ambiente virtual já existe"
    read -p "  Recriar? [s/N]: " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        rm -rf "$VENV_DIR"
        $PYTHON_CMD -m venv "$VENV_DIR"
        print_success "Ambiente virtual recriado"
    fi
else
    $PYTHON_CMD -m venv "$VENV_DIR"
    print_success "Ambiente virtual criado"
fi

source "$VENV_DIR/bin/activate"
print_success "Ambiente virtual ativado"

#===============================================================================
# 7. Instalar Dependências Python
#===============================================================================

print_header "7/8 - Instalando Dependências Python"

pip install --upgrade pip setuptools wheel --quiet
pip install -r "$PROJECT_ROOT/requirements.txt"
pip install pytz httpx aiofiles --quiet 2>/dev/null || true

print_success "Dependências Python instaladas"

#===============================================================================
# 8. Configurar Estrutura
#===============================================================================

print_header "8/8 - Configurando Estrutura do Projeto"

mkdir -p "$PROJECT_ROOT/data" "$PROJECT_ROOT/assets" "$PROJECT_ROOT/logs" "$PROJECT_ROOT/output"
print_success "Diretórios criados"

if [[ -f "$PROJECT_ROOT/data/experiments.db" ]]; then
    print_success "Banco de dados existente preservado"
fi

# Criar scripts de execução
cat > "$SCRIPT_DIR/start_services.sh" << 'SCRIPT'
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
SCRIPT
chmod +x "$SCRIPT_DIR/start_services.sh"

cat > "$SCRIPT_DIR/stop_services.sh" << 'SCRIPT'
#!/bin/bash
echo "Encerrando serviços Saúdelog..."

pkill -f "uvicorn src.api.main:app" 2>/dev/null && echo "  ✔ API encerrada" || echo "  - API não estava rodando"
pkill -f "streamlit run" 2>/dev/null && echo "  ✔ Streamlit encerrado" || echo "  - Streamlit não estava rodando"

if pgrep -x "ollama" > /dev/null 2>&1; then
    pkill -x "ollama" 2>/dev/null
    echo "  ✔ Ollama encerrado"
else
    echo "  - Ollama não estava rodando"
fi

echo "Serviços encerrados."
SCRIPT
chmod +x "$SCRIPT_DIR/stop_services.sh"

print_success "Scripts criados em instalacao/macos/"

#===============================================================================
# Validação e Conclusão
#===============================================================================

print_header "Validação Final"

$PYTHON_CMD << 'PYCHECK'
import sys
modules = [("numpy","numpy"),("pandas","pandas"),("fastapi","fastapi"),("streamlit","streamlit"),("pygame","pygame")]
failed = []
for name, mod in modules:
    try:
        __import__(mod)
        print(f"    ✔ {name}")
    except:
        print(f"    ✖ {name}")
        failed.append(name)
sys.exit(len(failed))
PYCHECK

echo ""
echo -e "${GREEN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════════╗
║           ✅  INSTALAÇÃO CONCLUÍDA COM SUCESSO!  ✅              ║
╚══════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "
  📋 COMO USAR:

  1. Ativar ambiente virtual:
     ${CYAN}source venv/bin/activate${NC}

  2. Iniciar serviços:
     ${CYAN}./instalacao/macos/start_services.sh${NC}

  3. Parar serviços:
     ${CYAN}./instalacao/macos/stop_services.sh${NC}

  📍 URLs:
     • Dashboard:  ${GREEN}http://localhost:8501${NC}
     • API:        ${GREEN}http://localhost:8000${NC}
     • Swagger:    ${GREEN}http://localhost:8000/docs${NC}
"

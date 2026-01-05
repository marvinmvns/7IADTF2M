#!/bin/bash

#===============================================================================
# Saúdelog - Script de Instalação para Linux
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

# Diretório raiz do projeto (dois níveis acima de instalacao/linux/)
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

print_success() {
    echo -e "${GREEN}  ✔ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}  ⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}  ✖ $1${NC}"
}

print_info() {
    echo -e "${CYAN}  ℹ $1${NC}"
}

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
  Instalação Local - Linux - VRP Optimizer
  FIAP Tech Challenge - Fase 2
  ══════════════════════════════════════════════════
EOF
echo -e "${NC}"

sleep 1

#===============================================================================
# 1. Detectar Sistema Operacional
#===============================================================================

print_header "1/8 - Detectando Sistema Operacional"

OS="linux"
PACKAGE_MANAGER=""

if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    DISTRO="$NAME"
fi

if check_command apt-get; then
    PACKAGE_MANAGER="apt"
elif check_command dnf; then
    PACKAGE_MANAGER="dnf"
elif check_command yum; then
    PACKAGE_MANAGER="yum"
elif check_command pacman; then
    PACKAGE_MANAGER="pacman"
elif check_command zypper; then
    PACKAGE_MANAGER="zypper"
fi

print_success "Sistema Operacional: Linux"
print_success "Distribuição: ${DISTRO:-Desconhecida}"
print_success "Gerenciador de Pacotes: ${PACKAGE_MANAGER:-não detectado}"

#===============================================================================
# 2. Verificar e Instalar Python
#===============================================================================

print_header "2/8 - Verificando Python 3.9+"

PYTHON_CMD=""

# Tentar diferentes comandos Python
for cmd in python3.11 python3.10 python3.9 python3 python; do
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
    print_error "Python 3.9+ não encontrado!"
    print_info "Tentando instalar Python..."

    case "$PACKAGE_MANAGER" in
        apt)
            sudo apt update
            sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
            PYTHON_CMD="python3.11"
            ;;
        dnf)
            sudo dnf install -y python3.11 python3.11-devel python3-pip
            PYTHON_CMD="python3.11"
            ;;
        pacman)
            sudo pacman -S --noconfirm python python-pip
            PYTHON_CMD="python3"
            ;;
        *)
            print_error "Não foi possível instalar Python automaticamente"
            print_info "Por favor, instale Python 3.9+ manualmente:"
            print_info "  https://www.python.org/downloads/"
            exit 1
            ;;
    esac

    print_success "Python instalado: $PYTHON_CMD"
fi

#===============================================================================
# 3. Instalar Dependências do Sistema (SDL2 para pygame)
#===============================================================================

print_header "3/8 - Instalando Dependências do Sistema"

install_system_deps() {
    case "$PACKAGE_MANAGER" in
        apt)
            print_info "Atualizando repositórios e instalando dependências..."
            sudo apt update
            sudo apt install -y \
                python3-pip \
                python3-venv \
                python3-dev \
                libsdl2-dev \
                libsdl2-image-dev \
                libsdl2-mixer-dev \
                libsdl2-ttf-dev \
                libfreetype6-dev \
                libportmidi-dev \
                libjpeg-dev \
                build-essential \
                curl \
                wget \
                git
            ;;
        dnf)
            print_info "Instalando dependências via dnf..."
            sudo dnf install -y \
                python3-pip \
                python3-devel \
                SDL2-devel \
                SDL2_image-devel \
                SDL2_mixer-devel \
                SDL2_ttf-devel \
                freetype-devel \
                portmidi-devel \
                libjpeg-devel \
                gcc \
                gcc-c++ \
                curl \
                wget \
                git
            ;;
        pacman)
            print_info "Instalando dependências via pacman..."
            sudo pacman -S --noconfirm \
                python-pip \
                sdl2 \
                sdl2_image \
                sdl2_mixer \
                sdl2_ttf \
                freetype2 \
                portmidi \
                base-devel \
                curl \
                wget \
                git
            ;;
        *)
            print_warning "Gerenciador de pacotes não suportado"
            print_warning "Instale manualmente: SDL2, SDL2_image, SDL2_mixer, SDL2_ttf, curl, wget"
            return 1
            ;;
    esac
    return 0
}

echo ""
echo "  Dependências do sistema são necessárias para pygame e visualizações."
echo "  Isso requer permissões de administrador (sudo)."
echo ""
read -p "  Instalar dependências do sistema? [S/n]: " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Ss]$ ]] || [[ -z $REPLY ]]; then
    if install_system_deps; then
        print_success "Dependências do sistema instaladas"
    else
        print_warning "Algumas dependências podem estar faltando"
    fi
else
    print_warning "Pulando instalação de dependências do sistema"
fi

#===============================================================================
# 4. Instalar Ollama (LLM Local)
#===============================================================================

print_header "4/8 - Instalando Ollama (LLM Local)"

if check_command ollama; then
    OLLAMA_VERSION=$(ollama --version 2>/dev/null | head -1)
    print_success "Ollama já instalado: $OLLAMA_VERSION"
else
    echo ""
    echo "  Ollama permite usar modelos LLM localmente para análises."
    echo ""
    read -p "  Instalar Ollama? [S/n]: " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Ss]$ ]] || [[ -z $REPLY ]]; then
        print_info "Baixando e instalando Ollama..."
        curl -fsSL https://ollama.com/install.sh | sh

        if check_command ollama; then
            print_success "Ollama instalado com sucesso"

            # Baixar modelo Gemma 3 (leve e eficiente)
            echo ""
            read -p "  Baixar modelo gemma3:4b (recomendado, ~2.5GB)? [S/n]: " -n 1 -r
            echo ""

            if [[ $REPLY =~ ^[Ss]$ ]] || [[ -z $REPLY ]]; then
                print_info "Baixando modelo gemma3:4b (pode demorar alguns minutos)..."
                ollama pull gemma3:4b || print_warning "Falha ao baixar modelo (pode baixar depois)"
            fi
        else
            print_warning "Falha na instalação do Ollama"
        fi
    else
        print_info "Pulando instalação do Ollama"
    fi
fi

#===============================================================================
# 5. Criar Ambiente Virtual Python
#===============================================================================

print_header "5/8 - Configurando Ambiente Virtual Python"

cd "$PROJECT_ROOT"

VENV_DIR="$PROJECT_ROOT/venv"

if [[ -d "$VENV_DIR" ]]; then
    print_info "Ambiente virtual já existe"
    read -p "  Recriar ambiente virtual? (dados serão preservados) [s/N]: " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Ss]$ ]]; then
        print_info "Removendo ambiente virtual antigo..."
        rm -rf "$VENV_DIR"
        $PYTHON_CMD -m venv "$VENV_DIR"
        print_success "Ambiente virtual recriado"
    else
        print_success "Mantendo ambiente virtual existente"
    fi
else
    print_info "Criando ambiente virtual..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    print_success "Ambiente virtual criado: $VENV_DIR"
fi

# Ativar ambiente virtual
source "$VENV_DIR/bin/activate"
print_success "Ambiente virtual ativado"

#===============================================================================
# 6. Instalar Dependências Python (requirements.txt)
#===============================================================================

print_header "6/8 - Instalando Dependências Python"

print_info "Atualizando pip, setuptools e wheel..."
pip install --upgrade pip setuptools wheel --quiet

print_info "Instalando dependências do requirements.txt..."
pip install -r "$PROJECT_ROOT/requirements.txt"

# Dependências adicionais que podem não estar no requirements
print_info "Instalando dependências complementares..."
pip install pytz httpx aiofiles --quiet 2>/dev/null || true

print_success "Todas as dependências Python instaladas"

#===============================================================================
# 7. Configurar Estrutura e Banco de Dados
#===============================================================================

print_header "7/8 - Configurando Estrutura do Projeto"

# Criar diretórios necessários
directories=(
    "$PROJECT_ROOT/data"
    "$PROJECT_ROOT/assets"
    "$PROJECT_ROOT/logs"
    "$PROJECT_ROOT/output"
)

for dir in "${directories[@]}"; do
    mkdir -p "$dir"
done
print_success "Diretórios criados/verificados"

# Verificar banco de dados existente
if [[ -f "$PROJECT_ROOT/data/experiments.db" ]]; then
    DB_SIZE=$(du -h "$PROJECT_ROOT/data/experiments.db" | cut -f1)
    DB_RECORDS=$($PYTHON_CMD -c "
import sqlite3
try:
    conn = sqlite3.connect('$PROJECT_ROOT/data/experiments.db')
    cursor = conn.execute('SELECT COUNT(*) FROM experiments')
    print(cursor.fetchone()[0])
    conn.close()
except:
    print('0')
" 2>/dev/null)
    print_success "Banco de dados existente preservado"
    print_info "  Tamanho: $DB_SIZE | Registros: $DB_RECORDS experimentos"
else
    print_info "Inicializando novo banco de dados..."
    cd "$PROJECT_ROOT"
    $PYTHON_CMD -c "
from src.database.database import create_tables
create_tables()
print('Banco de dados criado com sucesso')
" 2>/dev/null || print_warning "Banco será criado na primeira execução"
fi

#===============================================================================
# Criar Scripts de Execução
#===============================================================================

# Script para iniciar API
cat > "$SCRIPT_DIR/start_api.sh" << 'SCRIPT'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$PROJECT_ROOT"
source venv/bin/activate

echo ""
echo "🚀 Iniciando API FastAPI"
echo "   URL:  http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""

uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
SCRIPT
chmod +x "$SCRIPT_DIR/start_api.sh"

# Script para iniciar Web
cat > "$SCRIPT_DIR/start_web.sh" << 'SCRIPT'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$PROJECT_ROOT"
source venv/bin/activate

echo ""
echo "🌐 Iniciando Streamlit Dashboard"
echo "   URL: http://localhost:8501"
echo ""

streamlit run src/web/app.py --server.port 8501 --server.address 0.0.0.0
SCRIPT
chmod +x "$SCRIPT_DIR/start_web.sh"

# Script para iniciar Ollama
cat > "$SCRIPT_DIR/start_ollama.sh" << 'SCRIPT'
#!/bin/bash
echo ""
echo "🤖 Iniciando Ollama Server"
echo "   URL: http://localhost:11434"
echo ""

if command -v ollama &> /dev/null; then
    ollama serve
else
    echo "❌ Ollama não está instalado"
    echo "   Execute: curl -fsSL https://ollama.com/install.sh | sh"
fi
SCRIPT
chmod +x "$SCRIPT_DIR/start_ollama.sh"

# Script para iniciar TODOS os serviços
cat > "$SCRIPT_DIR/start_services.sh" << 'SCRIPT'
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
    echo "Serviços encerrados."
    exit 0
}

trap cleanup SIGINT SIGTERM

# Aguardar
wait
SCRIPT
chmod +x "$SCRIPT_DIR/start_services.sh"

# Script para parar todos os serviços
cat > "$SCRIPT_DIR/stop_services.sh" << 'SCRIPT'
#!/bin/bash
echo "Encerrando serviços Saúdelog..."

pkill -f "uvicorn src.api.main:app" 2>/dev/null && echo "  ✔ API encerrada"
pkill -f "streamlit run" 2>/dev/null && echo "  ✔ Streamlit encerrado"
pkill -f "ollama serve" 2>/dev/null && echo "  ✔ Ollama encerrado"

echo "Todos os serviços foram encerrados."
SCRIPT
chmod +x "$SCRIPT_DIR/stop_services.sh"

# Script para rodar testes
cat > "$SCRIPT_DIR/run_tests.sh" << 'SCRIPT'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$PROJECT_ROOT"
source venv/bin/activate

echo ""
echo "🧪 Executando testes..."
echo ""

pytest tests/ -v --tb=short
SCRIPT
chmod +x "$SCRIPT_DIR/run_tests.sh"

print_success "Scripts de execução criados em instalacao/linux/"

#===============================================================================
# 8. Validação Final
#===============================================================================

print_header "8/8 - Validação Final da Instalação"

echo ""
print_info "Verificando módulos Python..."
echo ""

VALIDATION_FAILED=0

$PYTHON_CMD << 'PYCHECK'
import sys

modules = [
    ("numpy", "numpy"),
    ("pandas", "pandas"),
    ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn"),
    ("streamlit", "streamlit"),
    ("sqlalchemy", "sqlalchemy"),
    ("folium", "folium"),
    ("matplotlib", "matplotlib"),
    ("pygame", "pygame"),
    ("pydantic", "pydantic"),
    ("requests", "requests"),
]

failed = []
for display_name, module_name in modules:
    try:
        mod = __import__(module_name)
        version = getattr(mod, '__version__', 'OK')
        print(f"    ✔ {display_name}: {version}")
    except ImportError as e:
        print(f"    ✖ {display_name}: FALHOU - {e}")
        failed.append(display_name)

print("")

# Testar imports do projeto
print("  Verificando módulos do projeto...")
try:
    from src.genetic_algorithm import GeneticAlgorithm
    print("    ✔ src.genetic_algorithm")
except Exception as e:
    print(f"    ✖ src.genetic_algorithm: {e}")
    failed.append("genetic_algorithm")

try:
    from src.api.main import app
    print("    ✔ src.api.main")
except Exception as e:
    print(f"    ✖ src.api.main: {e}")
    failed.append("api")

try:
    from src.database.database import create_tables
    print("    ✔ src.database")
except Exception as e:
    print(f"    ✖ src.database: {e}")
    failed.append("database")

sys.exit(len(failed))
PYCHECK

if [[ $? -eq 0 ]]; then
    print_success "Todas as validações passaram!"
else
    print_warning "Algumas validações falharam (verifique acima)"
    VALIDATION_FAILED=1
fi

# Verificar Ollama
echo ""
if check_command ollama; then
    print_success "Ollama instalado"
    MODELS=$(ollama list 2>/dev/null | tail -n +2 | wc -l)
    if [[ $MODELS -gt 0 ]]; then
        print_info "  Modelos disponíveis: $MODELS"
    else
        print_info "  Nenhum modelo baixado (execute: ollama pull gemma3:4b)"
    fi
else
    print_info "Ollama não instalado (opcional para LLM local)"
fi

#===============================================================================
# Conclusão
#===============================================================================

echo ""
echo ""

if [[ $VALIDATION_FAILED -eq 0 ]]; then
    echo -e "${GREEN}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║           ✅  INSTALAÇÃO CONCLUÍDA COM SUCESSO!  ✅              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
else
    echo -e "${YELLOW}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║       ⚠️  INSTALAÇÃO CONCLUÍDA COM AVISOS  ⚠️                   ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
fi

echo -e "
  📋 COMO USAR:

  1. Ativar ambiente virtual:
     ${CYAN}source venv/bin/activate${NC}

  2. Iniciar TODOS os serviços:
     ${CYAN}./instalacao/linux/start_services.sh${NC}

  3. Ou iniciar separadamente:
     ${CYAN}./instalacao/linux/start_api.sh${NC}      # Terminal 1 - API
     ${CYAN}./instalacao/linux/start_web.sh${NC}      # Terminal 2 - Dashboard
     ${CYAN}./instalacao/linux/start_ollama.sh${NC}   # Terminal 3 - LLM (opcional)

  4. Parar todos os serviços:
     ${CYAN}./instalacao/linux/stop_services.sh${NC}

  📍 URLs:
     • Dashboard:  ${GREEN}http://localhost:8501${NC}
     • API:        ${GREEN}http://localhost:8000${NC}
     • Swagger:    ${GREEN}http://localhost:8000/docs${NC}
     • Ollama:     ${GREEN}http://localhost:11434${NC}

  📁 Banco de dados: ${CYAN}data/experiments.db${NC} (preservado)
"

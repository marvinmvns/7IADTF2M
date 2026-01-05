#!/bin/bash

#===============================================================================
# Saúdelog - Script de Desinstalação para Linux
# Remove apenas: ambiente virtual (venv) e Ollama
# NÃO remove: código fonte, banco de dados, logs ou scripts
#===============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALACAO_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$INSTALACAO_DIR")"

print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}\n"
}

print_success() { echo -e "${GREEN}  ✔ $1${NC}"; }
print_warning() { echo -e "${YELLOW}  ⚠ $1${NC}"; }
print_info() { echo -e "${CYAN}  ℹ $1${NC}"; }

clear
echo -e "${RED}"
cat << "EOF"
   ____              __      _      _
  / ___|  __ _ _   _/ _| ___| | ___| | ___   __ _
  \___ \ / _` | | | | |_ / _ \ |/ _ \ |/ _ \ / _` |
   ___) | (_| | |_| |  _|  __/ |  __/ | (_) | (_| |
  |____/ \__,_|\__,_|_|  \___|_|\___|_|\___/ \__, |
                                              |___/
  ══════════════════════════════════════════════════
  Desinstalação - Linux - VRP Optimizer
  ══════════════════════════════════════════════════
EOF
echo -e "${NC}"

echo -e "\n${YELLOW}  Este script remove apenas:${NC}"
echo -e "    • Ambiente virtual Python (venv)"
echo -e "    • Ollama (se instalado)"
echo -e ""
echo -e "${GREEN}  NÃO serão removidos:${NC}"
echo -e "    • Código fonte do projeto"
echo -e "    • Banco de dados (experiments.db)"
echo -e "    • Logs e arquivos de saída"
echo -e "    • Scripts de instalação"
echo ""

# 1. Parar Serviços
print_header "1/3 - Parando Serviços"
pkill -f "uvicorn src.api.main:app" 2>/dev/null && print_success "API encerrada" || print_info "API não estava rodando"
pkill -f "streamlit run" 2>/dev/null && print_success "Streamlit encerrado" || print_info "Streamlit não estava rodando"

if systemctl is-active --quiet ollama 2>/dev/null; then
    sudo systemctl stop ollama 2>/dev/null && print_success "Ollama (systemd) encerrado"
fi
pkill -x "ollama" 2>/dev/null && print_success "Ollama encerrado" || print_info "Ollama não estava rodando"

# 2. Ambiente Virtual
print_header "2/3 - Ambiente Virtual"
VENV_DIR="$PROJECT_ROOT/venv"
if [[ -d "$VENV_DIR" ]]; then
    VENV_SIZE=$(du -sh "$VENV_DIR" 2>/dev/null | cut -f1)
    read -p "  Remover ambiente virtual ($VENV_SIZE)? [S/n]: " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Ss]$ ]] || [[ -z $REPLY ]]; then
        rm -rf "$VENV_DIR"
        print_success "Ambiente virtual removido"
    else
        print_info "Ambiente virtual mantido"
    fi
else
    print_info "Ambiente virtual não encontrado"
fi

# 3. Ollama
print_header "3/3 - Ollama"
if command -v ollama &> /dev/null; then
    read -p "  Desinstalar Ollama e modelos? [s/N]: " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        # Parar e desabilitar serviço systemd
        sudo systemctl stop ollama 2>/dev/null
        sudo systemctl disable ollama 2>/dev/null
        
        # Remover binário
        sudo rm -f /usr/local/bin/ollama 2>/dev/null
        sudo rm -f /usr/bin/ollama 2>/dev/null
        
        # Remover dados e modelos
        rm -rf ~/.ollama 2>/dev/null
        
        # Remover serviço systemd
        sudo rm -f /etc/systemd/system/ollama.service 2>/dev/null
        sudo systemctl daemon-reload 2>/dev/null
        
        print_success "Ollama removido completamente"
    else
        print_info "Ollama mantido"
    fi
else
    print_info "Ollama não estava instalado"
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           ✅  DESINSTALAÇÃO CONCLUÍDA!  ✅                       ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${CYAN}Para remover manualmente:${NC}"
echo -e "    • Banco de dados: ${YELLOW}rm $PROJECT_ROOT/data/experiments.db${NC}"
echo -e "    • Logs:           ${YELLOW}rm -rf $PROJECT_ROOT/logs/${NC}"
echo -e "    • Todo o projeto: ${YELLOW}rm -rf $PROJECT_ROOT${NC}"
echo ""

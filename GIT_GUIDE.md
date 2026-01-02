# Fluxo de Inicialização do Git

Este guia descreve como iniciar o controle de versão neste projeto.

## 1. Inicializar o Repositório
No terminal, execute:
```bash
git init
```

## 2. Criar um arquivo .gitignore
É importante ignorar arquivos temporários ou de ambiente virtual.
```bash
# Exemplo de .gitignore básico para Python
__pycache__/
*.pyc
venv/
.env
```

## 3. Adicionar arquivos
```bash
git add .
```

## 4. Primeiro Commit
```bash
git commit -m "Initial commit: Projeto de algoritmos genéticos com Haversine"
```

## 5. Conectar ao GitHub (Opcional)
```bash
git remote add origin https://github.com/USUARIO/NOME-DO-REPO.git
git branch -M main
git push -u origin main
```

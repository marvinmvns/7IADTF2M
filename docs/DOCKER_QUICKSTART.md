# Docker Quick Start Guide

## ✅ Preparação Concluída

Toda a configuração Docker foi criada com sucesso! Os arquivos estão em:

```
docker/
├── Dockerfile              # ✓ Imagem principal
├── Dockerfile.ollama       # ✓ Ollama + Gemma3
├── docker-compose.yml      # ✓ Com GPU
├── docker-compose.cpu.yml  # ✓ Sem GPU
├── entrypoint.sh           # ✓ Script de init
├── ollama-entrypoint.sh    # ✓ Script Ollama
└── README.md               # ✓ Documentação completa
```

## 🚀 Build Inicial (pode demorar 5-15 minutos)

O primeiro build demora pois precisa:
- Baixar imagem Python base (~150MB)
- Instalar dependências do sistema
- Instalar pacotes Python
- Baixar imagem Ollama
- Baixar modelo Gemma3 (~2GB)

### Opção 1: Build em Etapas (Recomendado)

```bash
# 1. Build apenas a imagem principal (mais rápido)
docker-compose -f docker/docker-compose.cpu.yml build api web

# 2. Iniciar apenas API e Web (sem Ollama)
docker-compose -f docker/docker-compose.cpu.yml up -d api web

# 3. Verificar se estão rodando
docker-compose -f docker/docker-compose.cpu.yml ps

# 4. (Opcional) Build Ollama depois
docker-compose -f docker/docker-compose.cpu.yml build ollama
docker-compose -f docker/docker-compose.cpu.yml up -d ollama
```

### Opção 2: Build Completo

```bash
# Build tudo de uma vez (demora mais)
docker-compose -f docker/docker-compose.cpu.yml up -d --build

# Acompanhar logs
docker-compose -f docker/docker-compose.cpu.yml logs -f
```

## 🧪 Testar Antes do Docker (Mais Rápido)

Se quiser testar rapidamente sem esperar o Docker:

```bash
# 1. Instalar dependências localmente
pip install -r requirements.txt

# 2. Iniciar API em um terminal
uvicorn src.api.main:app --reload

# 3. Em outro terminal, iniciar Web
streamlit run src/web/app.py

# 4. Acessar:
# - API: http://localhost:8000/docs
# - Web: http://localhost:8501
```

## 📊 Verificar Status

```bash
# Ver containers rodando
docker-compose -f docker/docker-compose.cpu.yml ps

# Ver logs
docker-compose -f docker/docker-compose.cpu.yml logs api
docker-compose -f docker/docker-compose.cpu.yml logs web
docker-compose -f docker/docker-compose.cpu.yml logs ollama

# Ver recursos
docker stats
```

## 🔍 Troubleshooting

### Build muito lento?

O primeiro build é sempre lento. Builds subsequentes usam cache e são mais rápidos.

### Erro de memória?

```bash
# Aumentar memória do Docker
# Docker Desktop > Settings > Resources > Memory: 4-8GB
```

### Container não inicia?

```bash
# Ver logs detalhados
docker-compose -f docker/docker-compose.cpu.yml logs api

# Entrar no container para debug
docker-compose -f docker/docker-compose.cpu.yml run api bash
```

### Porta já em uso?

```bash
# Verificar o que está usando a porta
sudo lsof -i :8000
sudo lsof -i :8501

# Parar o processo ou mudar a porta no docker-compose.yml
```

## 🎯 Próximos Passos

1. **Testar API**:
   ```bash
   curl http://localhost:8000/
   curl http://localhost:8000/docs
   ```

2. **Testar Web**:
   Abra http://localhost:8501 no navegador

3. **Testar Ollama** (se instalou):
   ```bash
   curl http://localhost:11434/api/tags
   ```

4. **Criar experimento**:
   Use a interface web ou:
   ```bash
   curl -X POST http://localhost:8000/run \
     -H "Content-Type: application/json" \
     -d '{
       "population_size": 50,
       "max_generations": 100,
       "scenario": "small"
     }'
   ```

## 📦 Publicar no Docker Hub

Quando estiver satisfeito com as imagens:

```bash
# 1. Login
docker login

# 2. Tag as imagens
docker tag docker_api:latest seu-usuario/ga-vrp-api:2.0.0
docker tag docker_web:latest seu-usuario/ga-vrp-web:2.0.0
docker tag docker_ollama:latest seu-usuario/ga-vrp-ollama:2.0.0

# 3. Push
docker push seu-usuario/ga-vrp-api:2.0.0
docker push seu-usuario/ga-vrp-web:2.0.0
docker push seu-usuario/ga-vrp-ollama:2.0.0

# 4. Usar em produção
# Edite docker-compose.yml para usar:
# image: seu-usuario/ga-vrp-api:2.0.0
# Remova a seção 'build'
```

## 🛑 Parar Tudo

```bash
# Parar containers
docker-compose -f docker/docker-compose.cpu.yml stop

# Parar e remover
docker-compose -f docker/docker-compose.cpu.yml down

# Parar e remover volumes (CUIDADO: apaga dados)
docker-compose -f docker/docker-compose.cpu.yml down -v
```

## ✨ Resumo

- ✅ Configuração Docker completa criada
- ✅ Scripts de entrypoint funcionais
- ✅ Documentação detalhada em `docker/README.md`
- ✅ Suporte GPU e CPU
- ✅ Ollama + Gemma3 configurado
- ✅ Todos os serviços orquestrados

**Tudo pronto para uso! 🎉**

Para documentação completa, veja: `docker/README.md`

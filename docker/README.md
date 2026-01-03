# Docker Configuration - GA VRP Optimization

Este diretório contém todos os arquivos de configuração Docker para o projeto de Otimização de Rotas com Algoritmos Genéticos.

## 📦 Arquivos

- **Dockerfile**: Imagem principal da aplicação (API + Web)
- **Dockerfile.ollama**: Imagem Ollama com modelo Gemma3
- **docker-compose.yml**: Orquestração completa com GPU
- **docker-compose.cpu.yml**: Orquestração sem GPU (CPU only)
- **entrypoint.sh**: Script de inicialização da aplicação
- **ollama-entrypoint.sh**: Script de inicialização do Ollama
- **README.md**: Esta documentação

## 🚀 Quick Start

### Opção 1: Com GPU (NVIDIA)

```bash
# Build e start de todos os serviços
docker-compose -f docker/docker-compose.yml up --build

# Ou em modo detached (background)
docker-compose -f docker/docker-compose.yml up -d --build
```

### Opção 2: Sem GPU (CPU only)

```bash
# Build e start com CPU
docker-compose -f docker/docker-compose.cpu.yml up --build

# Ou em modo detached
docker-compose -f docker/docker-compose.cpu.yml up -d --build
```

## 🌐 Acessando os Serviços

Após iniciar os containers:

- **API FastAPI**: http://localhost:8000
  - Documentação Swagger: http://localhost:8000/docs
  - Documentação ReDoc: http://localhost:8000/redoc

- **Web Interface (Streamlit)**: http://localhost:8501

- **Ollama Server**: http://localhost:11434
  - Teste: `curl http://localhost:11434/api/tags`

## 🏗️ Arquitetura dos Serviços

### 1. API Service (`ga-vrp-api`)

- **Base Image**: `python:3.11-slim`
- **Porta**: 8000
- **Função**: API REST com FastAPI
- **Volumes**:
  - `../data:/app/data` - Banco de dados SQLite
  - `../docs:/app/docs` - Documentação gerada
- **Health Check**: `curl http://localhost:8000/`

### 2. Web Service (`ga-vrp-web`)

- **Base Image**: `python:3.11-slim`
- **Porta**: 8501
- **Função**: Dashboard Streamlit
- **Volumes**:
  - `../data:/app/data` - Dados compartilhados com API
  - `../assets:/app/assets` - Recursos estáticos
- **Dependências**: `api`

### 3. Ollama Service (`ga-vrp-ollama`)

- **Base Image**: `ollama/ollama:latest`
- **Porta**: 11434
- **Função**: Servidor LLM local com Gemma3
- **Volumes**:
  - `ollama-models:/root/.ollama` - Armazenamento de modelos
- **GPU**: Opcional (configurado em docker-compose.yml)

## 🔧 Comandos Úteis

### Build

```bash
# Build todos os serviços
docker-compose -f docker/docker-compose.yml build

# Build serviço específico
docker-compose -f docker/docker-compose.yml build api

# Build sem cache
docker-compose -f docker/docker-compose.yml build --no-cache
```

### Start/Stop

```bash
# Start todos os serviços
docker-compose -f docker/docker-compose.yml up

# Start em background
docker-compose -f docker/docker-compose.yml up -d

# Stop todos os serviços
docker-compose -f docker/docker-compose.yml down

# Stop e remove volumes
docker-compose -f docker/docker-compose.yml down -v
```

### Logs

```bash
# Ver logs de todos os serviços
docker-compose -f docker/docker-compose.yml logs

# Ver logs em tempo real
docker-compose -f docker/docker-compose.yml logs -f

# Logs de serviço específico
docker-compose -f docker/docker-compose.yml logs -f api
docker-compose -f docker/docker-compose.yml logs -f ollama
```

### Exec (executar comandos)

```bash
# Shell no container da API
docker-compose -f docker/docker-compose.yml exec api bash

# Shell no container do Ollama
docker-compose -f docker/docker-compose.yml exec ollama bash

# Executar comando Python
docker-compose -f docker/docker-compose.yml exec api python -c "print('Hello')"

# Executar testes
docker-compose -f docker/docker-compose.yml exec api pytest tests/
```

### Status

```bash
# Ver status dos containers
docker-compose -f docker/docker-compose.yml ps

# Ver recursos utilizados
docker stats
```

## 🧪 Testando Ollama

### Verificar modelos disponíveis

```bash
curl http://localhost:11434/api/tags
```

### Fazer uma pergunta ao Gemma3

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "gemma2:latest",
  "prompt": "Explain genetic algorithms in one paragraph",
  "stream": false
}'
```

### Testar chat

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "gemma2:latest",
  "messages": [
    {"role": "user", "content": "What is the Vehicle Routing Problem?"}
  ],
  "stream": false
}'
```

## 🐳 Publicando no Docker Hub

### 1. Build com tag

```bash
# Build imagem principal
docker build -t seu-usuario/ga-vrp-app:latest -f docker/Dockerfile .
docker build -t seu-usuario/ga-vrp-app:2.0.0 -f docker/Dockerfile .

# Build imagem Ollama
docker build -t seu-usuario/ga-vrp-ollama:latest -f docker/Dockerfile.ollama .
```

### 2. Login no Docker Hub

```bash
docker login
```

### 3. Push para Docker Hub

```bash
# Push imagem principal
docker push seu-usuario/ga-vrp-app:latest
docker push seu-usuario/ga-vrp-app:2.0.0

# Push imagem Ollama
docker push seu-usuario/ga-vrp-ollama:latest
```

### 4. Usar imagens do Docker Hub

Edite o `docker-compose.yml` para usar suas imagens:

```yaml
services:
  api:
    image: seu-usuario/ga-vrp-app:latest
    # Remove a seção 'build'

  ollama:
    image: seu-usuario/ga-vrp-ollama:latest
    # Remove a seção 'build'
```

## ⚙️ Variáveis de Ambiente

### API/Web Container

- `SERVICE_TYPE`: Tipo de serviço (`api`, `web`, `all`)
- `PYTHONUNBUFFERED`: Desabilita buffer do Python (1)

### Ollama Container

- `OLLAMA_HOST`: Host e porta do servidor (default: `0.0.0.0:11434`)
- `OLLAMA_MODELS`: Diretório de modelos (default: `/root/.ollama/models`)

## 📊 Volumes

### Volumes Nomeados

- `ollama-models`: Armazena modelos Gemma3 (persistente)
- `api-cache`: Cache do pip e Python para API
- `web-cache`: Cache do pip e Python para Web

### Volumes Montados

- `../data`: Banco de dados SQLite (compartilhado entre containers)
- `../docs`: Documentação OpenAPI gerada
- `../assets`: Recursos estáticos (logos, imagens)

## 🔒 Segurança

### Recomendações para Produção

1. **Não exponha todas as portas**:
   ```yaml
   ports:
     - "127.0.0.1:8000:8000"  # Apenas localhost
   ```

2. **Use secrets do Docker**:
   ```yaml
   secrets:
     - db_password
   ```

3. **Configure resource limits**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 4G
   ```

4. **Use user não-root**:
   ```dockerfile
   RUN useradd -m appuser
   USER appuser
   ```

## 🐛 Troubleshooting

### Container não inicia

```bash
# Ver logs detalhados
docker-compose -f docker/docker-compose.yml logs api

# Verificar saúde do container
docker inspect ga-vrp-api | grep -A 10 Health
```

### Ollama não baixa o modelo

```bash
# Entrar no container
docker-compose -f docker/docker-compose.yml exec ollama bash

# Baixar manualmente
ollama pull gemma2:latest
```

### Erro de permissão em volumes

```bash
# Ajustar permissões (Linux)
sudo chown -R $USER:$USER data/
```

### Sem GPU NVIDIA

Use o arquivo `docker-compose.cpu.yml`:

```bash
docker-compose -f docker/docker-compose.cpu.yml up
```

## 📖 Documentação Adicional

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Ollama Documentation](https://github.com/jmorganca/ollama)
- [FastAPI in Docker](https://fastapi.tiangolo.com/deployment/docker/)

## 📝 Notas

- O primeiro start pode demorar pois o Gemma3 (~2GB) será baixado
- Ollama em CPU é mais lento que em GPU
- Modelos ficam persistidos no volume `ollama-models`
- Banco de dados SQLite é compartilhado entre API e Web

## 🤝 Contribuindo

Para modificar a configuração Docker:

1. Edite os arquivos em `docker/`
2. Teste localmente: `docker-compose -f docker/docker-compose.yml up --build`
3. Verifique logs e health checks
4. Commit e push

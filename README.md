# Otimização de Rotas para Distribuição de Medicamentos com Algoritmos Genéticos

**FIAP Tech Challenge - Fase 2**

Sistema completo de otimização de rotas utilizando Algoritmos Genéticos. Implementa arquitetura MVC com API REST, interface web moderna, visualização em tempo real e testes automatizados. O projeto conta com aproximadamente 14.200 linhas de código distribuídas em 30 módulos Python, incluindo 24 operadores genéticos distintos.

Atenção a conclusão e as otimizações e resultado encontram-se em 13. [Conclusão](#13-conclusão)

## 🚀 Instalação Rápida

### 🐳 Docker (Recomendado)
```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd 7IADTF2M

# 2. Inicie todos os serviços
docker-compose -f docker/docker-compose.cpu.yml up -d --build

# 3. Para parar os serviços
docker-compose -f docker/docker-compose.cpu.yml down
```
> ⚠️ A interface Pygame não funciona via Docker

### ⚙️ Execução Manual (com seu próprio Ollama)

Se você já possui as dependências instaladas (`pip install -r requirements.txt`) e quer usar seu próprio Ollama:

```bash
# 1. Ative o ambiente virtual
source venv/bin/activate  # Linux/macOS
# ou: venv\Scripts\activate  # Windows

# 2. Inicie a API (Terminal 1)
uvicorn src.api.main:app --reload --port 8000

# 3. Inicie o Dashboard (Terminal 2)
streamlit run src/web/app.py
```

> 💡 **Configurar Ollama:** No Dashboard (http://localhost:8501), clique na ⚙️ engrenagem e aponte para seu Ollama (ex: `http://localhost:11434`)

---

Para instalar localmente, de acordo com o sistema operacional use:

### 🐧 Linux
```bash
# 1. Clone o repositório e entre no diretório
git clone <url-do-repositorio>
cd 7IADTF2M

# 2. Execute o script de instalação
chmod +x instalacao/linux/install.sh
./instalacao/linux/install.sh

# 3. Inicie os serviços
./instalacao/linux/start_services.sh

# 4. Para parar os serviços
./instalacao/linux/stop_services.sh
```

### 🍎 macOS
```bash
# 1. Clone o repositório e entre no diretório
git clone <url-do-repositorio>
cd 7IADTF2M

# 2. Execute o script de instalação
chmod +x instalacao/macos/install.sh
./instalacao/macos/install.sh

# 3. Inicie os serviços
./instalacao/macos/start_services.sh

# 4. Para parar os serviços
./instalacao/macos/stop_services.sh
```

### 🪟 Windows (PowerShell como Administrador)
```powershell
# 1. Clone o repositório e entre no diretório
git clone <url-do-repositorio>
cd 7IADTF2M

# 2. Execute o script de instalação
.\instalacao\windows\install.ps1

# 3. Inicie os serviços
.\instalacao\windows\start_services.bat

# 4. Para parar os serviços
.\instalacao\windows\stop_services.bat
```

### 📁 Estrutura dos Scripts

```
instalacao/
├── linux/   → install.sh, uninstall.sh, start_services.sh, stop_services.sh
├── macos/   → install.sh, uninstall.sh, start_services.sh, stop_services.sh
└── windows/ → install.ps1, uninstall.ps1, start_services.bat, stop_services.bat
```

### 🌐 URLs dos Serviços (após instalação)

| Serviço | URL |
|---------|-----|
| Dashboard Web | http://localhost:8501 |
| API FastAPI | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| Ollama LLM | http://localhost:11434 |



---

## Sumário

1. [Introdução](#1-introdução)
2. [O Problema de Roteamento de Veículos](#2-o-problema-de-roteamento-de-veículos)
3. [Algoritmos Genéticos](#3-algoritmos-genéticos)
4. [Tipos de Função de Fitness](#4-tipos-de-função-de-fitness)
5. [Operadores Genéticos Implementados](#5-operadores-genéticos-implementados)
6. [Estrutura do Código](#6-estrutura-do-código)
7. [Arquitetura do Sistema](#7-arquitetura-do-sistema)
8. [Interfaces e Visualizações](#8-interfaces-e-visualizações)
9. [Instalação e Configuração](#9-instalação-e-configuração)
10. [Guia Completo de Execução](#10-guia-completo-de-execução)
11. [Testes Automatizados](#11-testes-automatizados)
12. [Resultados dos Experimentos](#12-resultados-dos-experimentos)
13. [Conclusão](#13-conclusão)
14. [Referências](#14-referências)

---

## 1. Introdução

Este projeto apresenta uma solução para o problema de distribuição de medicamentos e insumos hospitalares no estado de São Paulo, utilizando Algoritmos Genéticos como técnica de otimização. O problema tratado é uma variação do Problema do Caixeiro Viajante com Múltiplos Veículos (mVRP), incluindo restrições realistas como capacidade de carga, autonomia dos veículos, janelas de tempo e prioridades de entrega.

A solução não se limita a minimizar distâncias. O sistema considera que medicamentos críticos têm prioridade absoluta sobre entregas regulares, e que veículos possuem limitações físicas que devem ser respeitadas. Todo o desenvolvimento foi realizado em Python, com três formas distintas de visualização: mapas interativos HTML, interface em tempo real com Pygame e dashboard executivo web com Streamlit.

O projeto foi estruturado seguindo princípios de engenharia de software moderna, com separação clara de responsabilidades, persistência de dados, API REST para integração externa e cobertura completa de testes automatizados.

## 2. O Problema de Roteamento de Veículos

O Problema de Roteamento de Veículos (Vehicle Routing Problem - VRP) é um dos desafios clássicos de otimização combinatória na área de pesquisa operacional. O objetivo central é definir rotas eficientes para uma frota de veículos que deve atender um conjunto de clientes, partindo de um depósito central e retornando a ele após completar as entregas.

Neste projeto, implementamos uma variante complexa do VRP com as seguintes características:

**Múltiplos Veículos (mVRP):** O sistema gerencia uma frota de veículos que operam simultaneamente. Cada veículo é uma entidade independente com suas próprias características e restrições.

**Capacidade Limitada (CVRP):** Cada veículo possui uma capacidade máxima de carga medida em unidades de volume ou peso. Quando a capacidade é atingida, o veículo precisa retornar ao depósito antes de continuar atendendo outros pontos.

**Restrição de Autonomia:** Além da capacidade de carga, cada veículo tem uma distância máxima que pode percorrer antes de necessitar retornar ao depósito. Esta restrição simula limitações de combustível ou bateria.

**Prioridades de Entrega:** As entregas são classificadas em três níveis de prioridade - crítica (prioridade 1), urgente (prioridade 2) e regular (prioridade 3). Medicamentos críticos devem ser entregues prioritariamente, independente da distância percorrida. Esta característica distingue o problema de uma simples otimização de distância.

**Dados Geográficos Reais:** O sistema trabalha com coordenadas geográficas reais (latitude e longitude) de hospitais do estado de São Paulo. As distâncias são calculadas usando a fórmula de Haversine, que fornece a distância geodésica entre dois pontos na superfície terrestre.

## 3. Algoritmos Genéticos

Algoritmos Genéticos são técnicas de otimização inspiradas na teoria da evolução de Charles Darwin. Eles trabalham com uma população de soluções candidatas que evoluem ao longo de gerações sucessivas, melhorando gradualmente sua qualidade através de processos que simulam seleção natural, reprodução e mutação.

### 3.1 Estrutura Básica

Um Algoritmo Genético opera em ciclos repetidos que seguem este fluxo:

**Inicialização:** Cria-se uma população inicial de soluções. Estas soluções podem ser completamente aleatórias ou parcialmente construídas usando heurísticas (como o algoritmo do vizinho mais próximo).

**Avaliação:** Cada solução é avaliada através de uma função de fitness, que mede numericamente sua qualidade. Quanto menor o fitness, melhor a solução (no contexto de minimização).

**Seleção:** Indivíduos com melhor fitness têm maior probabilidade de serem selecionados como pais para a próxima geração.

**Crossover (Recombinação):** Pares de pais trocam informações genéticas para criar novos indivíduos (filhos) que herdam características de ambos.

**Mutação:** Pequenas alterações aleatórias são introduzidas nos filhos para manter diversidade genética e explorar novas regiões do espaço de busca.

**Substituição:** A nova geração substitui a antiga, geralmente preservando os melhores indivíduos (elitismo).

**Critério de Parada:** O processo se repete até atingir um número máximo de gerações, alcançar um fitness alvo ou detectar estagnação (quando não há melhoria significativa por várias gerações consecutivas).

### 3.2 Representação do Cromossomo

A forma como representamos uma solução é crítica para o sucesso do algoritmo. Neste projeto, cada cromossomo é uma permutação de todos os pontos de entrega, excluindo o depósito (que sempre está na posição 0).

Exemplo prático: Se temos 8 hospitais numerados de 1 a 8 e 2 veículos, um cromossomo pode ser representado como [3, 5, 1, 8, 2, 4, 6, 7]. Durante a avaliação do fitness, o algoritmo percorre esta sequência e divide as rotas quando uma restrição (capacidade ou autonomia) é violada:

- Rota do Veículo 1: Depósito → Hospital 3 → Hospital 5 → Hospital 1 → Depósito
- Rota do Veículo 2: Depósito → Hospital 8 → Hospital 2 → Hospital 4 → Hospital 6 → Hospital 7 → Depósito

Esta representação é flexível e permite que o próprio algoritmo descubra quantos veículos são necessários e como distribuir os pontos entre eles.

### 3.3 Função de Fitness

A função de fitness é o mecanismo que guia a evolução do algoritmo. Neste projeto, implementamos uma função multi-objetivo ponderada que equilibra diferentes aspectos da qualidade da solução:

```
Fitness = w1 × Distância_Total + w2 × Penalidade_Prioridade +
          w3 × Penalidade_Capacidade + w4 × Penalidade_Autonomia
```

**Distância Total:** Soma das distâncias percorridas por todos os veículos em todas as rotas.

**Penalidade de Prioridade:** Aplica-se quando entregas críticas (prioridade 1) não são realizadas no início das rotas. Esta penalidade é alta o suficiente para forçar o algoritmo a priorizar medicamentos emergenciais.

**Penalidade de Capacidade:** Acrescenta um custo quando a capacidade do veículo é excedida, forçando a criação de uma nova rota.

**Penalidade de Autonomia:** Similar à penalidade de capacidade, mas relacionada à distância máxima que o veículo pode percorrer.

Os pesos (w1, w2, w3, w4) são configuráveis e permitem ajustar a importância relativa de cada objetivo.

## 4. Tipos de Função de Fitness

O sistema implementa quatro estratégias distintas de avaliação de fitness, cada uma adequada a diferentes cenários operacionais. A escolha do tipo de fitness impacta diretamente os resultados da otimização.

### 4.1 Distance Only (Apenas Distância)

A estratégia mais simples, focada exclusivamente na minimização da quilometragem total percorrida pela frota.

**Fórmula:**
```
Fitness = Σ (Distância de cada rota)
```

**Características:**
- Otimiza exclusivamente o custo de transporte
- Não considera prioridades de entrega
- Ideal para logística simples sem restrições de urgência
- Eficiência típica: 4-12%

### 4.2 Priority Aware (Consciente de Prioridade)

Além da distância, penaliza soluções que atrasam entregas urgentes ou críticas.

**Fórmula:**
```
Fitness = Distância_Total + (Tempo_Crítico × 1.0) + (Tempo_Urgente × 0.5) + (Tempo_Regular × 0.1)
```

**Níveis de Prioridade:**
| Nível | Tipo | Peso | Aplicação |
|-------|------|------|-----------|
| 1 | Crítico | 100 | Insulina, sangue, medicamentos de emergência |
| 2 | Urgente | 50 | Antibióticos, medicamentos de curto prazo |
| 3 | Regular | 10 | Suprimentos de rotina |

**Características:**
- Garante que hospitais críticos sejam atendidos primeiro
- Balanceia eficiência com urgência
- Ideal para operações hospitalares
- Eficiência típica: 4-11%

### 4.3 Weighted Multi-Objective (Multi-Objetivo Ponderado)

A estratégia mais completa, considerando seis fatores simultaneamente com pesos configuráveis.

**Componentes:**
| Componente | Peso | O que mede |
|------------|------|------------|
| Tempo | 1.0 | Tempo total de viagem |
| Custo Operacional | 0.5 | Consumo de combustível |
| Prioridade | 10.0 | Penalidade por atrasar entregas críticas |
| Capacidade | 100.0 | Penalidade por exceder carga máxima |
| Autonomia | 100.0 | Penalidade por exceder km máximo |
| Janela de Tempo | 50.0 | Penalidade por chegar fora do horário |

**Fórmula:**
```
Fitness = (Tempo × 1.0) + (Custo × 0.5) + (Penalidade_Prioridade × 10.0) +
          (Violação_Capacidade × 100.0) + (Violação_Autonomia × 100.0) +
          (Violação_Janela × 50.0)
```

**Características:**
- Abordagem mais abrangente
- Garante soluções operacionalmente viáveis
- Maior potencial de otimização (até 43%)
- Ideal para operações complexas com múltiplas restrições
- Eficiência típica: 18-43%

### 4.4 Penalty Based (Baseado em Penalidades Adaptativas)

Utiliza penalidades que aumentam exponencialmente ao longo das gerações, permitindo exploração inicial e convergência para soluções viáveis.

**Mecanismo:**
```
Penalidade_Atual = Penalidade_Base × (1.1 ^ Geração)

Geração 0:   Penalidade = 100 × 1.1^0 = 100
Geração 50:  Penalidade = 100 × 1.1^50 = 11.739
Geração 100: Penalidade = 100 × 1.1^100 = 1.378.061
```

**Características:**
- Permite explorar soluções "inviáveis" no início
- Força convergência para viabilidade
- Garante rotas 100% executáveis
- Ideal quando restrições devem ser rigorosamente respeitadas
- Eficiência típica: 9-23%

### 4.5 Comparativo de Eficiência

| Tipo de Fitness | Eficiência Média | Melhor Caso | Recomendação |
|-----------------|------------------|-------------|--------------|
| Weighted Multi-Objective | 28.4% | 43.1% | Múltiplos objetivos |
| Penalty Based | 16.2% | 22.9% | Muitas restrições |
| Priority Aware | 7.3% | 11.1% | Entregas urgentes |
| Distance Only | 7.1% | 12.0% | Simplicidade |

## 5. Operadores Genéticos Implementados

Uma das principais contribuições deste projeto é a implementação completa de múltiplas variantes de operadores genéticos, permitindo análise comparativa de desempenho. Foram implementados 24 operadores distintos.

### 5.1 Operadores de Seleção

A seleção determina quais indivíduos se reproduzirão. Foram implementados 8 métodos:

**Seleção por Roleta (Roulette Wheel):** Cada indivíduo tem probabilidade de seleção proporcional ao seu fitness. Indivíduos com melhor fitness ocupam maior "fatia" da roleta.

**Seleção por Torneio (Tournament):** Escolhe-se aleatoriamente k indivíduos e seleciona-se o melhor entre eles. É simples, eficiente e permite controlar a pressão seletiva através do parâmetro k.

**Seleção por Ranking (Rank):** A probabilidade de seleção é baseada na posição do indivíduo no ranking ordenado por fitness, não no valor absoluto do fitness. Reduz o risco de convergência prematura.

**Seleção por Truncamento (Truncation):** Apenas os melhores T% da população são selecionados para reprodução. É uma abordagem direta mas pode reduzir a diversidade genética rapidamente.

**Seleção Elitista (Elitist):** Garante que os melhores indivíduos da geração atual passem diretamente para a próxima geração sem alterações.

**Amostragem Universal Estocástica (SUS):** Versão melhorada da roleta que usa múltiplos ponteiros igualmente espaçados, reduzindo o viés estocástico da seleção por roleta simples.

**Seleção de Boltzmann:** Usa uma "temperatura" que controla a pressão seletiva. No início (temperatura alta), a seleção é mais aleatória. Com o tempo (temperatura reduzida), favorece cada vez mais os melhores indivíduos.

**Seleção de Estado Estacionário (Steady State):** Apenas uma pequena fração da população é substituída a cada geração. Preserva mais a população existente entre gerações.

### 5.2 Operadores de Crossover

O crossover combina material genético de dois pais. Para problemas de permutação como o VRP, operadores especiais são necessários para manter a validade das soluções (sem duplicatas ou omissões). Foram implementados 8 operadores:

**Partially Mapped Crossover (PMX):** Copia um segmento de um pai para o filho e usa mapeamento para resolver conflitos. Preserva tanto a ordem relativa quanto a posição absoluta de alguns genes.

**Order Crossover (OX):** Copia um segmento de um pai e preenche as posições restantes com genes do outro pai na ordem em que aparecem. Preserva principalmente a ordem relativa.

**Cycle Crossover (CX):** Identifica ciclos de posições entre os pais e os alterna para criar filhos. Cada gene herda sua posição de um dos pais.

**Alternating Edges Crossover (AEX):** Constrói o filho alternando arestas (conexões entre cidades) dos dois pais.

**Edge Recombination Crossover (ERX):** Constrói uma tabela de adjacências dos pais e usa esta informação para criar filhos que preservam o máximo possível de arestas parentais.

**Sequential Constructive Crossover (SCX):** Constrói o filho sequencialmente, escolhendo o próximo gene baseado em critérios de distância mínima.

**Order-Based Crossover (OX2):** Variante do OX que seleciona posições aleatórias em vez de um segmento contínuo.

**Position-Based Crossover (POS):** Preserva as posições dos genes selecionados de um pai e preenche o resto com genes do outro pai.

### 5.3 Operadores de Mutação

A mutação introduz variabilidade genética e ajuda a explorar novas regiões do espaço de busca. Foram implementados 8 operadores:

**Swap Mutation:** Escolhe aleatoriamente dois genes e troca suas posições. É o operador de mutação mais simples.

**Inversion Mutation:** Seleciona um segmento do cromossomo e inverte sua ordem. É equivalente a uma operação 2-opt aplicada aleatoriamente.

**Scramble Mutation:** Seleciona um segmento e embaralha aleatoriamente os genes dentro dele.

**Insert Mutation:** Remove um gene de uma posição e o insere em outra posição.

**Displacement Mutation:** Remove um segmento inteiro e o reinsere em outra posição, mantendo a ordem interna do segmento.

**2-opt Mutation:** Remove duas arestas da rota e reconecta os segmentos de forma a eliminar cruzamentos. É uma técnica clássica de melhoria local em problemas de roteamento.

**3-opt Mutation:** Versão mais complexa do 2-opt que remove três arestas e considera múltiplas formas de reconexão.

**Reverse Sequence Mutation (RSM):** Variante da inversão com seleção de segmento baseada em tamanho aleatório.

## 6. Estrutura do Código

O projeto foi organizado seguindo princípios de modularização e separação de responsabilidades, facilitando manutenção, testes e extensibilidade.

```
projeto2_haversine/
├── data/
│   ├── hospitais_sp.py         # Dados dos hospitais e cenários de teste
│   ├── hospitais_sp.json       # Dados em formato JSON (19KB)
│   └── experiments.db          # Banco SQLite de experimentos
├── src/
│   ├── genetic_algorithm/      # Núcleo do Algoritmo Genético (4.085 linhas)
│   │   ├── chromosome.py       # Representação do cromossomo e rotas (494 linhas)
│   │   ├── population.py       # Gerenciamento da população (309 linhas)
│   │   ├── selection.py        # 8 métodos de seleção (632 linhas)
│   │   ├── crossover.py        # 8 operadores de crossover (953 linhas)
│   │   ├── mutation.py         # 8 operadores de mutação (471 linhas)
│   │   ├── fitness.py          # Função de fitness multi-objetivo (617 linhas)
│   │   └── genetic_algorithm.py # Orquestrador principal (579 linhas)
│   ├── visualization/          # Camada de Visualização (3.211 linhas)
│   │   ├── route_visualizer.py      # Mapas Folium e Matplotlib (606 linhas)
│   │   ├── evolution_visualizer.py  # Visualização Pygame (565 linhas)
│   │   └── interactive_viewer.py    # Interface interativa completa (2.017 linhas)
│   ├── api/                    # API REST com FastAPI (125 linhas)
│   │   └── main.py             # 10 endpoints RESTful
│   ├── controllers/            # Camada de Controle (260 linhas)
│   │   └── experiment_manager.py # Gerenciador de experimentos
│   ├── database/               # Camada de Persistência (47 linhas)
│   │   ├── database.py         # Configuração SQLAlchemy (22 linhas)
│   │   └── models.py           # Modelo ORM Experiment (25 linhas)
│   ├── web/                    # Interface Web com Streamlit
│   │   ├── app.py              # Dashboard executivo
│   │   ├── components/
│   │   │   └── styles.py       # Estilização CSS
│   │   └── pages/              # Páginas adicionais
│   └── utils/
│       └── distance.py         # Cálculo de distância Haversine
├── tests/                      # Suite de Testes (8 arquivos)
│   ├── test_ga_core.py         # Testes do núcleo
│   ├── test_ga_operators.py    # Testes dos operadores
│   ├── test_ga_fitness.py      # Testes de fitness
│   ├── test_ga_integration.py  # Testes de integração
│   ├── test_api.py             # Testes da API
│   ├── test_api_execution.py   # Testes de execução
│   ├── test_controller.py      # Testes do controller
│   └── test_database.py        # Testes de persistência
├── assets/
│   └── logo.png                # Logo do projeto
├── main.py                     # Script principal de execução
├── pytest.ini                  # Configuração de testes
├── README.md                   # Esta documentação
├── CLAUDE.md                   # Instruções para Claude Code
└── requirements.txt            # Dependências do projeto
```

**Estatísticas do Projeto:**
- Total de linhas de código: aproximadamente 14.200
- Arquivos Python: 30 módulos
- Operadores genéticos: 24 (8 seleção + 8 crossover + 8 mutação)
- Endpoints API: 10 endpoints RESTful
- Suites de teste: 8 arquivos
- Tamanho total: 2,1 MB

## 7. Arquitetura do Sistema

O sistema implementa uma arquitetura em três camadas seguindo o padrão MVC (Model-View-Controller), com persistência de dados, API REST e interfaces modernas.

### 7.1 Camada de Modelo (Model)

**Banco de Dados:** SQLite com SQLAlchemy ORM gerencia a persistência de experimentos.

O modelo Experiment armazena:
- Identificador único e timestamp de criação
- Status (pending, running, completed, failed)
- Configuração completa em formato JSON
- Resultados: melhor fitness, número de gerações executadas, tempo de execução
- Detalhes das rotas otimizadas em formato JSON

**Arquivos de Dados:** O módulo `hospitais_sp.py` contém dados reais de 25+ hospitais do estado de São Paulo, incluindo coordenadas GPS, demanda de medicamentos e nível de prioridade.

### 7.2 Camada de Controle (Controller)

O componente `ExperimentManager` orquestra toda a lógica de negócio:

**Gerenciamento de Experimentos:** Cria, recupera, lista e remove experimentos do banco de dados.

**Execução Assíncrona:** Inicia execuções do Algoritmo Genético em threads separadas, permitindo que múltiplos experimentos rodem em background sem bloquear a aplicação.

**Integração de Cenários:** Fornece acesso aos cenários pré-definidos (small, medium, large, critical) e permite preview dos dados antes da execução.

**Persistência de Resultados:** Atualiza o banco de dados com os resultados assim que a execução termina, incluindo tratamento robusto de erros.

### 7.3 Camada de Visão (View)

O sistema oferece três interfaces distintas:

**API REST (FastAPI):** Fornece acesso programático via HTTP para integração com outras aplicações.

**Dashboard Web (Streamlit):** Interface gráfica moderna para gestão de experimentos, configuração de parâmetros e análise de resultados.

**Visualização em Tempo Real (Pygame):** Interface visual que mostra a evolução do algoritmo enquanto ele executa.

### 7.4 API REST

Implementada com FastAPI, a API oferece 10 endpoints para controle completo do sistema:

**POST /run:** Cria e inicia um novo experimento. Aceita um objeto JSON com mais de 25 parâmetros configuráveis, incluindo tamanho da população, taxas de crossover e mutação, métodos de seleção, configuração de veículos, cenário a ser usado e pesos da função de fitness.

**GET /experiments:** Lista os experimentos mais recentes. Aceita parâmetro de limite para controlar quantos registros retornar.

**GET /experiments/latest:** Retorna apenas o último experimento executado.

**GET /experiments/{id}:** Obtém detalhes completos de um experimento específico, incluindo configuração, resultados e rotas geradas.

**DELETE /experiments/all:** Remove todos os experimentos do histórico (usado para limpeza).

**DELETE /experiments/failed:** Remove apenas experimentos que falharam durante a execução.

**DELETE /experiments/{id}:** Remove um experimento específico por ID.

**GET /scenarios/{name}:** Retorna preview dos pontos de um cenário (small, medium, large, critical) antes de executá-lo.

**GET /config/defaults:** Retorna a configuração padrão do sistema com todos os parâmetros.

**GET /config/options:** Lista todas as opções disponíveis para cada campo configurável (métodos de seleção, crossover, mutação, etc).

A API usa validação automática com Pydantic, garantindo que todos os parâmetros estejam dentro de faixas válidas. As execuções ocorrem em background através do sistema de BackgroundTasks do FastAPI, permitindo que a API responda imediatamente sem esperar a conclusão do experimento.

### 7.5 Documentação OpenAPI/Swagger

O projeto inclui documentação completa da API em formato OpenAPI 3.0, disponível tanto de forma dinâmica quanto estática.

**Documentação Dinâmica (com API rodando):**

Com a API executando (`uvicorn src.api.main:app`), acesse:

- **Swagger UI:** http://localhost:8000/docs - Interface interativa completa com teste de endpoints
- **ReDoc:** http://localhost:8000/redoc - Documentação em formato de três painéis

**Documentação Estática:**

O projeto inclui documentação gerada estaticamente na pasta `docs/`:

```bash
# Gerar documentação estática
python generate_docs.py
```

Arquivos gerados em `docs/`:
- **index.html:** Página inicial com links para toda documentação
- **swagger.html:** Swagger UI standalone (funciona offline)
- **redoc.html:** ReDoc standalone (funciona offline)
- **openapi.json:** Schema OpenAPI 3.0 completo

**Visualizando documentação offline:**

```bash
# Método 1: Abrir diretamente no navegador
open docs/index.html  # macOS
xdg-open docs/index.html  # Linux
start docs/index.html  # Windows

# Método 2: Servidor HTTP local
python -m http.server --directory docs 8080
# Acesse: http://localhost:8080
```

**Características da Documentação:**

- **Schemas Completos:** Todos os modelos de request/response documentados com Pydantic
- **Exemplos Práticos:** Cada endpoint inclui exemplos de uso
- **Validações Detalhadas:** Ranges válidos para cada parâmetro
- **Tags Organizadas:** Endpoints agrupados em: experiments, scenarios, configuration, health
- **Descrições Técnicas:** Explicações detalhadas do funcionamento de cada operação
- **Tipos de Resposta:** Documentação de todos os códigos HTTP retornados (200, 404, 422, 500)

**Integrando com outras ferramentas:**

O arquivo `openapi.json` pode ser importado em ferramentas como:
- **Postman:** Importar coleção a partir do schema OpenAPI
- **Insomnia:** Criar workspace a partir do schema
- **Swagger Codegen:** Gerar clientes em várias linguagens
- **API Testing Tools:** Ferramentas de teste automatizado de APIs

## 8. Interfaces e Visualizações

O sistema oferece três formas distintas de interação, cada uma adequada a um propósito específico.

### 8.1 Interface Web (Streamlit)

A interface web fornece controle completo do sistema através do navegador. Ela está dividida em várias páginas:

**Página Dashboard:**

Esta é a tela principal do sistema. Ao acessar, você vê três métricas principais no topo: total de experimentos executados, taxa de sucesso (percentual de experimentos concluídos sem erros) e melhor fitness alcançado em todos os experimentos.

Logo abaixo há um sistema de filtros que permite selecionar quais tipos de experimentos você quer visualizar. Os experimentos são classificados por tipo de função de fitness utilizada (Multiobjetivo, Distância Pura, Baseado em Penalidades, ou Consciente de Prioridade).

A seção principal mostra uma tabela com todos os experimentos executados. Para cada experimento, você vê:
- ID único do experimento
- Data e hora de criação (convertida para horário de Brasília)
- Status (pending, running, completed ou failed)
- Cenário utilizado (small, medium, large, critical)
- Número de veículos configurados
- Melhor fitness alcançado
- Número de gerações executadas
- Tempo total de execução em segundos

Você pode clicar em qualquer experimento para ver seus detalhes completos, incluindo a configuração exata usada e as rotas geradas.

No rodapé da página existem botões para limpar o histórico. "Limpar Falhados" remove apenas experimentos com erro, enquanto "Limpar Tudo" remove o histórico completo (com confirmação de segurança).

**Página Nova Execução:**

Esta página é um configurador completo para criar novos experimentos. A interface está organizada em seções expansíveis:

*Configuração de Cenário:* Aqui você escolhe qual conjunto de hospitais usar. "Small" usa cerca de 10 hospitais (ideal para testes rápidos), "Medium" usa cerca de 20 hospitais (padrão), "Large" usa todos os hospitais disponíveis (mais demorado), e "Critical" usa apenas hospitais com entregas críticas.

*Parâmetros do Algoritmo Genético:* Controla o comportamento central do algoritmo. Você define o tamanho da população (quantos indivíduos existem em cada geração), número máximo de gerações (quando parar se não houver melhoria), taxa de crossover (probabilidade de dois pais gerarem filhos) e taxa de mutação (probabilidade de um filho sofrer mutação).

*Métodos Genéticos:* Aqui você escolhe qual variante de cada operador usar. Pode selecionar entre os 8 métodos de seleção (como Tournament ou Roulette), os 8 operadores de crossover (como PMX ou Order Crossover) e os 8 operadores de mutação (como Inversion ou 2-opt). Cada método tem características próprias que afetam o desempenho.

*Configuração de Veículos:* Define as características da frota. Você especifica quantos veículos estão disponíveis, qual a capacidade de carga de cada um (em unidades), a velocidade média (km/h) e a autonomia máxima (distância em km antes de precisar retornar ao depósito).

*Pesos da Função de Fitness:* Controla a importância relativa de cada objetivo. Pesos maiores tornam aquele aspecto mais importante na avaliação. Você ajusta o peso da distância total, da penalidade de prioridade (quão importante é atender entregas críticas primeiro), da penalidade de capacidade e da penalidade de autonomia.

*Critérios de Parada:* Define quando o algoritmo deve parar além do número máximo de gerações. O limite de estagnação especifica quantas gerações sem melhoria são toleradas antes de encerrar.

Após configurar todos os parâmetros, você escolhe o modo de execução:

- "Executar com Visualização" abre uma janela Pygame mostrando a evolução em tempo real
- "Executar em Background" roda silenciosamente e salva os resultados no banco de dados

**Página Análise Detalhada:**

Mostra informações aprofundadas sobre os experimentos executados. Você pode selecionar um experimento específico e ver gráficos de evolução do fitness ao longo das gerações, comparação entre diferentes configurações, e análise estatística dos resultados.

**Página Gerador Logístico:**

Permite criar cenários customizados, adicionando ou removendo hospitais, ajustando prioridades e demandas. Útil para testar situações específicas.

**Página de Configurações:**

Permite ajustar configurações globais do sistema, como tema visual, timeout de requisições à API, e preferências de visualização.

### 8.2 Visualização em Tempo Real (Pygame)

A interface Pygame oferece uma visão completa da execução do algoritmo enquanto ele roda. A tela é dividida em três áreas principais:

**Painel de Visualização (lado esquerdo):**

Mostra um mapa geográfico simplificado com todos os hospitais e as rotas. O depósito aparece como um círculo vermelho maior. Cada hospital é representado por um círculo colorido de acordo com sua prioridade - vermelho para crítico, amarelo para urgente, verde para regular.

As rotas aparecem como linhas conectando os pontos. Cada veículo tem uma cor diferente para facilitar a identificação. À medida que o algoritmo evolui, você vê as rotas mudando de forma, cruzamentos sendo eliminados, e a solução melhorando visualmente.

Abaixo do mapa há uma legenda explicando as cores e símbolos utilizados.

**Painel de Gráficos (lado direito superior):**

Mostra dois gráficos em tempo real:

O primeiro gráfico exibe a evolução do fitness ao longo das gerações. A linha azul mostra o melhor fitness encontrado até o momento, enquanto a linha cinza mostra a média da população. Você pode observar como o algoritmo converge gradualmente para soluções melhores.

O segundo gráfico mostra a diversidade da população ao longo do tempo, medida pelo desvio padrão do fitness. Alta diversidade indica que a população tem soluções muito variadas, enquanto baixa diversidade sugere convergência.

**Painel de Estatísticas (lado direito inferior):**

Apresenta informações detalhadas sobre a melhor solução atual:

- Geração atual e progresso percentual
- Melhor fitness encontrado (quanto menor, melhor)
- Distância total percorrida por todos os veículos
- Número de rotas criadas
- Tempo decorrido desde o início
- Velocidade de processamento (gerações por segundo)

Para cada veículo, são listados:
- Número de paradas que ele faz
- Distância total percorrida
- Carga transportada
- Utilização percentual da capacidade

**Controles Interativos:**

Na parte inferior da tela há botões de controle:

- "Iniciar/Continuar": Começa ou resume a execução
- "Pausar": Pausa a execução para análise detalhada
- "Parar": Encerra completamente a execução
- "Salvar Resultado": Exporta a melhor solução encontrada
- "Ajustar Velocidade": Controla a velocidade de visualização

Você pode pausar a qualquer momento para examinar uma geração específica, aproximar o zoom no mapa para ver detalhes das rotas, ou ajustar parâmetros em tempo real.

### 8.3 Mapas Interativos (Folium)

Após a execução do algoritmo, o sistema gera um arquivo HTML com um mapa interativo baseado em mapas reais do OpenStreetMap. Este mapa pode ser aberto em qualquer navegador.

O mapa mostra:

**Localizações Reais:** Cada hospital aparece em sua posição geográfica exata no mapa de São Paulo. Você pode dar zoom, arrastar o mapa e ver as ruas e regiões reais.

**Rotas Otimizadas:** As rotas de cada veículo são desenhadas com cores diferentes. Você pode seguir visualmente o caminho que cada veículo percorre.

**Marcadores Interativos:** Clicando em qualquer hospital, um popup aparece mostrando:
- Nome do hospital
- Endereço
- Prioridade da entrega
- Demanda de medicamentos
- Qual veículo atenderá este ponto
- Ordem de visita na rota

**Legenda:** Uma legenda flutuante explica as cores das rotas e símbolos utilizados.

Este mapa é especialmente útil para apresentações e para verificar a viabilidade prática das rotas geradas, já que você pode comparar com o conhecimento local do tráfego e infraestrutura de São Paulo.

## 9. Instalação e Configuração

Este guia detalha todos os passos necessários para instalar e configurar o sistema em sua máquina.

### 9.1 Requisitos de Sistema

**Sistema Operacional:** O projeto funciona em Linux, macOS e Windows. Os exemplos de comandos a seguir assumem Linux/macOS, mas equivalentes Windows são fornecidos quando necessário.

**Python:** É necessário Python 3.8 ou superior. Recomenda-se Python 3.10 ou 3.11 para melhor compatibilidade. Você pode verificar sua versão com:

```bash
python --version
```

ou

```bash
python3 --version
```

**Espaço em Disco:** Reserve pelo menos 500 MB para o projeto, dependências e banco de dados de experimentos.

**Memória RAM:** Mínimo de 4 GB, recomendado 8 GB para executar experimentos maiores.

### 9.2 Obtenção do Código

Se o projeto está em um repositório Git:

```bash
git clone <url-do-repositorio>
cd projeto2_haversine
```

Se você recebeu um arquivo compactado:

```bash
unzip projeto2_haversine.zip
cd projeto2_haversine
```

ou

```bash
tar -xzf projeto2_haversine.tar.gz
cd projeto2_haversine
```

### 9.3 Ambiente Virtual

Criar um ambiente virtual é altamente recomendado para isolar as dependências do projeto. Isso evita conflitos com outros projetos Python em seu sistema.

**No Linux ou macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

Após executar o segundo comando, você verá `(venv)` no início do seu prompt, indicando que o ambiente virtual está ativo.

**No Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

Para desativar o ambiente virtual quando terminar de trabalhar:

```bash
deactivate
```

### 9.4 Instalação de Dependências

Com o ambiente virtual ativado, instale todas as dependências do projeto:

```bash
pip install -r requirements.txt
```

Este comando instalará:

- **numpy**: Computação numérica e arrays
- **matplotlib**: Geração de gráficos e visualizações estáticas
- **pygame**: Interface gráfica em tempo real
- **folium**: Geração de mapas interativos
- **fastapi**: Framework para API REST
- **uvicorn**: Servidor ASGI para rodar a API
- **sqlalchemy**: ORM para persistência de dados
- **pydantic**: Validação de dados
- **streamlit**: Framework para interface web
- **pandas**: Manipulação de dados tabulares
- **pytest**: Framework de testes
- **requests**: Cliente HTTP para requisições à API

A instalação pode levar alguns minutos dependendo da sua conexão com a internet.

### 9.5 Verificação da Instalação

Para verificar se tudo foi instalado corretamente:

```bash
python -c "import numpy, matplotlib, pygame, folium, fastapi, streamlit; print('Todas as dependências OK')"
```

Se este comando executar sem erros, a instalação foi bem-sucedida.

### 9.6 Estrutura de Diretórios

Após a instalação, verifique se a estrutura de diretórios está completa:

```bash
ls -la
```

Você deve ver os diretórios: `src/`, `data/`, `tests/`, `assets/` e os arquivos `main.py`, `requirements.txt`, `README.md`, entre outros.

### 9.7 Execução com Docker

O projeto inclui configuração completa para execução em containers Docker, incluindo servidor Ollama com modelo Gemma3 para inferência local de LLM.

**Pré-requisitos Docker:**

- Docker Engine 20.10+
- Docker Compose V2
- (Opcional) NVIDIA Docker para GPU support

**Quick Start com Docker:**

```bash
docker-compose -f docker/docker-compose.cpu.yml up -d --build
```

**Serviços disponíveis:**

Após iniciar os containers:

- **API FastAPI**: http://localhost:8000
  - Documentação: http://localhost:8000/docs
- **Web Dashboard**: http://localhost:8501
- **Ollama Server**: http://localhost:11434

**Testando Ollama com Gemma3:**

```bash
# Verificar modelos disponíveis
curl http://localhost:11434/api/tags

# Fazer pergunta ao Gemma3
curl http://localhost:11434/api/generate -d '{
  "model": "gemma2:latest",
  "prompt": "Explain genetic algorithms briefly",
  "stream": false
}'
```

**Gerenciamento dos containers:**

```bash
# Ver logs
docker-compose -f docker/docker-compose.yml logs -f

# Parar serviços
docker-compose -f docker/docker-compose.yml down

# Parar e remover volumes
docker-compose -f docker/docker-compose.yml down -v

# Ver status
docker-compose -f docker/docker-compose.yml ps
```

**Arquivos Docker:**

Todos os arquivos de configuração Docker estão em `docker/`:

- `Dockerfile` - Imagem principal (API + Web)
- `Dockerfile.ollama` - Imagem Ollama com Gemma3
- `docker-compose.yml` - Orquestração com GPU
- `docker-compose.cpu.yml` - Orquestração sem GPU
- `entrypoint.sh` - Script de inicialização
- `ollama-entrypoint.sh` - Script Ollama
- `README.md` - Documentação completa Docker

**Publicando no Docker Hub:**

```bash
# Build com tag
docker build -t seu-usuario/ga-vrp-app:2.0.0 -f docker/Dockerfile .

# Login
docker login

# Push
docker push seu-usuario/ga-vrp-app:2.0.0
```

**Notas importantes:**

- Primeiro start pode demorar: Gemma3 (~2GB) será baixado automaticamente
- Modelos Ollama ficam persistidos em volume Docker
- Banco SQLite é compartilhado entre API e Web
- Para mais detalhes, consulte `docker/README.md`

## 10. Guia Completo de Execução

Esta seção detalha os modos de execução disponíveis: Docker, API REST e Interface Web.

### 10.1 Executando a API REST

Para disponibilizar o sistema como serviço web:

**Inicie o servidor API:**

```bash
uvicorn src.api.main:app --reload --port 8000
```

**Parâmetros explicados:**

- `src.api.main:app`: Caminho para a aplicação FastAPI
- `--reload`: Reinicia automaticamente quando o código é modificado (útil para desenvolvimento)
- `--port 8000`: Porta onde o servidor vai escutar

**O que você verá:**

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Acessando a documentação:**

Abra seu navegador e acesse:

- Documentação Swagger UI: http://localhost:8000/docs
- Documentação ReDoc: http://localhost:8000/redoc

Na interface Swagger, você pode testar todos os endpoints diretamente do navegador.

**Criando um experimento via API:**

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "population_size": 80,
    "max_generations": 150,
    "scenario": "medium",
    "selection_method": "tournament",
    "crossover_method": "order_crossover",
    "mutation_method": "inversion"
  }'
```

**Resposta esperada:**

```json
{
  "id": 1,
  "status": "pending",
  "message": "Experimento iniciado."
}
```

**Consultando o experimento:**

```bash
curl http://localhost:8000/experiments/1
```

**Listando todos os experimentos:**

```bash
curl http://localhost:8000/experiments
```

**Removendo experimentos falhados:**

```bash
curl -X DELETE http://localhost:8000/experiments/failed
```

### 10.2 Executando a Interface Web

Para iniciar o dashboard web Streamlit:

```bash
streamlit run src/web/app.py
```

**O que você verá no terminal:**

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.100:8501
```

**Acesse:** http://localhost:8501

**Primeira vez acessando:**

1. Você verá o logo "Saudelog" no topo
2. A navegação mostra: Dashboard, Nova Execução, Análise Detalhada, Gerador Logístico, Configurações
3. Se nenhum experimento foi executado ainda, o Dashboard estará vazio
4. Clique em "Nova Execução" para criar seu primeiro experimento

**Criando um experimento pela interface web:**

1. Vá para "Nova Execução"
2. Escolha o cenário "small" (mais rápido para testar)
3. Mantenha os parâmetros padrão ou ajuste conforme desejar
4. Clique em "Executar em Background"
5. Você verá uma mensagem de confirmação
6. Volte para o Dashboard e atualize a página
7. O experimento aparecerá na tabela

**Executando com visualização:**

1. Configure os parâmetros
2. Clique em "Executar com Visualização"
3. Uma janela Pygame será aberta automaticamente
4. Acompanhe a execução em tempo real

### 10.3 Workflow Recomendado

Para uma experiência completa e profissional, execute o sistema em modo completo:

**Terminal 1 - API:**

```bash
# Ative o ambiente virtual
source venv/bin/activate

# Inicie a API
uvicorn src.api.main:app --reload --port 8000
```

Deixe este terminal rodando.

**Terminal 2 - Interface Web:**

Abra um novo terminal na mesma pasta do projeto.

```bash
# Ative o ambiente virtual (no novo terminal)
source venv/bin/activate

# Inicie a interface web
streamlit run src/web/app.py
```

Deixe este terminal rodando também.

**Navegador:**

1. Abra uma aba em: http://localhost:8501 (Interface Web)
2. Abra outra aba em: http://localhost:8000/docs (Documentação da API)

**Usando o sistema:**

1. Na interface web, configure um experimento
2. Execute em background ou com visualização
3. Acompanhe o progresso
4. Consulte resultados no Dashboard
5. Se quiser, use a API diretamente para automação

**Para parar tudo:**

- Em cada terminal, pressione `Ctrl+C`
- Desative o ambiente virtual com `deactivate`

### 10.4 Cenários Disponíveis

O sistema vem com quatro cenários pré-configurados:

**Small (pequeno):**
- Aproximadamente 10 hospitais
- 2 veículos
- Tempo de execução: 1-2 minutos
- Ideal para: Testes rápidos, aprendizado, debug

**Medium (médio):**
- Aproximadamente 20 hospitais
- 3 veículos
- Tempo de execução: 3-5 minutos
- Ideal para: Demonstrações, experimentos padrão

**Large (grande):**
- Todos os hospitais disponíveis (25+)
- 4-5 veículos
- Tempo de execução: 10-20 minutos
- Ideal para: Análise completa, benchmarking

**Critical (crítico):**
- Apenas hospitais com entregas críticas
- 2-3 veículos
- Tempo de execução: 2-4 minutos
- Ideal para: Situações de emergência, priorização máxima

**Especificando o cenário:**

Via API:
```json
{
  "scenario": "critical"
}
```

Via interface web: Selecione no dropdown "Configuração de Cenário"

## 11. Testes Automatizados

O projeto inclui uma suite completa de testes para garantir qualidade e confiabilidade.

### 11.1 Organização dos Testes

Os testes estão organizados em 8 arquivos, cada um focando em uma área específica:

**test_ga_core.py:** Testa o núcleo do algoritmo genético
- Criação de cromossomos
- Validação de permutações
- Construção de rotas
- Gerenciamento de veículos
- Divisão correta quando restrições são violadas

**test_ga_operators.py:** Testa todos os 24 operadores genéticos
- Cada operador de seleção (8 testes)
- Cada operador de crossover (8 testes)
- Cada operador de mutação (8 testes)
- Validação de que permutações permanecem válidas após operações

**test_ga_fitness.py:** Testa a função de fitness
- Cálculo correto de distâncias
- Aplicação de penalidades
- Função multi-objetivo
- Casos extremos

**test_ga_integration.py:** Testes de integração completa
- Execução ponta a ponta do algoritmo
- Convergência
- Melhoria do fitness ao longo de gerações
- Diferentes configurações

**test_api.py:** Testa os endpoints da API
- Validação de schemas com Pydantic
- Respostas HTTP corretas
- Tratamento de erros
- Serialização JSON

**test_api_execution.py:** Testa execuções via API
- Criação de experimentos
- Execução em background
- Atualização de status
- Persistência de resultados

**test_controller.py:** Testa o ExperimentManager
- CRUD de experimentos
- Execução assíncrona
- Gerenciamento de cenários
- Tratamento de exceções

**test_database.py:** Testa a camada de persistência
- Modelos SQLAlchemy
- Operações de banco de dados
- Integridade de dados
- Transações

### 11.2 Executando os Testes

**Todos os testes:**

```bash
pytest tests/
```

**Com saída detalhada:**

```bash
pytest tests/ -v
```

**Saída típica:**

```
tests/test_ga_core.py::test_chromosome_creation PASSED
tests/test_ga_core.py::test_route_division PASSED
tests/test_ga_operators.py::test_tournament_selection PASSED
tests/test_ga_operators.py::test_pmx_crossover PASSED
...
================================ 67 passed in 12.34s ================================
```

**Teste específico:**

```bash
pytest tests/test_ga_operators.py -v
```

**Teste individual:**

```bash
pytest tests/test_ga_operators.py::test_tournament_selection -v
```

**Com cobertura de código:**

Primeiro, instale a extensão:

```bash
pip install pytest-cov
```

Execute com relatório de cobertura:

```bash
pytest tests/ --cov=src --cov-report=html
```

Isso gera um relatório HTML em `htmlcov/`. Abra-o com:

```bash
# Linux
xdg-open htmlcov/index.html

# macOS
open htmlcov/index.html

# Windows
start htmlcov/index.html
```

**Testes em modo watch (re-executa quando código muda):**

Instale pytest-watch:

```bash
pip install pytest-watch
```

Execute:

```bash
ptw tests/
```

### 11.3 Interpretando Resultados

**PASSED:** Teste executado com sucesso, comportamento esperado confirmado.

**FAILED:** Teste falhou. O pytest mostrará:
- Qual asserção falhou
- Valores esperados vs obtidos
- Traceback completo

**SKIPPED:** Teste foi pulado (geralmente por estar marcado com @pytest.mark.skip).

**ERROR:** Erro durante a execução do teste (não no código testado, mas no próprio teste).

**Exemplo de falha:**

```
FAILED tests/test_ga_operators.py::test_pmx_crossover - AssertionError: assert [1, 2, 3] == [1, 3, 2]
```

Isso indica que o teste esperava `[1, 3, 2]` mas obteve `[1, 2, 3]`.

### 11.4 Escrevendo Novos Testes

Se você modificar o código, adicione testes correspondentes. Exemplo básico:

```python
def test_nova_funcionalidade():
    # Arrange (preparar)
    entrada = preparar_dados()

    # Act (executar)
    resultado = minha_funcao(entrada)

    # Assert (verificar)
    assert resultado == valor_esperado
```

Execute o novo teste:

```bash
pytest tests/test_novo_modulo.py::test_nova_funcionalidade -v
```

## 12. Resultados dos Experimentos

Esta seção apresenta um resumo dos resultados obtidos através de 396 experimentos executados com diferentes configurações de operadores genéticos e tipos de fitness.

> **Análise completa disponível em:** [`docs/conclusao.md`](docs/conclusao.md)

### 12.1 Resumo Executivo

| Métrica | Valor |
|---------|-------|
| Total de Experimentos | 396 |
| Melhor Eficiência | 43.1% (weighted_multi + medium) |
| Pior Eficiência | 4.0% (priority_aware + medium) |
| Eficiência Média Geral | 14.7% |

### 12.2 Eficiência por Tipo de Fitness

| Tipo de Fitness | Eficiência Média | Melhor Caso | Recomendação |
|-----------------|------------------|-------------|--------------|
| Weighted Multi-Objective | 28.4% | 43.1% | Múltiplos objetivos |
| Penalty Based | 16.2% | 22.9% | Muitas restrições |
| Priority Aware | 7.3% | 11.1% | Entregas urgentes |
| Distance Only | 7.1% | 12.0% | Simplicidade |

### 12.3 Melhores Operadores por Tipo de Fitness

| Fitness Type | Seleção | Crossover | Mutação |
|--------------|---------|-----------|---------|
| distance_only | Tournament | Order Crossover | 2-opt |
| priority_aware | Boltzmann | Order-Based | Inversion |
| weighted_multi | Boltzmann | Order-Based | Inversion |
| penalty_based | Rank | Order Crossover | Insert |

### 12.4 Economia Estimada (Cenário Large - 80 hospitais)

Considerando as premissas de combustível a R$ 7,00/litro, consumo de 10 km/litro e custo de motorista a R$ 25,00/hora:

| Componente | Economia/Dia | Economia/Mês | Economia/Ano |
|------------|--------------|--------------|--------------|
| Combustível | R$ 179,71 | R$ 3.953,62 | R$ 47.443,44 |
| Mão-de-obra | R$ 160,50 | R$ 3.531,00 | R$ 42.372,00 |
| **TOTAL** | **R$ 340,21** | **R$ 7.484,62** | **R$ 89.815,44** |

### 12.5 Recomendações por Caso de Uso

| Caso de Uso | Fitness Type | Configuração | Eficiência Esperada |
|-------------|--------------|--------------|---------------------|
| Logística simples | distance_only | Tournament + Order + 2-opt | 4-12% |
| Hospital/Urgência | priority_aware | Boltzmann + Order-Based + Inversion | 4-11% |
| Múltiplos objetivos | weighted_multi | Boltzmann + Order-Based + Inversion | 18-43% |
| Muitas restrições | penalty_based | Rank + Order + Insert | 9-23% |

Para análise detalhada incluindo interpretação dos ganhos em termos de tempo, dinheiro, segurança e qualidade de serviço, consulte o documento [`docs/conclusao.md`](docs/conclusao.md).

## 13. Conclusão

Este projeto demonstra a aplicação de Algoritmos Genéticos em um problema real de otimização logística, com complexidade comparável a desafios encontrados em operações empresariais. A solução vai além de uma implementação acadêmica básica, oferecendo uma arquitetura profissional completa com API REST, persistência de dados, interface web moderna e testes automatizados.

Os experimentos realizados (396 execuções com diferentes configurações) demonstraram ganhos de eficiência entre **4% e 43%**, com potencial de economia anual superior a **R$ 89.000** em operações de grande porte. A análise completa está documentada em [`docs/conclusao.md`](docs/conclusao.md).

**Principais Realizações:**

**Arquitetura de Produção:** O sistema implementa separação clara de responsabilidades através do padrão MVC, com camadas de modelo, visão e controle bem definidas. A API REST permite integração com outros sistemas, enquanto a interface web oferece usabilidade para usuários não técnicos.

**Implementação Completa de Operadores:** Os 24 operadores genéticos implementados (8 de seleção, 8 de crossover e 8 de mutação) fornecem uma base sólida para análise comparativa e pesquisa. Cada operador foi implementado seguindo a literatura acadêmica correspondente, com validações que garantem a integridade das permutações.

**Quatro Estratégias de Fitness:** O sistema oferece quatro tipos distintos de função de fitness (Distance Only, Priority Aware, Weighted Multi-Objective e Penalty Based), permitindo adaptar a otimização a diferentes cenários operacionais. A estratégia multi-objetivo demonstrou os maiores ganhos (até 43%), enquanto a estratégia baseada em penalidades garante 100% de viabilidade das rotas.

**Visualizações Profissionais:** As três formas de visualização atendem diferentes necessidades - mapas interativos HTML para apresentações e análise geográfica, interface Pygame para acompanhamento da evolução em tempo real, e dashboard web Streamlit para gestão executiva e análise de resultados.

**Dados e Validação Reais:** O uso de coordenadas GPS reais de hospitais de São Paulo, combinado com o cálculo de distâncias geodésicas via fórmula de Haversine, garante que os resultados sejam aplicáveis ao mundo real. As prioridades de entrega refletem decisões logísticas reais onde medicamentos críticos não podem esperar.

**Qualidade e Manutenibilidade:** A suite de testes automatizados com 8 arquivos de teste cobrindo desde unidades individuais até integração completa garante que modificações futuras não quebrem funcionalidades existentes. A documentação detalhada facilita compreensão e manutenção.

**Aplicabilidade Prática:**

O sistema pode ser utilizado em cenários reais de logística hospitalar. A função de fitness multi-objetivo permite balancear diferentes prioridades conforme as necessidades específicas de cada situação. Em uma emergência, pode-se aumentar drasticamente o peso de prioridade para garantir que medicamentos críticos sejam entregues primeiro. Em operações regulares, pode-se equilibrar melhor entre distância e prioridade.

A capacidade de executar experimentos em background via API permite automação completa. É possível, por exemplo, executar otimizações automaticamente toda noite para planejar as rotas do dia seguinte, ou executar múltiplas configurações em paralelo para encontrar a melhor para uma situação específica.

**Contribuição Acadêmica:**

Para o contexto do FIAP Tech Challenge Fase 2, o projeto demonstra:

- Domínio de meta-heurísticas aplicadas a problemas de otimização combinatória
- Capacidade de implementar arquiteturas de software modernas e escaláveis
- Conhecimento de boas práticas de engenharia de software (testes, modularização, documentação)
- Habilidade de comunicar soluções técnicas através de visualizações e interfaces intuitivas
- Aplicação prática de conhecimentos teóricos em problemas de relevância social

O código está estruturado para extensão futura. Novos operadores genéticos podem ser adicionados facilmente seguindo os padrões estabelecidos. Novos tipos de restrições (janelas de tempo estritas, múltiplos depósitos, cargas especiais) podem ser incorporados na função de fitness. A arquitetura permite que o sistema evolua conforme necessidades futuras.

Com mais de 14.000 linhas de código implementadas e testadas, o projeto representa um trabalho significativo que combina teoria de algoritmos evolutivos, engenharia de software e aplicação prática em logística de saúde.

## 14. Referências

[1] Toth, P., & Vigo, D. (Eds.). (2014). Vehicle routing: problems, methods, and applications. Society for Industrial and Applied Mathematics.

[2] Goldberg, D. E. (1989). Genetic Algorithms in Search, Optimization, and Machine Learning. Addison-Wesley.

[3] Eiben, A. E., & Smith, J. E. (2015). Introduction to Evolutionary Computing. Springer.

[4] Laporte, G. (2009). Fifty years of vehicle routing. Transportation Science, 43(4), 408-416.

[5] Bräysy, O., & Gendreau, M. (2005). Vehicle routing problem with time windows, Part I: Route construction and local search algorithms. Transportation Science, 39(1), 104-118.

[6] Potvin, J. Y. (1996). Genetic algorithms for the traveling salesman problem. Annals of Operations Research, 63(3), 337-370.

[7] Baker, B. M., & Ayechew, M. A. (2003). A genetic algorithm for the vehicle routing problem. Computers & Operations Research, 30(5), 787-800.

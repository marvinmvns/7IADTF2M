# Projeto 2: Otimização de Rotas para Distribuição de Medicamentos com Algoritmos Genéticos

> **FIAP Tech Challenge - Fase 2**
> Sistema completo de otimização de rotas usando Algoritmos Genéticos
> Arquitetura MVC • API REST • Interface Web • Testes Automatizados
> **~14.200 linhas de código** | **30 módulos Python** | **24 operadores genéticos**

---

## 📋 Índice

1. [Introdução](#1-introdução)
2. [O Problema de Roteamento de Veículos (VRP)](#2-o-problema-de-roteamento-de-veículos-vrp)
3. [Algoritmos Genéticos (AGs)](#3-algoritmos-genéticos-ags)
4. [Abordagens de Operadores Genéticos](#4-abordagens-de-operadores-genéticos)
5. [Estrutura do Código](#5-estrutura-do-código)
6. [Arquitetura Moderna e Camadas do Sistema](#6-arquitetura-moderna-e-camadas-do-sistema)
   - 6.1. [API REST com FastAPI](#61-api-rest-com-fastapi)
   - 6.2. [Banco de Dados e Persistência](#62-banco-de-dados-e-persistência)
   - 6.3. [Camada de Controle (Controller)](#63-camada-de-controle-controller)
   - 6.4. [Interface Web com Streamlit](#64-interface-web-com-streamlit)
7. [Visualização](#7-visualização)
8. [Testes Automatizados](#8-testes-automatizados)
9. [Como Executar o Projeto](#9-como-executar-o-projeto)
10. [Conclusão](#10-conclusão)
11. [Referências](#11-referências)

---

## 1. Introdução

Este documento apresenta o desenvolvimento do Projeto 2 do Tech Challenge, focado na otimização de rotas para a distribuição de medicamentos e insumos hospitalares no estado de São Paulo. O problema, uma variação do Problema do Caixeiro Viajante com Múltiplos Veículos (Multiple Vehicle Routing Problem - mVRP), é resolvido utilizando **Algoritmos Genéticos (AGs)**, uma meta-heurística inspirada na teoria da evolução de Charles Darwin.

A solução proposta visa não apenas minimizar a distância total percorrida, mas também considerar restrições do mundo real, como capacidade dos veículos, autonomia, janelas de tempo e, crucialmente, a **prioridade das entregas** (medicamentos críticos, urgentes e regulares). O projeto foi desenvolvido em Python, com visualizações interativas utilizando Pygame e Folium para a plotagem em mapas reais.

## 2. O Problema de Roteamento de Veículos (VRP)

O Problema de Roteamento de Veículos (Vehicle Routing Problem - VRP) é um problema de otimização combinatória bem conhecido na área de pesquisa operacional e logística. O objetivo é encontrar um conjunto de rotas ótimas para uma frota de veículos que parte de um depósito central para entregar bens a um conjunto de clientes, minimizando custos (distância, tempo, etc.) e respeitando um conjunto de restrições [1].

Neste projeto, lidamos com as seguintes características:

- **Múltiplos Veículos (mVRP):** Uma frota de veículos está disponível para realizar as entregas.
- **Capacidade (CVRP):** Cada veículo possui uma capacidade limitada de carga.
- **Autonomia:** Cada veículo tem uma distância máxima que pode percorrer.
- **Prioridades:** As entregas possuem diferentes níveis de urgência, influenciando a ordem e o tempo de entrega.

## 3. Algoritmos Genéticos (AGs)

Algoritmos Genéticos são uma classe de algoritmos de busca e otimização que mimetizam o processo de seleção natural. Eles operam sobre uma **população** de soluções candidatas (chamadas de **cromossomos**), evoluindo-as ao longo de várias **gerações** para encontrar soluções cada vez melhores para um problema [2].

O fluxo de um Algoritmo Genético é o seguinte:

1.  **Inicialização:** Criação de uma população inicial de soluções aleatórias (ou parcialmente heurísticas).
2.  **Avaliação (Fitness):** Cada solução é avaliada por uma **função de fitness**, que mede sua qualidade.
3.  **Seleção:** Indivíduos mais aptos (com melhor fitness) são selecionados como pais para a próxima geração.
4.  **Crossover (Recombinação):** Os pais trocam informações genéticas para criar novos descendentes (filhos).
5.  **Mutação:** Pequenas alterações aleatórias são introduzidas nos filhos para manter a diversidade genética.
6.  **Substituição:** A nova geração substitui a antiga (total ou parcialmente).
7.  **Critério de Parada:** O processo se repete até que um critério de parada seja atingido (número de gerações, convergência, etc.).

### 3.1. Representação do Cromossomo

Para o VRP, uma representação eficaz é crucial. Neste projeto, um cromossomo é uma **permutação de todos os pontos de entrega**. A divisão das rotas entre os veículos é feita dinamicamente durante a avaliação do fitness, inserindo "quebras" na permutação quando uma restrição (capacidade ou autonomia) é violada.

> **Exemplo:** Se temos 8 hospitais (1 a 8) e 2 veículos, um cromossomo pode ser `[3, 5, 1, 8, 2, 4, 6, 7]`. Durante a avaliação, isso pode ser dividido em:
> - **Rota 1 (Veículo 1):** Depósito -> 3 -> 5 -> 1 -> Depósito
> - **Rota 2 (Veículo 2):** Depósito -> 8 -> 2 -> 4 -> 6 -> 7 -> Depósito

### 3.2. Função de Fitness

A função de fitness é o coração do AG. Ela deve quantificar a "qualidade" de uma solução. Para este projeto, foi implementada uma função de fitness multi-objetivo ponderada:

`Fitness = w1 * Distância + w2 * PenalidadePrioridade + w3 * PenalidadeCapacidade + w4 * PenalidadeAutonomia`

- **Distância:** A soma das distâncias de todas as rotas.
- **Penalidade de Prioridade:** Penaliza soluções onde entregas críticas (prioridade 1) não são feitas no início das rotas.
- **Penalidade de Capacidade/Autonomia:** Penaliza rotas que excedem a capacidade ou a autonomia do veículo.

## 4. Abordagens de Operadores Genéticos

Uma parte central deste estudo acadêmico foi a implementação e comparação de múltiplos operadores genéticos. A combinação correta de operadores de seleção, crossover e mutação é fundamental para o desempenho do AG.

### 4.1. Operadores de Seleção

O operador de seleção escolhe quais indivíduos da população atual se tornarão pais. Foram implementados **8 métodos de seleção**:

| Método de Seleção                  | Descrição                                                                                             |
| --------------------------------- | ----------------------------------------------------------------------------------------------------- |
| **Seleção por Roleta**            | A probabilidade de seleção é proporcional ao fitness do indivíduo.                                     |
| **Seleção por Torneio**           | Seleciona *k* indivíduos aleatoriamente e escolhe o melhor deles. Simples e eficaz.                   |
| **Seleção por Ranking**           | A probabilidade de seleção é baseada no ranking do indivíduo, não no seu fitness absoluto.            |
| **Seleção por Truncamento**       | Apenas os *T%* melhores indivíduos são selecionados para reprodução.                                   |
| **Seleção Elitista**              | Garante que os melhores indivíduos passem diretamente para a próxima geração.                          |
| **Amostragem Universal Estocástica (SUS)** | Variante da roleta com menor viés, usando múltiplos ponteiros igualmente espaçados.                 |
| **Seleção de Boltzmann**          | Usa uma "temperatura" que controla a pressão seletiva, diminuindo ao longo do tempo.                |
| **Seleção de Estado Estacionário** | Apenas uma pequena fração da população é substituída a cada geração.                                  |

### 4.2. Operadores de Crossover

O crossover combina o material genético de dois pais para criar filhos. Para problemas de permutação como o VRP, operadores especiais são necessários. Foram implementados **8 operadores de crossover**:

| Operador de Crossover                     | Descrição                                                                                                |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| **Partially Mapped Crossover (PMX)**      | Mapeia um segmento de um pai para o outro, resolvendo conflitos. Preserva posição e ordem.           |
| **Order Crossover (OX)**                  | Copia um segmento de um pai e preenche o restante com genes do outro pai na ordem em que aparecem.      |
| **Cycle Crossover (CX)**                  | Identifica ciclos de posições entre os pais e os alterna para criar os filhos. Preserva posição.     |
| **Alternating Edges Crossover (AEX)**     | Constrói o filho alternando arestas (adjacências) dos dois pais.                                      |
| **Edge Recombination Crossover (ERX)**    | Constrói uma tabela de arestas dos pais e a utiliza para criar um filho que preserva muitas arestas. |
| **Sequential Constructive Crossover (SCX)** | Constrói o filho de forma sequencial, escolhendo o próximo gene com base em critérios de distância. |
| **Order-Based Crossover (OX2)**           | Variante do OX que seleciona posições aleatórias em vez de um segmento contínuo.                   |
| **Position-Based Crossover (POS)**        | Preserva as posições dos genes selecionados de um pai e preenche o resto com genes do outro.        |

### 4.3. Operadores de Mutação

A mutação introduz novas informações genéticas, ajudando a evitar a convergência prematura. Foram implementados **8 operadores de mutação**:

| Operador de Mutação                   | Descrição                                                                                             |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| **Swap Mutation**                     | Troca dois genes de posição.                                                                          |
| **Inversion Mutation**                | Inverte um segmento do cromossomo. Equivalente a uma operação 2-opt.                                |
| **Scramble Mutation**                 | Embaralha aleatoriamente os genes dentro de um segmento.                                              |
| **Insert Mutation**                   | Move um gene de uma posição para outra.                                                               |
| **Displacement Mutation**             | Move um segmento inteiro para outra posição.                                                          |
| **2-opt Mutation**                    | Remove duas arestas e reconecta os segmentos de forma a descruzar a rota. Clássico no TSP.         |
| **3-opt Mutation**                    | Versão mais poderosa do 2-opt, que remove e reconecta três arestas.                                |
| **Reverse Sequence Mutation (RSM)**   | Variante da inversão com seleção de segmento baseada em tamanho aleatório.                          |

## 5. Estrutura do Código

O projeto foi estruturado de forma modular seguindo arquitetura **MVC (Model-View-Controller)**, separando as responsabilidades em diferentes camadas:

```
projeto2_haversine/
├── data/
│   ├── hospitais_sp.py         # Módulo com dados dos hospitais e cenários
│   ├── hospitais_sp.json       # Dados em formato JSON (19KB)
│   └── experiments.db          # Banco de dados SQLite de experimentos
├── src/
│   ├── genetic_algorithm/      # Núcleo do Algoritmo Genético (4.085 linhas)
│   │   ├── __init__.py
│   │   ├── chromosome.py       # Representação do cromossomo e rotas (494 linhas)
│   │   ├── population.py       # Gerenciamento da população (309 linhas)
│   │   ├── selection.py        # 8 métodos de seleção (632 linhas)
│   │   ├── crossover.py        # 8 operadores de crossover (953 linhas)
│   │   ├── mutation.py         # 8 operadores de mutação (471 linhas)
│   │   ├── fitness.py          # Função de fitness multi-objetivo (617 linhas)
│   │   └── genetic_algorithm.py # Orquestrador principal do AG (579 linhas)
│   ├── visualization/          # Camada de Visualização (3.211 linhas)
│   │   ├── __init__.py
│   │   ├── route_visualizer.py      # Mapas com Folium e Matplotlib (606 linhas)
│   │   ├── evolution_visualizer.py  # Visualização Pygame em tempo real (565 linhas)
│   │   └── interactive_viewer.py    # Interface interativa completa (2.017 linhas)
│   ├── api/                    # API REST com FastAPI (125 linhas)
│   │   └── main.py             # 10 endpoints RESTful
│   ├── controllers/            # Camada de Controle (260 linhas)
│   │   └── experiment_manager.py # Gerenciador de experimentos e execuções
│   ├── database/               # Camada de Persistência (47 linhas)
│   │   ├── database.py         # Configuração SQLAlchemy (22 linhas)
│   │   └── models.py           # Modelo ORM Experiment (25 linhas)
│   ├── web/                    # Interface Web com Streamlit
│   │   ├── app.py              # Dashboard executivo e configurador
│   │   ├── components/
│   │   │   └── styles.py       # Estilização CSS customizada
│   │   └── pages/              # Páginas adicionais (futuro)
│   └── utils/
│       ├── __init__.py
│       └── distance.py         # Cálculo de distância Haversine
├── tests/                      # Suite de Testes Automatizados (8 arquivos)
│   ├── test_ga_core.py         # Testes do núcleo do AG
│   ├── test_ga_operators.py    # Testes dos operadores genéticos
│   ├── test_ga_fitness.py      # Testes da função de fitness
│   ├── test_ga_integration.py  # Testes de integração completa
│   ├── test_api.py             # Testes dos endpoints da API
│   ├── test_api_execution.py   # Testes de execução via API
│   ├── test_controller.py      # Testes do ExperimentManager
│   └── test_database.py        # Testes da camada de persistência
├── assets/                     # Recursos gráficos
│   └── logo.png                # Logo do projeto (347KB)
├── main.py                     # Script principal para execução (16KB)
├── pytest.ini                  # Configuração do pytest
├── README.md                   # Este documento (documentação completa)
├── CLAUDE.md                   # Instruções para Claude Code
├── requirements.txt            # Dependências do projeto
└── .gitignore                  # Exclusões do Git

# Arquivos Gerados (não versionados)
├── mapa_rotas_hospitais_sp.html # Mapa interativo HTML gerado (101KB)
└── sql_app.db                  # Banco de dados SQLite da aplicação (12KB)
```

**Estatísticas do Projeto:**
- **Total de linhas de código:** ~14.200 linhas
- **Arquivos Python:** 30 módulos
- **Operadores genéticos:** 24 (8 seleção + 8 crossover + 8 mutação)
- **Endpoints API:** 10 endpoints RESTful
- **Testes automatizados:** 8 suites de teste
- **Tamanho total:** 2,1 MB

## 6. Arquitetura Moderna e Camadas do Sistema

O projeto evoluiu para uma **arquitetura de 3 camadas** completa, seguindo o padrão **MVC (Model-View-Controller)** com persistência de dados, API REST e interface web moderna.

### 6.1. API REST com FastAPI

A API fornece acesso programático ao sistema de otimização, permitindo automação de experimentos e integração com outras aplicações.

**Arquivo:** `src/api/main.py` (125 linhas)

**Endpoints Disponíveis:**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/run` | Inicia um novo experimento com configuração personalizada |
| `GET` | `/experiments` | Lista os experimentos mais recentes (limite configurável) |
| `GET` | `/experiments/latest` | Retorna o último experimento executado |
| `GET` | `/experiments/{id}` | Obtém detalhes completos de um experimento específico |
| `DELETE` | `/experiments/all` | Remove TODOS os experimentos do histórico |
| `DELETE` | `/experiments/failed` | Remove apenas experimentos com status "failed" |
| `DELETE` | `/experiments/{id}` | Remove um experimento específico por ID |
| `GET` | `/scenarios/{name}` | Retorna preview dos pontos de um cenário (small, medium, large, critical) |

**Parâmetros Configuráveis (POST /run):**

O endpoint `/run` aceita um objeto `ExperimentConfig` com 25+ parâmetros configuráveis via JSON:

```json
{
  "population_size": 100,
  "max_generations": 200,
  "crossover_rate": 0.9,
  "mutation_rate": 0.15,
  "selection_method": "tournament",
  "crossover_method": "order_crossover",
  "mutation_method": "inversion",
  "replacement_strategy": "elitist",
  "fitness_type": "weighted_multi_objective",
  "tournament_size": 3,
  "elite_size": 2,
  "truncation_threshold": 0.5,
  "boltzmann_temperature": 100.0,
  "steady_state_ratio": 0.2,
  "num_vehicles": 3,
  "vehicle_capacity": 100.0,
  "vehicle_speed": 40.0,
  "vehicle_max_distance": 200.0,
  "scenario": "large",
  "w_distance": 1.0,
  "w_priority": 10.0,
  "w_capacity": 100.0,
  "w_autonomy": 100.0,
  "w_window": 50.0,
  "stagnation_limit": 50,
  "heuristic_init_ratio": 0.2
}
```

**Validação com Pydantic:**
- Todos os parâmetros são validados automaticamente
- Restrições de intervalo (ex: `crossover_rate` entre 0.0 e 1.0)
- Validação de enums (métodos de seleção, crossover, mutação)
- Mensagens de erro claras e estruturadas

**Execução em Background:**
- Experimentos são executados em `BackgroundTasks` do FastAPI
- Não bloqueia a API durante execuções longas
- Status do experimento pode ser consultado via `GET /experiments/{id}`

**Exemplo de Uso:**

```bash
# Iniciar a API
uvicorn src.api.main:app --reload --port 8000

# Criar um novo experimento
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"population_size": 80, "max_generations": 150, "scenario": "medium"}'

# Listar experimentos
curl http://localhost:8000/experiments

# Ver detalhes de um experimento
curl http://localhost:8000/experiments/1
```

### 6.2. Banco de Dados e Persistência

O sistema utiliza **SQLAlchemy ORM** com **SQLite** para persistência de todos os experimentos e resultados.

**Arquivos:**
- `src/database/database.py` - Configuração do engine e sessões (22 linhas)
- `src/database/models.py` - Modelos ORM (25 linhas)

**Modelo Experiment:**

```python
class Experiment(Base):
    __tablename__ = "experiments"

    id: int                    # Chave primária
    created_at: datetime       # Timestamp de criação
    status: str                # pending | running | completed | failed
    config: JSON               # Configuração completa do experimento
    best_fitness: float        # Melhor fitness alcançado
    generations_run: int       # Número de gerações executadas
    execution_time: float      # Tempo total de execução (segundos)
    result_details: JSON       # Detalhes das rotas e solução
```

**Estados do Experimento:**
- **pending**: Experimento criado, aguardando execução
- **running**: Em execução no momento
- **completed**: Finalizado com sucesso
- **failed**: Erro durante a execução

**Banco de Dados:**
- Localização: `data/experiments.db` e `sql_app.db`
- Schema criado automaticamente na primeira execução
- Histórico completo de todas as execuções
- Resultados detalhados em formato JSON

**Benefícios:**
- Rastreabilidade completa de experimentos
- Comparação de configurações e resultados
- Reprodutibilidade científica
- Análise histórica de desempenho

### 6.3. Camada de Controle (Controller)

O **ExperimentManager** orquestra toda a lógica de negócio do sistema.

**Arquivo:** `src/controllers/experiment_manager.py` (260 linhas)

**Responsabilidades:**

1. **Gerenciamento de Experimentos:**
   - `create_experiment(config_dict)` - Cria novo registro no banco
   - `get_experiment(experiment_id)` - Recupera experimento por ID
   - `list_experiments(limit)` - Lista experimentos recentes
   - `delete_experiment(experiment_id)` - Remove experimento específico
   - `delete_all_experiments()` - Limpa todo o histórico
   - `delete_failed_experiments()` - Remove apenas falhados

2. **Execução do Algoritmo Genético:**
   - `run_experiment_background(experiment_id)` - Inicia execução em thread separada
   - `_run_process(experiment_id)` - Lógica principal de execução
   - Conversão de configuração JSON → GAConfig
   - Criação de delivery points a partir dos cenários
   - Configuração de veículos com parâmetros customizados

3. **Integração de Cenários:**
   - `get_scenario_data(scenario_name)` - Retorna dados do cenário
   - Suporte a 4 cenários: small, medium, large, critical
   - Preview de pontos antes da execução

4. **Persistência de Resultados:**
   - `update_experiment_result()` - Salva resultados após execução
   - `complete_experiment()` - Marca como completo e persiste
   - Tratamento de erros e status "failed"

**Integração:**
- Conecta API ↔ Banco de Dados ↔ Algoritmo Genético
- Threading para execuções assíncronas
- Tratamento robusto de exceções

### 6.4. Interface Web com Streamlit

Uma interface web moderna e intuitiva para gestão de experimentos e visualização de resultados.

**Arquivo:** `src/web/app.py`

**Funcionalidades:**

1. **Dashboard Executivo:**
   - Métricas globais (total de experimentos, taxa de sucesso, melhor fitness)
   - Histórico de execuções com KPIs
   - Gráficos de evolução temporal

2. **Configurador Intuitivo:**
   - Interface gráfica para ajustar todos os 25+ parâmetros
   - Sliders, selectboxes e inputs organizados por categoria
   - Validação em tempo real
   - Preview do cenário selecionado

3. **Controle de Execução:**
   - Botão para iniciar experimentos via API
   - Modo background (silencioso, salva no banco)
   - Modo interativo (abre visualização Pygame)
   - Acompanhamento de status em tempo real

4. **Análise Detalhada:**
   - Tabela de experimentos históricos
   - Comparação de configurações
   - Visualização de rotas otimizadas
   - Exportação de resultados

5. **Gestão de Histórico:**
   - Limpeza de experimentos falhados
   - Reset completo do histórico
   - Remoção individual de experimentos

**Recursos Visuais:**
- Logo customizada (assets/logo.png)
- Estilização CSS profissional
- Layout responsivo
- Navegação por abas

**Exemplo de Uso:**

```bash
# Iniciar interface web
streamlit run src/web/app.py

# Acesse no navegador: http://localhost:8501
```

## 7. Visualização

Para uma melhor compreensão dos resultados, foram implementadas três formas de visualização:

### 7.1. Mapas Interativos com Folium

Após a execução do algoritmo, um mapa interativo em HTML é gerado usando a biblioteca **Folium**, que se baseia no Leaflet.js. Este mapa mostra:

- A localização real dos hospitais e do depósito no mapa de São Paulo.
- As rotas otimizadas, com cores diferentes para cada veículo.
- Pop-ups interativos com detalhes de cada hospital e rota.
- Uma legenda clara para identificar os elementos.

![Mapa de Rotas](rotas_hospitais_sp.png)
*Figura 1: Exemplo de mapa de rotas gerado com Matplotlib (uma versão estática também é criada).*

### 7.2. Visualização em Tempo Real com Pygame

Para fins acadêmicos e de análise do comportamento do algoritmo, foi criada uma interface interativa com **Pygame**. Esta interface permite:

- Visualizar a evolução das rotas da melhor solução a cada geração.
- Acompanhar o gráfico de convergência do fitness (melhor e média da população).
- Iniciar, pausar e parar a execução do algoritmo.
- Analisar estatísticas detalhadas da solução em tempo real.

### 7.3. Interface Web e Dashboard (Streamlit)

Uma interface moderna foi desenvolvida para facilitar a gestão dos experimentos:

- **Dashboard Executivo:** Métricas globais, histórico de execuções e KPIs.
- **Configurador Intuitivo:** Interface gráfica para ajustar todos os parâmetros do AG (taxas, métodos, população).
- **Integração Visual:** Botão para lançar a visualização Pygame diretamente do navegador.
- **Modo Background:** Execute experimentos silenciosamente via API e salve os resultados no banco de dados.
- **Gestão de Histórico:** Limpeza de experimentos, visualização de resultados, comparação de configurações.

## 8. Testes Automatizados

O projeto conta com uma suite completa de testes automatizados usando **pytest**.

**Arquivo de Configuração:** `pytest.ini`

**Suites de Testes (8 arquivos):**

| Arquivo de Teste | Descrição | Cobertura |
|------------------|-----------|-----------|
| `test_ga_core.py` | Testa o núcleo do AG | Chromosome, Vehicle, divisão de rotas |
| `test_ga_operators.py` | Testa operadores genéticos | Mutação, crossover, validação de permutações |
| `test_ga_fitness.py` | Testa função de fitness | Cálculo multi-objetivo, penalidades |
| `test_ga_integration.py` | Testa integração completa | Execução ponta a ponta do GA |
| `test_api.py` | Testa endpoints REST | Validação de schemas, respostas HTTP |
| `test_api_execution.py` | Testa execução via API | Integração API → Execução → Banco |
| `test_controller.py` | Testa ExperimentManager | CRUD, execução background |
| `test_database.py` | Testa camada de persistência | ORM SQLAlchemy, modelos |

**Executar Testes:**

```bash
# Todos os testes
pytest tests/

# Modo verbose
pytest tests/ -v

# Teste específico
pytest tests/test_ga_operators.py -v

# Com cobertura (se tiver pytest-cov)
pytest tests/ --cov=src --cov-report=html
```

**Cobertura:**
- Testa todos os 24 operadores genéticos
- Validação de permutações válidas
- Testes de integração completa
- Validação de API e persistência
- Tratamento de erros

## 9. Como Executar o Projeto

### 9.1. Pré-requisitos

- **Python 3.8+** (recomendado: Python 3.10 ou superior)
- Bibliotecas listadas em `requirements.txt`
- Sistema Operacional: Linux, macOS ou Windows

### 9.2. Instalação

1. Clone o repositório ou descompacte os arquivos do projeto:
   ```bash
   git clone <url-do-repositorio>
   cd projeto2_haversine
   ```

2. Crie um ambiente virtual (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # ou
   venv\Scripts\activate  # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

### 9.3. Modos de Execução via Terminal

O script `main.py` oferece diferentes modos de execução:

#### **Modo Básico (Terminal)**
Roda a otimização no terminal e exibe os resultados:
```bash
python main.py --mode basic
```

#### **Visualização Interativa (Pygame)**
Abre a interface Pygame para visualização em tempo real:
```bash
python main.py --mode visual
```

#### **Modo Experimento**
Compara o desempenho de diferentes operadores genéticos:
```bash
python main.py --mode experiment
```

#### **Gerar Mapa HTML**
Executa otimização e gera o mapa interativo `mapa_rotas_hospitais_sp.html`:
```bash
python main.py --mode map
```

#### **Modo Silencioso**
Executa sem logs detalhados:
```bash
python main.py --mode basic --quiet
```

### 9.4. Executar API REST (Backend)

Inicie o servidor FastAPI para acesso programático:

```bash
# Modo desenvolvimento (com auto-reload)
uvicorn src.api.main:app --reload --port 8000

# Modo produção
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

**Acesse a documentação interativa:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Exemplos de uso:**

```bash
# Criar experimento
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

# Listar experimentos
curl http://localhost:8000/experiments

# Ver experimento específico
curl http://localhost:8000/experiments/1

# Limpar histórico de falhados
curl -X DELETE http://localhost:8000/experiments/failed
```

### 9.5. Executar Interface Web (Streamlit)

Inicie a interface web moderna:

```bash
streamlit run src/web/app.py
```

**Acesse no navegador:** http://localhost:8501

**Funcionalidades disponíveis:**
- Dashboard com métricas globais
- Configurador visual de todos os parâmetros
- Execução de experimentos (modo background ou interativo)
- Visualização de histórico
- Limpeza de experimentos
- Análise detalhada de resultados

### 9.6. Executar Testes Automatizados

Execute a suite completa de testes:

```bash
# Todos os testes
pytest tests/

# Com verbose
pytest tests/ -v

# Teste específico
pytest tests/test_ga_operators.py -v

# Com cobertura (requer pytest-cov)
pip install pytest-cov
pytest tests/ --cov=src --cov-report=html

# Abrir relatório de cobertura
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### 9.7. Workflow Completo Recomendado

Para uma experiência completa do sistema:

1. **Terminal 1** - Inicie a API:
   ```bash
   uvicorn src.api.main:app --reload --port 8000
   ```

2. **Terminal 2** - Inicie a Interface Web:
   ```bash
   streamlit run src/web/app.py
   ```

3. **Navegador** - Acesse:
   - Interface Web: http://localhost:8501
   - API Docs: http://localhost:8000/docs

4. **Configure e Execute:**
   - Use a interface web para configurar parâmetros
   - Execute experimentos via web ou API
   - Visualize resultados em tempo real (Pygame) ou no dashboard
   - Consulte histórico e compare configurações

## 10. Conclusão

Este projeto demonstrou a eficácia dos **Algoritmos Genéticos** na resolução de um problema complexo de otimização logística do mundo real: a distribuição de medicamentos e insumos hospitalares no estado de São Paulo. A implementação de **24 operadores genéticos** (8 de seleção, 8 de crossover e 8 de mutação) permitiu uma análise empírica aprofundada sobre quais combinações são mais adequadas para o problema de roteamento de veículos com múltiplas restrições.

**Principais Contribuições do Projeto:**

1. **Arquitetura Profissional Completa:**
   - Backend robusto com API REST (FastAPI)
   - Persistência de dados com SQLAlchemy e SQLite
   - Frontend moderno com Streamlit
   - Camada de controle (MVC) bem estruturada
   - Suite completa de testes automatizados (pytest)

2. **Múltiplas Abordagens de Operadores:**
   - Implementação detalhada de 8 variantes de cada tipo de operador
   - Comparação empírica de desempenho
   - Documentação acadêmica completa
   - Código modular e extensível

3. **Visualizações Ricas e Interativas:**
   - Mapas reais de São Paulo com Folium/Leaflet.js
   - Interface em tempo real com Pygame
   - Dashboard web com métricas e análises
   - Exportação de resultados em múltiplos formatos

4. **Dados Reais e Validação:**
   - 25+ hospitais reais do estado de São Paulo
   - Coordenadas GPS precisas
   - Prioridades de entrega (crítico, urgente, regular)
   - Cálculo de distância geodésica (Haversine)
   - Múltiplos cenários de teste (small, medium, large, critical)

5. **Reprodutibilidade Científica:**
   - Histórico completo de experimentos no banco de dados
   - Configurações parametrizáveis
   - Testes automatizados garantindo qualidade
   - Documentação detalhada (README + CLAUDE.md)

**Aplicabilidade Prática:**

O sistema desenvolvido pode ser utilizado em cenários reais de logística hospitalar, considerando não apenas a minimização de distâncias, mas também:
- **Priorização de entregas críticas** (medicamentos emergenciais)
- **Restrições de capacidade e autonomia** dos veículos
- **Múltiplos veículos** operando simultaneamente
- **Escalabilidade** para diferentes tamanhos de problema

**Impacto Acadêmico:**

Este projeto atende plenamente aos requisitos do **FIAP Tech Challenge Fase 2**, demonstrando:
- Domínio de meta-heurísticas (Algoritmos Genéticos)
- Implementação de arquitetura moderna (MVC, API REST, ORM)
- Boas práticas de engenharia de software (testes, modularização, documentação)
- Aplicação prática em problema de relevância social (saúde pública)

O código está **pronto para produção**, com mais de **14.000 linhas** de implementação robusta, testada e documentada.

## 11. Referências

[1] Toth, P., & Vigo, D. (Eds.). (2014). *Vehicle routing: problems, methods, and applications*. Society for Industrial and Applied Mathematics.

[2] Goldberg, D. E. (1989). *Genetic Algorithms in Search, Optimization, and Machine Learning*. Addison-Wesley.

[3] Eiben, A. E., & Smith, J. E. (2015). *Introduction to Evolutionary Computing*. Springer.

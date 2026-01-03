# Arquitetura do Sistema - Saudelog

Este documento apresenta a arquitetura completa do sistema de otimização de rotas utilizando diagramas Mermaid.

## 1. Visão Geral da Arquitetura MVC

```mermaid
graph TB
    subgraph "Camada de Visão (View)"
        WEB[Interface Web Streamlit]
        PYGAME[Visualização Pygame]
        API[API REST FastAPI]
        FOLIUM[Mapas HTML Folium]
    end

    subgraph "Camada de Controle (Controller)"
        MANAGER[ExperimentManager]
        GA_CTRL[GeneticAlgorithm]
    end

    subgraph "Camada de Modelo (Model)"
        DB[(SQLite Database)]
        ORM[SQLAlchemy ORM]
        DATA[Dados dos Hospitais]
    end

    subgraph "Núcleo do Algoritmo Genético"
        POP[Population]
        CHROM[Chromosome]
        SEL[Selection 8 métodos]
        CROSS[Crossover 8 operadores]
        MUT[Mutation 8 operadores]
        FIT[Fitness Function]
    end

    WEB --> MANAGER
    PYGAME --> GA_CTRL
    API --> MANAGER

    MANAGER --> GA_CTRL
    MANAGER --> ORM

    GA_CTRL --> POP
    GA_CTRL --> DATA

    POP --> CHROM
    POP --> SEL
    POP --> CROSS
    POP --> MUT

    CHROM --> FIT

    ORM --> DB

    GA_CTRL --> FOLIUM

    style WEB fill:#e1f5ff
    style PYGAME fill:#e1f5ff
    style API fill:#e1f5ff
    style FOLIUM fill:#e1f5ff
    style MANAGER fill:#fff4e1
    style GA_CTRL fill:#fff4e1
    style DB fill:#e8f5e9
    style ORM fill:#e8f5e9
    style DATA fill:#e8f5e9
```

## 2. Arquitetura Detalhada de Componentes

```mermaid
graph LR
    subgraph "Frontend"
        ST[Streamlit Dashboard]
        PG[Pygame Visualizer]
    end

    subgraph "Backend API"
        FA[FastAPI Server]
        EP1[POST /run]
        EP2[GET /experiments]
        EP3[DELETE /experiments]
        EP4[GET /scenarios]
        EP5[GET /config]

        FA --> EP1
        FA --> EP2
        FA --> EP3
        FA --> EP4
        FA --> EP5
    end

    subgraph "Business Logic"
        EM[ExperimentManager]
        GA[GeneticAlgorithm]

        EM --> GA
    end

    subgraph "Data Layer"
        SQL[(SQLite DB)]
        SQLA[SQLAlchemy ORM]
        MODELS[Experiment Model]

        SQLA --> SQL
        MODELS --> SQLA
    end

    subgraph "Domain Logic"
        GENETIC[genetic_algorithm/]
        VIZ[visualization/]
        UTILS[utils/]
    end

    ST -.HTTP.-> FA
    PG --> GA

    EP1 --> EM
    EP2 --> EM
    EP3 --> EM
    EP4 --> EM

    EM --> MODELS
    GA --> GENETIC
    GA --> VIZ
    GA --> UTILS

    style ST fill:#4285f4,color:#fff
    style PG fill:#4285f4,color:#fff
    style FA fill:#34a853,color:#fff
    style EM fill:#fbbc04
    style GA fill:#fbbc04
    style SQL fill:#ea4335,color:#fff
```

## 3. Estrutura de Módulos e Dependências

```mermaid
graph TD
    subgraph "src/genetic_algorithm"
        GA_MAIN[genetic_algorithm.py]
        POP[population.py]
        CHROM[chromosome.py]
        SEL[selection.py]
        CROSS[crossover.py]
        MUT[mutation.py]
        FIT[fitness.py]

        GA_MAIN --> POP
        GA_MAIN --> SEL
        GA_MAIN --> CROSS
        GA_MAIN --> MUT
        POP --> CHROM
        CHROM --> FIT
    end

    subgraph "src/visualization"
        ROUTE_VIZ[route_visualizer.py]
        EVO_VIZ[evolution_visualizer.py]
        INT_VIEW[interactive_viewer.py]

        INT_VIEW --> EVO_VIZ
        INT_VIEW --> ROUTE_VIZ
    end

    subgraph "src/api"
        API_MAIN[main.py]
    end

    subgraph "src/controllers"
        EXP_MGR[experiment_manager.py]
    end

    subgraph "src/database"
        DB_CONF[database.py]
        DB_MODELS[models.py]

        DB_MODELS --> DB_CONF
    end

    subgraph "src/web"
        WEB_APP[app.py]
        STYLES[components/styles.py]

        WEB_APP --> STYLES
    end

    subgraph "src/utils"
        DIST[distance.py]
    end

    subgraph "data"
        HOSP[hospitais_sp.py]
    end

    API_MAIN --> EXP_MGR
    WEB_APP --> API_MAIN
    INT_VIEW --> GA_MAIN

    EXP_MGR --> GA_MAIN
    EXP_MGR --> DB_MODELS
    EXP_MGR --> HOSP

    GA_MAIN --> ROUTE_VIZ
    CHROM --> DIST
    FIT --> DIST

    style GA_MAIN fill:#ff6b6b
    style API_MAIN fill:#4ecdc4
    style WEB_APP fill:#45b7d1
    style EXP_MGR fill:#f9ca24
```

## 4. Fluxo de Dados - Execução de Experimento

```mermaid
sequenceDiagram
    participant User
    participant Streamlit
    participant API
    participant Manager
    participant GA
    participant Database

    User->>Streamlit: Configura parâmetros
    Streamlit->>API: POST /run (config JSON)
    API->>Manager: create_experiment(config)
    Manager->>Database: INSERT experiment (status: pending)
    Database-->>Manager: experiment_id
    Manager-->>API: experiment_id
    API-->>Streamlit: {id, status: "pending"}

    Note over Manager,GA: Execução em Background
    Manager->>Database: UPDATE status = "running"
    Manager->>GA: execute(config)

    loop Para cada geração
        GA->>GA: Selection
        GA->>GA: Crossover
        GA->>GA: Mutation
        GA->>GA: Fitness Evaluation
    end

    GA-->>Manager: result (best_solution)
    Manager->>Database: UPDATE experiment<br/>(status: "completed",<br/>best_fitness, routes)

    User->>Streamlit: Consulta Dashboard
    Streamlit->>API: GET /experiments
    API->>Manager: list_experiments()
    Manager->>Database: SELECT * FROM experiments
    Database-->>Manager: experiments[]
    Manager-->>API: experiments[]
    API-->>Streamlit: JSON response
    Streamlit-->>User: Exibe resultados
```

## 5. Stack Tecnológico

```mermaid
graph TB
    subgraph "Frontend & Visualização"
        ST[Streamlit<br/>Interface Web]
        PG[Pygame<br/>Visualização Tempo Real]
        FOL[Folium<br/>Mapas Interativos]
        MPL[Matplotlib<br/>Gráficos Estáticos]
    end

    subgraph "Backend & API"
        FA[FastAPI<br/>REST API]
        UV[Uvicorn<br/>ASGI Server]
        PYD[Pydantic<br/>Validação]
    end

    subgraph "Persistência"
        SQLA[SQLAlchemy<br/>ORM]
        SQLITE[SQLite<br/>Database]
    end

    subgraph "Computação Científica"
        NP[NumPy<br/>Arrays & Cálculos]
        PD[Pandas<br/>DataFrames]
    end

    subgraph "Testes"
        PT[Pytest<br/>Framework de Testes]
        PTCOV[Pytest-cov<br/>Cobertura]
    end

    subgraph "Linguagem"
        PY[Python 3.8+]
    end

    ST --> PY
    PG --> PY
    FOL --> PY
    MPL --> PY
    FA --> PY
    UV --> FA
    PYD --> FA
    SQLA --> PY
    SQLITE --> SQLA
    NP --> PY
    PD --> PY
    PT --> PY
    PTCOV --> PT

    style PY fill:#3776ab,color:#fff
    style ST fill:#ff4b4b,color:#fff
    style FA fill:#009688,color:#fff
    style SQLITE fill:#003b57,color:#fff
    style PT fill:#0a9edc,color:#fff
```

## 6. Fluxo de Operadores Genéticos

```mermaid
graph TD
    START[Início da Geração]

    START --> EVAL1[Avaliação Fitness<br/>População Atual]

    EVAL1 --> SEL{Seleção}

    SEL -->|Tournament| SEL1[Tournament Selection]
    SEL -->|Roulette| SEL2[Roulette Wheel]
    SEL -->|Rank| SEL3[Rank Selection]
    SEL -->|Truncation| SEL4[Truncation]
    SEL -->|Elitist| SEL5[Elitist Selection]
    SEL -->|SUS| SEL6[Stochastic Universal]
    SEL -->|Boltzmann| SEL7[Boltzmann Selection]
    SEL -->|Steady State| SEL8[Steady State]

    SEL1 --> PARENTS[Pais Selecionados]
    SEL2 --> PARENTS
    SEL3 --> PARENTS
    SEL4 --> PARENTS
    SEL5 --> PARENTS
    SEL6 --> PARENTS
    SEL7 --> PARENTS
    SEL8 --> PARENTS

    PARENTS --> CROSS{Crossover}

    CROSS -->|PMX| CROSS1[Partially Mapped]
    CROSS -->|OX| CROSS2[Order Crossover]
    CROSS -->|CX| CROSS3[Cycle Crossover]
    CROSS -->|AEX| CROSS4[Alternating Edges]
    CROSS -->|ERX| CROSS5[Edge Recombination]
    CROSS -->|SCX| CROSS6[Sequential Constructive]
    CROSS -->|OX2| CROSS7[Order-Based]
    CROSS -->|POS| CROSS8[Position-Based]

    CROSS1 --> OFFSPRING[Filhos Gerados]
    CROSS2 --> OFFSPRING
    CROSS3 --> OFFSPRING
    CROSS4 --> OFFSPRING
    CROSS5 --> OFFSPRING
    CROSS6 --> OFFSPRING
    CROSS7 --> OFFSPRING
    CROSS8 --> OFFSPRING

    OFFSPRING --> MUT{Mutação}

    MUT -->|Swap| MUT1[Swap Mutation]
    MUT -->|Inversion| MUT2[Inversion]
    MUT -->|Scramble| MUT3[Scramble]
    MUT -->|Insert| MUT4[Insert]
    MUT -->|Displacement| MUT5[Displacement]
    MUT -->|2-opt| MUT6[2-opt]
    MUT -->|3-opt| MUT7[3-opt]
    MUT -->|RSM| MUT8[Reverse Sequence]

    MUT1 --> MUTATED[Filhos Mutados]
    MUT2 --> MUTATED
    MUT3 --> MUTATED
    MUT4 --> MUTATED
    MUT5 --> MUTATED
    MUT6 --> MUTATED
    MUT7 --> MUTATED
    MUT8 --> MUTATED

    MUTATED --> EVAL2[Avaliação Fitness<br/>Nova Geração]

    EVAL2 --> REPLACE{Substituição}

    REPLACE -->|Generational| REP1[Substitui População Completa]
    REPLACE -->|Steady State| REP2[Substitui Parcialmente]
    REPLACE -->|Elitist| REP3[Preserva Melhores + Nova Geração]

    REP1 --> CHECK{Critério<br/>de Parada?}
    REP2 --> CHECK
    REP3 --> CHECK

    CHECK -->|Não| START
    CHECK -->|Sim| END[Retorna Melhor Solução]

    style START fill:#4caf50,color:#fff
    style END fill:#f44336,color:#fff
    style SEL fill:#2196f3,color:#fff
    style CROSS fill:#ff9800,color:#fff
    style MUT fill:#9c27b0,color:#fff
    style REPLACE fill:#00bcd4,color:#fff
```

## 7. Modelo de Dados

```mermaid
erDiagram
    EXPERIMENT {
        int id PK
        datetime created_at
        string status
        json config
        float best_fitness
        int generations_run
        float execution_time
        json result_details
    }

    DELIVERY_POINT {
        int id
        string name
        float latitude
        float longitude
        int priority
        float demand
        string address
    }

    VEHICLE {
        int id
        float capacity
        float max_distance
        float speed
    }

    ROUTE {
        int id
        int vehicle_id FK
        float total_distance
        float total_load
        json stops
    }

    CHROMOSOME {
        int id
        json genes
        float fitness
        int generation
    }

    EXPERIMENT ||--o{ ROUTE : "generates"
    ROUTE }o--|| VEHICLE : "uses"
    ROUTE }o--o{ DELIVERY_POINT : "visits"
    EXPERIMENT ||--o{ CHROMOSOME : "evaluates"
```

## 8. Ciclo de Vida do Experimento

```mermaid
stateDiagram-v2
    [*] --> Pending: Experimento criado

    Pending --> Running: Iniciar execução

    Running --> Initializing: Criar população inicial
    Initializing --> Evolving: População criada

    Evolving --> Evaluating: Calcular fitness
    Evaluating --> Selecting: Fitness calculado
    Selecting --> Crossing: Pais selecionados
    Crossing --> Mutating: Filhos criados
    Mutating --> Replacing: Mutação aplicada
    Replacing --> Evolving: Nova geração criada

    Evolving --> Converged: Critério de parada
    Converged --> Completed: Salvar resultados

    Running --> Failed: Erro ocorreu

    Completed --> [*]
    Failed --> [*]

    note right of Evolving
        Loop executado por
        max_generations ou
        até stagnation_limit
    end note

    note right of Completed
        - best_fitness salvo
        - routes persistidas
        - execution_time registrado
    end note
```

## 9. Arquitetura de Deployment

```mermaid
graph TB
    subgraph "Cliente - Navegador"
        BROWSER[Web Browser]
    end

    subgraph "Servidor de Aplicação - Localhost"
        subgraph "Processo 1 - Terminal 1"
            API_SERVER[FastAPI Server<br/>Port 8000<br/>uvicorn]
        end

        subgraph "Processo 2 - Terminal 2"
            WEB_SERVER[Streamlit Server<br/>Port 8501<br/>streamlit]
        end

        subgraph "Processo 3 - Opcional"
            PYGAME_PROC[Processo Pygame<br/>Visualização Desktop]
        end

        subgraph "Armazenamento Local"
            DB_FILE[(experiments.db<br/>SQLite)]
            DATA_FILE[(hospitais_sp.json<br/>Dados Estáticos)]
            ASSETS[assets/<br/>logo.png]
        end
    end

    BROWSER -->|HTTP :8501| WEB_SERVER
    WEB_SERVER -->|HTTP :8000| API_SERVER

    API_SERVER --> DB_FILE
    API_SERVER --> DATA_FILE

    WEB_SERVER --> ASSETS
    WEB_SERVER -.spawn.-> PYGAME_PROC

    PYGAME_PROC --> DATA_FILE

    style BROWSER fill:#ffd54f
    style API_SERVER fill:#4caf50,color:#fff
    style WEB_SERVER fill:#2196f3,color:#fff
    style PYGAME_PROC fill:#9c27b0,color:#fff
    style DB_FILE fill:#f44336,color:#fff
```

## 10. Estrutura de Testes

```mermaid
graph LR
    subgraph "Suite de Testes"
        PYTEST[Pytest Framework]

        subgraph "Testes Unitários"
            T_CORE[test_ga_core.py<br/>Chromosome, Vehicle]
            T_OPS[test_ga_operators.py<br/>24 operadores]
            T_FIT[test_ga_fitness.py<br/>Função fitness]
        end

        subgraph "Testes de Integração"
            T_INT[test_ga_integration.py<br/>Execução completa]
            T_API[test_api.py<br/>Endpoints REST]
            T_EXEC[test_api_execution.py<br/>Execução via API]
        end

        subgraph "Testes de Infraestrutura"
            T_CTRL[test_controller.py<br/>ExperimentManager]
            T_DB[test_database.py<br/>ORM & Persistência]
        end
    end

    subgraph "Código Fonte"
        SRC[src/]
    end

    subgraph "Relatórios"
        COV[Coverage Report<br/>HTML]
        RESULTS[Test Results<br/>Terminal]
    end

    PYTEST --> T_CORE
    PYTEST --> T_OPS
    PYTEST --> T_FIT
    PYTEST --> T_INT
    PYTEST --> T_API
    PYTEST --> T_EXEC
    PYTEST --> T_CTRL
    PYTEST --> T_DB

    T_CORE -.testa.-> SRC
    T_OPS -.testa.-> SRC
    T_FIT -.testa.-> SRC
    T_INT -.testa.-> SRC
    T_API -.testa.-> SRC
    T_EXEC -.testa.-> SRC
    T_CTRL -.testa.-> SRC
    T_DB -.testa.-> SRC

    PYTEST --> COV
    PYTEST --> RESULTS

    style PYTEST fill:#0a9edc,color:#fff
    style COV fill:#4caf50,color:#fff
    style RESULTS fill:#ff9800,color:#fff
```

## Resumo da Arquitetura

### Camadas Principais

1. **Camada de Apresentação (View)**
   - Interface Web Streamlit (Dashboard, Configuração, Análise)
   - Visualização em Tempo Real Pygame
   - Mapas Interativos Folium
   - API REST FastAPI

2. **Camada de Lógica de Negócio (Controller)**
   - ExperimentManager: Orquestra experimentos e persistência
   - GeneticAlgorithm: Implementa o algoritmo genético completo

3. **Camada de Domínio**
   - 24 Operadores Genéticos (8 seleção + 8 crossover + 8 mutação)
   - Função de Fitness Multi-objetivo
   - Representação de Cromossomos e População

4. **Camada de Dados (Model)**
   - SQLAlchemy ORM
   - SQLite Database
   - Modelo Experiment
   - Dados estáticos dos hospitais

### Tecnologias Principais

- **Backend**: Python 3.8+, FastAPI, Uvicorn
- **Frontend**: Streamlit, Pygame
- **Visualização**: Folium, Matplotlib
- **Persistência**: SQLAlchemy, SQLite
- **Computação**: NumPy, Pandas
- **Testes**: Pytest, pytest-cov
- **Validação**: Pydantic

### Fluxos Principais

1. **Fluxo de Criação de Experimento**: User → Streamlit → API → Manager → Database
2. **Fluxo de Execução**: Manager → GA → Operadores Genéticos → Resultado
3. **Fluxo de Visualização**: GA → Pygame/Folium → User
4. **Fluxo de Consulta**: User → Streamlit → API → Database → Response

### Características de Qualidade

- **Modularidade**: Separação clara de responsabilidades
- **Extensibilidade**: Novos operadores podem ser adicionados facilmente
- **Testabilidade**: 8 suites de teste cobrindo todas as camadas
- **Escalabilidade**: Execução assíncrona e background tasks
- **Persistência**: Histórico completo de experimentos
- **Usabilidade**: Múltiplas interfaces para diferentes casos de uso

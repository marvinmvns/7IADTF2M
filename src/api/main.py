from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from src.controllers.experiment_manager import ExperimentManager
from src.genetic_algorithm.selection import SelectionMethod
from src.genetic_algorithm.crossover import CrossoverMethod
from src.genetic_algorithm.mutation import MutationMethod
from src.genetic_algorithm.genetic_algorithm import ReplacementStrategy
from src.genetic_algorithm.fitness import FitnessType

app = FastAPI(
    title="Genetic Algorithm VRP Optimization API",
    description="""
# API de Otimização de Rotas com Algoritmo Genético

API RESTful para otimização de rotas de entrega de medicamentos e suprimentos para hospitais usando Algoritmos Genéticos.

## Características

* **24 Operadores Genéticos**: 8 métodos de seleção, 8 operadores de crossover, 8 operadores de mutação
* **Multi-objetivo**: Otimiza distância, prioridades, capacidade e autonomia
* **Dados Reais**: Baseado em coordenadas de hospitais de São Paulo
* **Execução Assíncrona**: Experimentos executam em background
* **Persistência**: Histórico completo em SQLite

## Cenários Disponíveis

* `small`: ~10 hospitais, 2 veículos (testes rápidos)
* `medium`: ~20 hospitais, 3 veículos (padrão)
* `large`: Todos hospitais, 4-5 veículos (computacionalmente intensivo)
* `critical`: Apenas entregas críticas/urgentes

## Tecnologias

* FastAPI + Uvicorn
* SQLAlchemy + SQLite
* NumPy + Pandas
* Pydantic para validação
    """,
    version="2.0.0",
    contact={
        "name": "FIAP Tech Challenge - Fase 2",
        "email": "contato@example.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_tags=[
        {
            "name": "experiments",
            "description": "Operações de criação, consulta e gerenciamento de experimentos"
        },
        {
            "name": "scenarios",
            "description": "Consulta de cenários e dados de hospitais"
        },
        {
            "name": "configuration",
            "description": "Configurações padrão e opções disponíveis"
        }
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = ExperimentManager()

# ==================== RESPONSE MODELS ====================

class ExperimentResponse(BaseModel):
    """Resposta de criação de experimento"""
    id: int = Field(..., description="ID único do experimento")
    status: str = Field(..., description="Status: pending, running, completed, failed")
    message: str = Field(..., description="Mensagem descritiva")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 42,
                "status": "pending",
                "message": "Experimento iniciado."
            }
        }

class ExperimentDetail(BaseModel):
    """Detalhes completos de um experimento"""
    id: int
    created_at: datetime
    status: str
    config: Dict
    best_fitness: Optional[float] = None
    generations_run: Optional[int] = None
    execution_time: Optional[float] = None
    result_details: Optional[Dict] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 42,
                "created_at": "2024-01-15 14:30:00",
                "status": "completed",
                "config": {"population_size": 100, "max_generations": 10000},
                "best_fitness": 1234.56,
                "generations_run": 150,
                "execution_time": 45.2,
                "result_details": {"routes": [[0, 1, 2, 0], [0, 3, 4, 0]]}
            }
        }

class DeleteResponse(BaseModel):
    """Resposta de operação de deleção"""
    message: str = Field(..., description="Mensagem de confirmação")

    class Config:
        json_schema_extra = {
            "example": {"message": "Experimento 42 removido"}
        }

# ==================== REQUEST MODELS ====================

class ExperimentConfig(BaseModel):
    """Configuração completa de um experimento de otimização"""

    # Parâmetros Gerais
    population_size: int = Field(
        100,
        ge=10,
        le=500,
        description="Tamanho da população (10-500)",
        examples=[50, 100, 200]
    )
    max_generations: int = Field(
        10000,
        ge=10,
        le=10000,
        description="Número máximo de gerações (10-10000)",
        examples=[200, 1000, 10000]
    )
    crossover_rate: float = Field(
        0.9,
        ge=0.0,
        le=1.0,
        description="Taxa de crossover (0.0-1.0). Recomendado: 0.8-0.95",
        examples=[0.8, 0.9, 0.95]
    )
    mutation_rate: float = Field(
        0.15,
        ge=0.0,
        le=1.0,
        description="Taxa de mutação (0.0-1.0). Recomendado: 0.05-0.2",
        examples=[0.05, 0.1, 0.15]
    )
    
    # Métodos (Enums)
    selection_method: SelectionMethod = Field(
        SelectionMethod.TOURNAMENT,
        description="Método de seleção: TOURNAMENT, ROULETTE, RANKING, TRUNCATION, ELITIST, SUS, BOLTZMANN, STEADY_STATE"
    )
    crossover_method: CrossoverMethod = Field(
        CrossoverMethod.OX,
        description="Operador de crossover: PMX, OX, CX, AEX, ERX, SCX, OX2, POS"
    )
    mutation_method: MutationMethod = Field(
        MutationMethod.INVERSION,
        description="Operador de mutação: SWAP, INVERSION, SCRAMBLE, INSERT, DISPLACEMENT, TWO_OPT, THREE_OPT, RSM"
    )
    replacement_strategy: ReplacementStrategy = Field(
        ReplacementStrategy.ELITIST,
        description="Estratégia de substituição: GENERATIONAL, STEADY_STATE, ELITIST"
    )
    fitness_type: FitnessType = Field(
        FitnessType.WEIGHTED_MULTI,
        description="Tipo de função fitness: WEIGHTED_MULTI, LEXICOGRAPHIC, PARETO"
    )

    # Parâmetros Específicos de Métodos
    tournament_size: int = Field(
        3,
        ge=2,
        le=10,
        description="Tamanho do torneio para Tournament Selection (2-10)",
        examples=[2, 3, 5]
    )
    elite_size: int = Field(
        2,
        ge=0,
        le=20,
        description="Número de indivíduos elitistas a preservar (0-20)",
        examples=[1, 2, 5]
    )
    truncation_threshold: float = Field(
        0.5,
        ge=0.0,
        le=1.0,
        description="Limiar de truncamento para Truncation Selection (0.0-1.0)",
        examples=[0.3, 0.5, 0.7]
    )
    boltzmann_temperature: float = Field(
        100.0,
        ge=0.1,
        description="Temperatura inicial para Boltzmann Selection",
        examples=[50.0, 100.0, 200.0]
    )
    steady_state_ratio: float = Field(
        0.2,
        ge=0.0,
        le=1.0,
        description="Taxa de substituição para Steady State Selection (0.0-1.0)",
        examples=[0.1, 0.2, 0.3]
    )

    # Configuração do Problema
    num_vehicles: int = Field(
        3,
        ge=1,
        le=10,
        description="Número de veículos disponíveis (1-10)",
        examples=[2, 3, 5]
    )
    vehicle_capacity: float = Field(
        100.0,
        ge=1.0,
        description="Capacidade de carga do veículo (kg ou unidades)",
        examples=[50.0, 100.0, 150.0]
    )
    vehicle_speed: float = Field(
        40.0,
        ge=1.0,
        description="Velocidade média do veículo (km/h)",
        examples=[30.0, 40.0, 60.0]
    )
    vehicle_max_distance: float = Field(
        200.0,
        ge=1.0,
        description="Autonomia máxima do veículo (km)",
        examples=[150.0, 200.0, 300.0]
    )

    # Configuração do Cenário
    scenario: str = Field(
        "large",
        pattern="^(small|medium|large|critical|custom)$",
        description="Cenário de teste: small (~10 hospitais), medium (~20), large (todos), critical (entregas críticas)",
        examples=["small", "medium", "large"]
    )

    # Pesos da Função de Fitness (Multi-objetivo)
    w_distance: float = Field(
        1.0,
        ge=0.0,
        description="Peso da distância total percorrida na função fitness",
        examples=[0.5, 1.0, 2.0]
    )
    w_priority: float = Field(
        10.0,
        ge=0.0,
        description="Peso da penalidade de prioridade (entregas críticas não atendidas cedo)",
        examples=[5.0, 10.0, 50.0]
    )
    w_capacity: float = Field(
        100.0,
        ge=0.0,
        description="Peso da penalidade de violação de capacidade",
        examples=[50.0, 100.0, 200.0]
    )
    w_autonomy: float = Field(
        100.0,
        ge=0.0,
        description="Peso da penalidade de violação de autonomia",
        examples=[50.0, 100.0, 200.0]
    )
    w_window: float = Field(
        50.0,
        ge=0.0,
        description="Peso da penalidade de janela de tempo",
        examples=[20.0, 50.0, 100.0]
    )

    # Critérios de Parada
    stagnation_enabled: bool = Field(
        True,
        description="Habilita parada por estagnação"
    )
    stagnation_limit: int = Field(
        5000,
        ge=1,
        le=10000,
        description="Limite de gerações consecutivas sem melhoria antes de parar (1-10000). Ignorado se estagnação estiver desativada",
        examples=[200, 1000, 5000]
    )

    # Configuração de Inicialização
    heuristic_init_ratio: float = Field(
        0.2,
        ge=0.0,
        le=1.0,
        description="Proporção da população inicial gerada com heurística nearest-neighbor (0.0-1.0)",
        examples=[0.0, 0.2, 0.5]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "population_size": 100,
                "max_generations": 10000,
                "crossover_rate": 0.9,
                "mutation_rate": 0.15,
                "selection_method": "TOURNAMENT",
                "crossover_method": "OX",
                "mutation_method": "INVERSION",
                "replacement_strategy": "ELITIST",
                "fitness_type": "WEIGHTED_MULTI",
                "tournament_size": 3,
                "elite_size": 2,
                "num_vehicles": 3,
                "vehicle_capacity": 100.0,
                "vehicle_speed": 40.0,
                "vehicle_max_distance": 200.0,
                "scenario": "medium",
                "w_distance": 1.0,
                "w_priority": 10.0,
                "w_capacity": 100.0,
                "w_autonomy": 100.0,
                "w_window": 50.0,
                "stagnation_enabled": True,
                "stagnation_limit": 5000,
                "heuristic_init_ratio": 0.2
            }
        }

# ==================== ENDPOINTS ====================

@app.post(
    "/run",
    response_model=ExperimentResponse,
    tags=["experiments"],
    summary="Criar e executar novo experimento",
    description="""
    Cria um novo experimento de otimização de rotas e inicia sua execução em background.

    O experimento será executado de forma assíncrona. Use os endpoints de consulta para
    acompanhar o progresso e obter resultados.

    **Fluxo de execução:**
    1. Valida configuração recebida
    2. Cria registro no banco de dados (status: pending)
    3. Inicia processamento em background
    4. Retorna ID para consulta posterior

    **Tempo estimado de execução:**
    - Small scenario: 10-30 segundos
    - Medium scenario: 30-90 segundos
    - Large scenario: 2-5 minutos
    """,
    responses={
        200: {
            "description": "Experimento criado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "id": 42,
                        "status": "pending",
                        "message": "Experimento iniciado."
                    }
                }
            }
        },
        422: {"description": "Erro de validação nos parâmetros"},
        500: {"description": "Erro interno do servidor"}
    }
)
async def run_experiment(config: ExperimentConfig, background_tasks: BackgroundTasks):
    try:
        config_dict = config.model_dump(mode='json')
        exp = manager.create_experiment(config_dict)
        background_tasks.add_task(manager.run_experiment_background, exp.id)
        return {"id": exp.id, "status": "pending", "message": "Experimento iniciado."}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/experiments",
    response_model=List[ExperimentDetail],
    tags=["experiments"],
    summary="Listar todos os experimentos",
    description="""
    Retorna lista de todos os experimentos executados, ordenados por data de criação (mais recentes primeiro).

    Cada experimento contém:
    - **id**: Identificador único
    - **created_at**: Data/hora de criação
    - **status**: pending, running, completed, failed
    - **config**: Configuração utilizada
    - **best_fitness**: Melhor fitness obtido (se concluído)
    - **generations_run**: Gerações executadas
    - **execution_time**: Tempo de execução em segundos
    - **result_details**: Rotas e detalhes da solução
    """
)
def list_experiments(limit: int = 200):
    return manager.list_experiments(limit=limit)

@app.get(
    "/experiments/latest",
    tags=["experiments"],
    summary="Obter último experimento",
    description="Retorna o experimento mais recente executado no sistema."
)
def get_latest_experiment():
    exps = manager.list_experiments(limit=1)
    if not exps:
        return {}
    return exps[0]

@app.get(
    "/experiments/{experiment_id}",
    tags=["experiments"],
    summary="Obter detalhes de experimento específico",
    description="Retorna todos os detalhes de um experimento pelo seu ID.",
    responses={
        200: {"description": "Experimento encontrado"},
        404: {"description": "Experimento não encontrado"}
    }
)
def get_experiment(experiment_id: int):
    exp = manager.get_experiment(experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experimento não encontrado")
    return exp

@app.delete(
    "/experiments/all",
    response_model=DeleteResponse,
    tags=["experiments"],
    summary="Limpar todo histórico de experimentos",
    description="""
    **ATENÇÃO:** Remove TODOS os experimentos do banco de dados. Esta operação é irreversível.

    Use este endpoint para limpar o histórico completo de experimentos.
    """,
    responses={
        200: {"description": "Histórico limpo com sucesso"},
        500: {"description": "Erro ao limpar histórico"}
    }
)
def delete_all_experiments():
    success = manager.delete_all_experiments()
    if not success:
        raise HTTPException(status_code=500, detail="Erro ao limpar histórico")
    return {"message": "Histórico limpo com sucesso"}

@app.delete(
    "/experiments/failed",
    response_model=DeleteResponse,
    tags=["experiments"],
    summary="Remover experimentos falhados",
    description="Remove apenas os experimentos com status 'failed', mantendo os demais intactos."
)
def delete_failed_experiments():
    success = manager.delete_failed_experiments()
    if not success:
        raise HTTPException(status_code=500, detail="Erro ao limpar experimentos falhados")
    return {"message": "Experimentos falhados removidos"}

@app.delete(
    "/experiments/{experiment_id}",
    response_model=DeleteResponse,
    tags=["experiments"],
    summary="Deletar experimento específico",
    description="Remove um experimento específico pelo seu ID.",
    responses={
        200: {"description": "Experimento removido com sucesso"},
        404: {"description": "Experimento não encontrado"}
    }
)
def delete_experiment(experiment_id: int):
    success = manager.delete_experiment(experiment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Experimento não encontrado ou erro ao deletar")
    return {"message": f"Experimento {experiment_id} removido"}

@app.get(
    "/scenarios/{scenario_name}",
    tags=["scenarios"],
    summary="Visualizar dados do cenário",
    description="""
    Retorna os dados completos de um cenário (hospitais, coordenadas, demandas, prioridades).

    Útil para preview antes de executar experimento.

    **Cenários disponíveis:**
    - `small`: ~10 hospitais
    - `medium`: ~20 hospitais
    - `large`: Todos os hospitais (~50+)
    - `critical`: Apenas entregas críticas/urgentes
    """,
    responses={
        200: {"description": "Dados do cenário"},
        500: {"description": "Cenário inválido ou erro ao carregar"}
    }
)
def get_scenario_preview(scenario_name: str):
    try:
        data = manager.get_scenario_data(scenario_name)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/config/defaults",
    tags=["configuration"],
    summary="Obter configuração padrão",
    description="""
    Retorna os valores padrão recomendados para todos os parâmetros de configuração.

    Use este endpoint para:
    - Inicializar formulários de configuração
    - Resetar configurações para valores padrão
    - Entender valores recomendados
    """
)
def get_default_config():
    default_config = ExperimentConfig()
    return {
        "population_size": default_config.population_size,
        "max_generations": default_config.max_generations,
        "crossover_rate": default_config.crossover_rate,
        "mutation_rate": default_config.mutation_rate,
        "selection_method": default_config.selection_method.value,
        "crossover_method": default_config.crossover_method.value,
        "mutation_method": default_config.mutation_method.value,
        "replacement_strategy": default_config.replacement_strategy.value,
        "fitness_type": default_config.fitness_type.value,
        "tournament_size": default_config.tournament_size,
        "elite_size": default_config.elite_size,
        "truncation_threshold": default_config.truncation_threshold,
        "boltzmann_temperature": default_config.boltzmann_temperature,
        "steady_state_ratio": default_config.steady_state_ratio,
        "num_vehicles": default_config.num_vehicles,
        "vehicle_capacity": default_config.vehicle_capacity,
        "vehicle_speed": default_config.vehicle_speed,
        "vehicle_max_distance": default_config.vehicle_max_distance,
        "scenario": default_config.scenario,
        "w_distance": default_config.w_distance,
        "w_priority": default_config.w_priority,
        "w_capacity": default_config.w_capacity,
        "w_autonomy": default_config.w_autonomy,
        "w_window": default_config.w_window,
        "stagnation_enabled": default_config.stagnation_enabled,
        "stagnation_limit": default_config.stagnation_limit,
        "heuristic_init_ratio": default_config.heuristic_init_ratio
    }

@app.get(
    "/config/options",
    tags=["configuration"],
    summary="Obter opções de configuração disponíveis",
    description="""
    Retorna todas as opções válidas para campos de configuração (enums, cenários, etc.).

    Útil para:
    - Construir dropdowns/selects em UIs
    - Validar inputs antes de enviar
    - Descobrir operadores genéticos disponíveis

    **Retorna:**
    - `scenarios`: Lista de cenários válidos
    - `selection_methods`: 8 métodos de seleção disponíveis
    - `crossover_methods`: 8 operadores de crossover
    - `mutation_methods`: 8 operadores de mutação
    - `replacement_strategies`: Estratégias de substituição
    - `fitness_types`: Tipos de função fitness
    """
)
def get_config_options():
    return {
        "scenarios": ["small", "medium", "large", "critical"],
        "selection_methods": [method.value for method in SelectionMethod],
        "crossover_methods": [method.value for method in CrossoverMethod],
        "mutation_methods": [method.value for method in MutationMethod],
        "replacement_strategies": [strategy.value for strategy in ReplacementStrategy],
        "fitness_types": [ft.value for ft in FitnessType],
        "api_url": "http://localhost:8000",
        "logo_path": "assets/logo.png"
    }

@app.get(
    "/",
    tags=["health"],
    summary="Health check",
    description="Verifica se a API está funcionando corretamente."
)
def root():
    return {
        "status": "online",
        "service": "Genetic Algorithm VRP Optimization API",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

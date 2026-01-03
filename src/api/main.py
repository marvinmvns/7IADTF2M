from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict
from src.controllers.experiment_manager import ExperimentManager
from src.genetic_algorithm.selection import SelectionMethod
from src.genetic_algorithm.crossover import CrossoverMethod
from src.genetic_algorithm.mutation import MutationMethod
from src.genetic_algorithm.genetic_algorithm import ReplacementStrategy 
from src.genetic_algorithm.fitness import FitnessType

app = FastAPI(title="GA Optimization API", description="API para Algoritmo Genético de Rotas")

manager = ExperimentManager()

class ExperimentConfig(BaseModel):
    # Parâmetros Gerais
    population_size: int = Field(100, ge=10, description="Tamanho da população")
    max_generations: int = Field(200, ge=10, description="Número máximo de gerações")
    crossover_rate: float = Field(0.9, ge=0.0, le=1.0, description="Taxa de crossover")
    mutation_rate: float = Field(0.15, ge=0.0, le=1.0, description="Taxa de mutação")
    
    # Métodos (Enums)
    selection_method: SelectionMethod = SelectionMethod.TOURNAMENT
    crossover_method: CrossoverMethod = CrossoverMethod.OX
    mutation_method: MutationMethod = MutationMethod.INVERSION
    replacement_strategy: ReplacementStrategy = ReplacementStrategy.ELITIST
    fitness_type: FitnessType = FitnessType.WEIGHTED_MULTI
    
    # Parâmetros Específicos de Métodos
    tournament_size: int = Field(3, ge=2, description="Tamanho do torneio (Selection)")
    elite_size: int = Field(2, ge=0, description="Número de indivíduos elitistas")
    truncation_threshold: float = Field(0.5, ge=0.0, le=1.0, description="Limiar de truncamento (Selection)")
    boltzmann_temperature: float = Field(100.0, ge=0.1, description="Temperatura inicial (Selection Boltzmann)")
    steady_state_ratio: float = Field(0.2, ge=0.0, le=1.0, description="Taxa de substituição (Selection Steady State)")
    
    # Configuração do Problema
    num_vehicles: int = Field(3, ge=1, description="Número de veículos")
    vehicle_capacity: float = Field(100.0, ge=1.0, description="Capacidade de carga do veículo")
    vehicle_speed: float = Field(40.0, ge=1.0, description="Velocidade média do veículo (km/h)")
    vehicle_max_distance: float = Field(200.0, ge=1.0, description="Autonomia máxima do veículo (km)")
    
    # Configuração do Cenário
    scenario: str = Field("large", pattern="^(small|medium|large|critical|custom)$", description="Cenário de teste (small, medium, large, critical)")
    
    # Pesos da Função de Fitness (Multi-objetivo)
    w_distance: float = Field(1.0, ge=0.0)
    w_priority: float = Field(10.0, ge=0.0)
    w_capacity: float = Field(100.0, ge=0.0)
    w_autonomy: float = Field(100.0, ge=0.0)
    w_window: float = Field(50.0, ge=0.0)
    
    # Critérios de Parada
    stagnation_limit: int = Field(50, ge=5, description="Limite de gerações sem melhoria")
    
    # Configuração de Inicialização
    heuristic_init_ratio: float = Field(0.2, ge=0.0, le=1.0, description="Proporção da população iniciada com heurística")

@app.post("/run")
async def run_experiment(config: ExperimentConfig, background_tasks: BackgroundTasks):
    """Cria e inicia um novo experimento."""
    try:
        # Pydantic converte Enums para seriais, mas precisamos garantir que o dict passado
        # para o manager seja compatível com o que ele espera (geralmente strings dos valores dos enums ou objetos enum)
        # O ExperimentManager usa GAConfig que espera Enums. O Pydantic Validation garante que os inputs são válidos.
        # Vamos passar o dict com .model_dump(mode='json') para transformar Enums em strings para o banco de dados.
        
        config_dict = config.model_dump(mode='json')
        exp = manager.create_experiment(config_dict)
        background_tasks.add_task(manager.run_experiment_background, exp.id)
        return {"id": exp.id, "status": "pending", "message": "Experimento iniciado."}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/experiments")
def list_experiments():
    """Lista experimentos recentes."""
    return manager.list_experiments()

@app.get("/experiments/latest")
def get_latest_experiment():
    """Retorna a configuração do último experimento."""
    exps = manager.list_experiments(limit=1)
    if not exps:
        return {}
    return exps[0]

@app.get("/experiments/{experiment_id}")
def get_experiment(experiment_id: int):
    """Obtém detalhes de um experimento."""
    exp = manager.get_experiment(experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experimento não encontrado")
    return exp

@app.delete("/experiments/all")
def delete_all_experiments():
    success = manager.delete_all_experiments()
    if not success:
        raise HTTPException(status_code=500, detail="Erro ao limpar histórico")
    return {"message": "Histórico limpo com sucesso"}

@app.delete("/experiments/failed")
def delete_failed_experiments():
    success = manager.delete_failed_experiments()
    if not success:
        raise HTTPException(status_code=500, detail="Erro ao limpar experimentos falhados")
    return {"message": "Experimentos falhados removidos"}

@app.delete("/experiments/{experiment_id}")
def delete_experiment(experiment_id: int):
    success = manager.delete_experiment(experiment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Experimento não encontrado ou erro ao deletar")
    return {"message": f"Experimento {experiment_id} removido"}

@app.get("/scenarios/{scenario_name}")
def get_scenario_preview(scenario_name: str):
    """Retorna os pontos do cenário para preview."""
    try:
        data = manager.get_scenario_data(scenario_name)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

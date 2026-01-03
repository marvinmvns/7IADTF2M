from fastapi.testclient import TestClient
from src.api.main import app
from unittest.mock import patch

client = TestClient(app)

def test_read_main():
    response = client.get("/experiments")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@patch('src.controllers.experiment_manager.ExperimentManager.create_experiment')
@patch('src.controllers.experiment_manager.ExperimentManager.run_experiment_background')
def test_run_endpoint(mock_run, mock_create):
    mock_create.return_value.id = 1
    
    payload = {
        "population_size": 100,
        "max_generations": 50,
        "crossover_method": "order_crossover", # Valid enum value
        "selection_method": "tournament"
    }
    
    response = client.post("/run", json=payload)
    
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert mock_run.called

@patch('src.controllers.experiment_manager.ExperimentManager.create_experiment')
@patch('src.controllers.experiment_manager.ExperimentManager.run_experiment_background')
def test_run_endpoint_all_options(mock_run, mock_create):
    """Testa endpoint com todas as opções de enum para garantir validação."""
    mock_create.return_value.id = 2
    
    payload = {
        "population_size": 50,
        "max_generations": 100,
        "crossover_rate": 0.8,
        "mutation_rate": 0.2,
        "selection_method": "roulette_wheel",
        "crossover_method": "partially_mapped_crossover",
        "mutation_method": "swap",
        "replacement_strategy": "steady_state",
        "fitness_type": "distance_only",
        "num_vehicles": 5,
        "vehicle_capacity": 150.0,
        "vehicle_speed": 60.0,
        "vehicle_max_distance": 300.0,
        "scenario": "medium",
        "elite_size": 4,
        "w_distance": 1.0,
        "w_priority": 5.0,
        "w_capacity": 50.0,
        "w_autonomy": 50.0,
        "w_window": 20.0,
        "stagnation_limit": 20,
        "heuristic_init_ratio": 0.5,
        "tournament_size": 4,
        "truncation_threshold": 0.7,
        "boltzmann_temperature": 50.0,
        "steady_state_ratio": 0.3
    }
    
    response = client.post("/run", json=payload)
    assert response.status_code == 200
    assert response.json()["id"] == 2

def test_get_scenario_preview():
    """Testa o endpoint de preview de cenários."""
    response = client.get("/scenarios/small")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "lat" in data[0]
    assert "lon" in data[0]
    assert "priority" in data[0]

def test_run_endpoint_invalid_enum():
    """Testa erro de validação com enum inválido."""
    payload = {
        "crossover_method": "invalid_method_name"
    }
    response = client.post("/run", json=payload)
    assert response.status_code == 422 # Erro de validação Pydantic
@patch('src.controllers.experiment_manager.ExperimentManager.create_experiment')
def test_run_endpoint_hybrid(mock_create):
    """Testa se os métodos híbridos são aceitos pela API."""
    mock_create.return_value.id = 3
    payload = {
        "crossover_method": "hybrid",
        "mutation_method": "hybrid"
    }
    response = client.post("/run", json=payload)
    assert response.status_code == 200
    assert response.json()["id"] == 3

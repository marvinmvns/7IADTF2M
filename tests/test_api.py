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

def test_get_default_config():
    """Testa endpoint de configuração padrão."""
    response = client.get("/config/defaults")
    assert response.status_code == 200
    data = response.json()

    # Verifica se todas as chaves necessárias estão presentes
    required_keys = [
        "population_size", "max_generations", "crossover_rate", "mutation_rate",
        "selection_method", "crossover_method", "mutation_method",
        "replacement_strategy", "fitness_type",
        "num_vehicles", "vehicle_capacity", "vehicle_speed", "vehicle_max_distance",
        "scenario", "w_distance", "w_priority", "w_capacity", "w_autonomy", "w_window",
        "stagnation_limit", "heuristic_init_ratio",
        "tournament_size", "elite_size", "truncation_threshold",
        "boltzmann_temperature", "steady_state_ratio"
    ]

    for key in required_keys:
        assert key in data, f"Chave {key} não encontrada na configuração padrão"

    # Verifica tipos de dados
    assert isinstance(data["population_size"], int)
    assert isinstance(data["max_generations"], int)
    assert isinstance(data["crossover_rate"], float)
    assert isinstance(data["mutation_rate"], float)
    assert isinstance(data["num_vehicles"], int)
    assert isinstance(data["vehicle_capacity"], float)
    assert isinstance(data["selection_method"], str)
    assert isinstance(data["scenario"], str)

    # Verifica valores razoáveis
    assert data["population_size"] > 0
    assert data["max_generations"] > 0
    assert 0.0 <= data["crossover_rate"] <= 1.0
    assert 0.0 <= data["mutation_rate"] <= 1.0
    assert data["num_vehicles"] > 0

def test_get_config_options():
    """Testa endpoint de opções de configuração."""
    response = client.get("/config/options")
    assert response.status_code == 200
    data = response.json()

    # Verifica se todas as listas de opções estão presentes
    required_lists = [
        "scenarios", "selection_methods", "crossover_methods",
        "mutation_methods", "replacement_strategies", "fitness_types"
    ]

    for key in required_lists:
        assert key in data, f"Lista {key} não encontrada nas opções"
        assert isinstance(data[key], list), f"{key} deveria ser uma lista"
        assert len(data[key]) > 0, f"{key} não deveria estar vazia"

    # Verifica se opções específicas estão presentes
    assert "small" in data["scenarios"]
    assert "medium" in data["scenarios"]
    assert "large" in data["scenarios"]

    assert "tournament" in data["selection_methods"]
    assert "order_crossover" in data["crossover_methods"]
    assert "inversion" in data["mutation_methods"]

    # Verifica se API URL e logo path estão presentes
    assert "api_url" in data
    assert "logo_path" in data
    assert isinstance(data["api_url"], str)
    assert isinstance(data["logo_path"], str)

def test_config_defaults_match_run_endpoint():
    """Testa se a configuração padrão pode ser usada no endpoint /run."""
    defaults_response = client.get("/config/defaults")
    assert defaults_response.status_code == 200
    defaults = defaults_response.json()

    # Remove campos que são strings (enums) e adiciona como estão
    payload = {
        "population_size": defaults["population_size"],
        "max_generations": defaults["max_generations"],
        "crossover_rate": defaults["crossover_rate"],
        "mutation_rate": defaults["mutation_rate"],
        "selection_method": defaults["selection_method"],
        "crossover_method": defaults["crossover_method"],
        "mutation_method": defaults["mutation_method"],
        "replacement_strategy": defaults["replacement_strategy"],
        "fitness_type": defaults["fitness_type"],
        "num_vehicles": defaults["num_vehicles"],
        "vehicle_capacity": defaults["vehicle_capacity"],
        "vehicle_speed": defaults["vehicle_speed"],
        "vehicle_max_distance": defaults["vehicle_max_distance"],
        "scenario": defaults["scenario"],
        "w_distance": defaults["w_distance"],
        "w_priority": defaults["w_priority"],
        "w_capacity": defaults["w_capacity"],
        "w_autonomy": defaults["w_autonomy"],
        "w_window": defaults["w_window"],
        "stagnation_limit": defaults["stagnation_limit"],
        "heuristic_init_ratio": defaults["heuristic_init_ratio"],
        "tournament_size": defaults["tournament_size"],
        "elite_size": defaults["elite_size"],
        "truncation_threshold": defaults["truncation_threshold"],
        "boltzmann_temperature": defaults["boltzmann_temperature"],
        "steady_state_ratio": defaults["steady_state_ratio"]
    }

    with patch('src.controllers.experiment_manager.ExperimentManager.create_experiment') as mock_create, \
         patch('src.controllers.experiment_manager.ExperimentManager.run_experiment_background'):
        mock_create.return_value.id = 99
        response = client.post("/run", json=payload)
        assert response.status_code == 200, f"Config padrão falhou no /run: {response.text}"

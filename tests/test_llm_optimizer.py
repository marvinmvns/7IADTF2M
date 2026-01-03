"""
Testes para o otimizador LLM
"""
import pytest
from unittest.mock import patch, MagicMock


class TestLLMOptimizer:
    """Testes para o loop de otimização"""
    
    def test_compare_fitness_calculates_percentage(self):
        """Deve calcular % de melhoria corretamente"""
        from src.llm.optimizer import compare_fitness
        
        # Melhoria (fitness menor = melhor)
        old_fitness = 6441.75
        new_fitness = 6200.50
        
        pct = compare_fitness(old_fitness, new_fitness)
        
        assert pct < 0  # Negativo = melhoria
        assert abs(pct - (-3.74)) < 0.1  # Aproximadamente -3.74%
    
    def test_compare_fitness_detects_regression(self):
        """Deve detectar piora no fitness"""
        from src.llm.optimizer import compare_fitness
        
        old_fitness = 6200.50
        new_fitness = 6500.00
        
        pct = compare_fitness(old_fitness, new_fitness)
        
        assert pct > 0  # Positivo = piora
    
    def test_optimization_stops_at_max_iterations(self):
        """Deve parar ao atingir máximo de iterações"""
        from src.llm.optimizer import LLMOptimizer
        
        optimizer = LLMOptimizer(max_iterations=3)
        
        # Mock do adapter
        mock_adapter = MagicMock()
        mock_adapter.suggest_params.return_value = {"population_size": 100}
        
        # Mock da API
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = {
                "id": 1,
                "best_fitness": 6000.0
            }
            mock_post.return_value.status_code = 200
            
            results = optimizer.run(
                base_params={"population_size": 50},
                base_fitness=6500.0,
                adapter=mock_adapter
            )
            
            assert len(results) <= 3
    
    def test_optimization_tracks_best_result(self):
        """Deve rastrear o melhor resultado"""
        from src.llm.optimizer import LLMOptimizer
        
        optimizer = LLMOptimizer(max_iterations=2)
        
        mock_adapter = MagicMock()
        mock_adapter.suggest_params.side_effect = [
            {"population_size": 80},
            {"population_size": 100}
        ]
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.side_effect = [
                {"id": 1, "best_fitness": 6200.0},
                {"id": 2, "best_fitness": 5800.0}
            ]
            mock_post.return_value.status_code = 200
            
            with patch.object(optimizer, '_wait_for_completion') as mock_wait:
                mock_wait.side_effect = [
                    {"best_fitness": 6200.0},
                    {"best_fitness": 5800.0}
                ]
                
                results = optimizer.run(
                    base_params={},
                    base_fitness=6500.0,
                    adapter=mock_adapter
                )
                
                best = optimizer.get_best()
                
                assert best["fitness"] == 5800.0


class TestAPIIntegration:
    """Testes de integração com a API do GA"""
    
    def test_call_api_with_new_params(self):
        """Deve chamar API /run com novos parâmetros"""
        from src.llm.optimizer import call_ga_api
        
        new_params = {
            "population_size": 100,
            "mutation_rate": 0.15,
            "scenario": "small"
        }
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = {"id": 123}
            mock_post.return_value.status_code = 200
            
            result = call_ga_api(new_params, api_url="http://localhost:8000")
            
            mock_post.assert_called_once()
            assert "id" in result
    
    def test_wait_for_experiment_completion(self):
        """Deve aguardar conclusão do experimento"""
        from src.llm.optimizer import wait_for_experiment
        
        with patch('requests.get') as mock_get:
            # Primeiro: running, Segundo: completed
            mock_get.return_value.json.side_effect = [
                {"status": "running"},
                {"status": "completed", "best_fitness": 5500.0}
            ]
            mock_get.return_value.status_code = 200
            
            with patch('time.sleep'):
                result = wait_for_experiment(exp_id=1, api_url="http://localhost:8000")
            
            assert result["status"] == "completed"
            assert result["best_fitness"] == 5500.0

"""
LLM Optimizer - Orquestra loop de otimização do GA via LLM
"""
import requests
import time
from typing import List, Dict, Optional
from .adapters import LLMAdapter


def compare_fitness(old_fitness: float, new_fitness: float) -> float:
    """Calcula % de mudança no fitness (negativo = melhoria)"""
    if old_fitness == 0:
        return 0
    return ((new_fitness - old_fitness) / old_fitness) * 100


def call_ga_api(params: dict, api_url: str = "http://localhost:8000") -> dict:
    """Chama API /run com novos parâmetros"""
    try:
        resp = requests.post(f"{api_url}/run", json=params, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"Erro ao chamar API: {e}")
    return {}


def wait_for_experiment(exp_id: int, api_url: str = "http://localhost:8000", 
                        max_wait: int = 300, poll_interval: int = 2) -> dict:
    """Aguarda conclusão do experimento com polling"""
    start = time.time()
    while time.time() - start < max_wait:
        try:
            resp = requests.get(f"{api_url}/experiments/{exp_id}", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('status') == 'completed':
                    return data
                if data.get('status') == 'error':
                    return data
        except:
            pass
        time.sleep(poll_interval)
    return {"status": "timeout"}


class LLMOptimizer:
    """Orquestra loop de otimização usando LLM"""
    
    def __init__(self, max_iterations: int = 10, api_url: str = "http://localhost:8000"):
        self.max_iterations = max_iterations
        self.api_url = api_url
        self.history: List[dict] = []
        self.best_result: Optional[dict] = None
        self._stop_requested = False
    
    def stop(self):
        """Para o loop de otimização"""
        self._stop_requested = True
    
    def run(self, base_params: dict, base_fitness: float, 
            adapter: LLMAdapter, callback=None) -> List[dict]:
        """
        Executa loop de otimização.
        
        Args:
            base_params: Parâmetros iniciais
            base_fitness: Fitness inicial
            adapter: Adapter LLM configurado
            callback: Função chamada a cada iteração (iteration, result)
        
        Returns:
            Lista de resultados de cada iteração
        """
        self.history = []
        self.best_result = {"params": base_params, "fitness": base_fitness}
        self._stop_requested = False
        
        current_params = base_params.copy()
        current_fitness = base_fitness
        
        for i in range(self.max_iterations):
            if self._stop_requested:
                break
            
            # Monta contexto para LLM
            context = {
                "fitness": current_fitness,
                "params": current_params,
                "history": self.history
            }
            
            # Obtém sugestão do LLM
            new_params = adapter.suggest_params(context)
            if not new_params:
                continue
            
            # Mescla com parâmetros base e valida contra domínios
            from .domains import GADomains

            merged_params = current_params.copy()
            # Atualiza com novos parâmetros sugeridos
            merged_params.update(new_params)

            # Valida e corrige parâmetros
            merged_params = GADomains.validate_params(merged_params)
            
            # Chama API
            api_result = call_ga_api(merged_params, self.api_url)
            if not api_result.get('id'):
                continue
            
            # Aguarda conclusão
            exp_result = wait_for_experiment(api_result['id'], self.api_url)
            if exp_result.get('status') != 'completed':
                continue
            
            new_fitness = exp_result.get('best_fitness', float('inf'))
            change_pct = compare_fitness(current_fitness, new_fitness)
            
            # Registra resultado
            result = {
                "iteration": i + 1,
                "old_fitness": current_fitness,
                "new_fitness": new_fitness,
                "change_pct": change_pct,
                "improved": new_fitness < current_fitness,
                "params": merged_params,
                "experiment_id": api_result['id']
            }
            self.history.append(result)
            
            # Atualiza melhor se melhorou
            if new_fitness < self.best_result["fitness"]:
                self.best_result = {"params": merged_params, "fitness": new_fitness}
                current_params = merged_params
                current_fitness = new_fitness
            
            # Callback para UI
            if callback:
                callback(i + 1, result)
        
        return self.history
    
    def get_best(self) -> dict:
        """Retorna melhor resultado encontrado"""
        return self.best_result or {}
    
    def get_improvement(self) -> float:
        """Retorna % de melhoria total"""
        if not self.history:
            return 0
        initial = self.history[0].get('old_fitness', 0)
        best = self.best_result.get('fitness', initial)
        return compare_fitness(initial, best)

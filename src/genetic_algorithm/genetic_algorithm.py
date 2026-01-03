"""
Módulo Principal do Algoritmo Genético
======================================

Este módulo implementa o framework principal do algoritmo genético
para otimização de rotas de entrega de medicamentos e insumos.

O algoritmo segue o fluxo clássico:
1. Inicialização da população
2. Avaliação de fitness
3. Seleção de pais
4. Crossover
5. Mutação
6. Substituição da população
7. Repetir até critério de parada

Referências:
-----------
- Holland, J. H. (1975). Adaptation in Natural and Artificial Systems.
- Goldberg, D. E. (1989). Genetic Algorithms in Search, Optimization, and Machine Learning.
- Mitchell, M. (1998). An Introduction to Genetic Algorithms.
"""

import time
import random
from typing import List, Optional, Callable, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .chromosome import Chromosome, DeliveryPoint, Vehicle
from .population import Population, PopulationStats
from .selection import SelectionOperator, SelectionMethod, create_selector
from .crossover import CrossoverOperator, CrossoverMethod, create_crossover
from .mutation import MutationOperator, MutationMethod, create_mutation
from .fitness import FitnessFunction, FitnessType, create_fitness


class ReplacementStrategy(Enum):
    """Estratégias de substituição da população."""
    GENERATIONAL = "generational"  # Substitui toda a população
    STEADY_STATE = "steady_state"  # Substitui apenas alguns indivíduos
    ELITIST = "elitist"  # Preserva os melhores


@dataclass
class GAConfig:
    """
    Configuração do Algoritmo Genético.
    
    Centraliza todos os parâmetros configuráveis do AG.
    """
    # Parâmetros da população
    population_size: int = 100
    
    # Parâmetros de evolução
    max_generations: int = 500
    crossover_rate: float = 0.9
    mutation_rate: float = 0.1
    
    # Estratégias
    selection_method: SelectionMethod = SelectionMethod.TOURNAMENT
    crossover_method: CrossoverMethod = CrossoverMethod.OX
    mutation_method: MutationMethod = MutationMethod.INVERSION
    replacement_strategy: ReplacementStrategy = ReplacementStrategy.ELITIST
    fitness_type: FitnessType = FitnessType.WEIGHTED_MULTI
    
    # Parâmetros de elitismo
    elite_size: int = 2
    
    # Parâmetros específicos
    tournament_size: int = 3
    
    # Critérios de parada
    stagnation_limit: int = 50  # Gerações sem melhoria
    target_fitness: Optional[float] = None
    
    # Inicialização
    heuristic_init_ratio: float = 0.2  # Fração com heurística
    
    # Logging
    verbose: bool = True
    log_interval: int = 10


@dataclass
class GAResult:
    """
    Resultado da execução do Algoritmo Genético.
    
    Armazena informações sobre a execução e a melhor solução encontrada.
    """
    best_chromosome: Chromosome
    best_fitness: float
    generations_run: int
    execution_time: float
    history: List[PopulationStats]
    convergence_generation: int
    final_population: List[Chromosome]
    config: GAConfig


class GeneticAlgorithm:
    """
    Implementação do Algoritmo Genético para Otimização de Rotas.
    
    Esta classe coordena todos os componentes do AG:
    - População de cromossomos
    - Operadores de seleção, crossover e mutação
    - Função de fitness
    - Estratégia de substituição
    
    Attributes:
        config: Configuração do algoritmo
        population: População atual
        selector: Operador de seleção
        crossover: Operador de crossover
        mutator: Operador de mutação
        fitness_func: Função de fitness
    """
    
    def __init__(self, config: GAConfig,
                 delivery_points: List[DeliveryPoint],
                 vehicles: Optional[List[Vehicle]] = None,
                 depot_index: int = 0):
        """
        Inicializa o Algoritmo Genético.
        
        Args:
            config: Configuração do algoritmo
            delivery_points: Lista de pontos de entrega
            vehicles: Lista de veículos disponíveis
            depot_index: Índice do ponto de depósito
        """
        self.config = config
        self.delivery_points = delivery_points
        self.vehicles = vehicles or [Vehicle(id=1)]
        self.depot_index = depot_index
        
        # Inicializa operadores
        self._init_operators()
        
        # Inicializa população
        self.population = Population(
            size=config.population_size,
            delivery_points=delivery_points,
            vehicles=vehicles,
            depot_index=depot_index
        )
        
        # Variáveis de controle
        self._best_ever: Optional[Chromosome] = None
        self._stagnation_counter = 0
        self._callbacks: List[Callable] = []
    
    def _init_operators(self):
        """Inicializa os operadores genéticos."""
        # Seleção
        selector_kwargs = {}
        if self.config.selection_method == SelectionMethod.TOURNAMENT:
            selector_kwargs['tournament_size'] = self.config.tournament_size
        
        self.selector = create_selector(
            self.config.selection_method,
            **selector_kwargs
        )
        
        # Crossover
        self.crossover = create_crossover(
            self.config.crossover_method,
            crossover_rate=self.config.crossover_rate
        )
        
        # Mutação
        self.mutator = create_mutation(
            self.config.mutation_method,
            mutation_rate=self.config.mutation_rate
        )
        
        # Fitness
        self.fitness_func = create_fitness(self.config.fitness_type)
    
    def add_callback(self, callback: Callable[[int, Population, Chromosome], None]):
        """
        Adiciona callback para ser chamado a cada geração.
        
        Args:
            callback: Função(geração, população, melhor_cromossomo)
        """
        self._callbacks.append(callback)
    
    def run(self) -> GAResult:
        """
        Executa o algoritmo genético.
        
        Returns:
            Objeto GAResult com resultados da execução
        """
        start_time = time.time()
        
        # Inicializa população
        if self.config.heuristic_init_ratio > 0:
            self.population.initialize_heuristic(self.config.heuristic_init_ratio)
        else:
            self.population.initialize_random()
        
        # Avalia população inicial
        self.population.evaluate(self.fitness_func.evaluate)
        self._best_ever = self.population.get_best().copy()
        self.initial_best_fitness = self._best_ever.fitness
        
        # Capture initial detailed metrics
        initial_components = self.fitness_func.get_components(self._best_ever)
        self.initial_total_distance = initial_components.total_distance
        self.initial_components_dict = {
            'total_distance': initial_components.total_distance,
            'priority_penalty': initial_components.priority_penalty,
            'capacity_violation': initial_components.capacity_violation,
            'autonomy_violation': initial_components.autonomy_violation,
            'time_window_violation': initial_components.time_window_violation
        }
        
        convergence_gen = 0
        
        if self.config.verbose:
            print(f"Algoritmo Genético iniciado")
            print(f"  População: {self.config.population_size}")
            print(f"  Melhor Fitness Inicial: {self.initial_best_fitness:.4f}")
            print(f"  Seleção: {self.selector.name}")
            print(f"  Crossover: {self.crossover.name}")
            print(f"  Mutação: {self.mutator.name}")
            print(f"  Fitness: {self.fitness_func.name}")
            print("-" * 50)
        
        # Loop principal de evolução
        for generation in range(self.config.max_generations):
            self.population.generation = generation
            
            # Atualiza penalidades se necessário
            if hasattr(self.fitness_func, 'set_generation'):
                self.fitness_func.set_generation(generation)
            
            # Evolui uma geração
            self._evolve_generation()
            
            # Avalia nova população
            self.population.evaluate(self.fitness_func.evaluate)
            
            # Atualiza melhor solução
            current_best = self.population.get_best()
            if current_best.fitness < self._best_ever.fitness:
                self._best_ever = current_best.copy()
                self._stagnation_counter = 0
                convergence_gen = generation
            else:
                self._stagnation_counter += 1
            
            # Calcula estatísticas
            stats = self.population.calculate_stats()
            
            # Logging
            if self.config.verbose and generation % self.config.log_interval == 0:
                self._log_generation(generation, stats)
            
            # Callbacks
            for callback in self._callbacks:
                callback(generation, self.population, self._best_ever)
            
            # Verifica critérios de parada
            if self._should_stop(generation):
                if self.config.verbose:
                    print(f"\nParada antecipada na geração {generation}")
                break
        
        execution_time = time.time() - start_time
        
        if self.config.verbose:
            print("-" * 50)
            print(f"Execução concluída em {execution_time:.2f}s")
            print(f"Melhor fitness: {self._best_ever.fitness:.4f}")
        
        return GAResult(
            best_chromosome=self._best_ever,
            best_fitness=self._best_ever.fitness,
            generations_run=self.population.generation + 1,
            execution_time=execution_time,
            history=self.population.history,
            convergence_generation=convergence_gen,
            final_population=[c.copy() for c in self.population.chromosomes],
            config=self.config
        )
    
    def _evolve_generation(self):
        """Evolui a população por uma geração."""
        new_population = []
        
        # Preserva elite
        if self.config.replacement_strategy == ReplacementStrategy.ELITIST:
            elite = self.population.get_elite(self.config.elite_size)
            new_population.extend(elite)
        
        # Gera novos indivíduos
        while len(new_population) < self.config.population_size:
            # Seleção
            parents = self.selector.select(
                self.population.chromosomes, 
                num_parents=2
            )
            
            # Crossover
            child1, child2 = self.crossover.crossover(parents[0], parents[1])
            
            # Mutação
            child1 = self.mutator.mutate(child1)
            child2 = self.mutator.mutate(child2)
            
            # Adiciona à nova população
            new_population.append(child1)
            if len(new_population) < self.config.population_size:
                new_population.append(child2)
        
        # Substitui população
        self.population.replace(new_population[:self.config.population_size])
    
    def _should_stop(self, generation: int) -> bool:
        """
        Verifica se deve parar a execução.
        
        Args:
            generation: Geração atual
        
        Returns:
            True se deve parar
        """
        # Verifica estagnação
        if self._stagnation_counter >= self.config.stagnation_limit:
            return True
        
        # Verifica fitness alvo
        if (self.config.target_fitness is not None and 
            self._best_ever.fitness <= self.config.target_fitness):
            return True
        
        return False
    
    def _log_generation(self, generation: int, stats: PopulationStats):
        """
        Registra informações da geração.
        
        Args:
            generation: Número da geração
            stats: Estatísticas da população
        """
        print(f"Gen {generation:4d} | "
              f"Best: {stats.best_fitness:10.2f} | "
              f"Avg: {stats.avg_fitness:10.2f} | "
              f"Worst: {stats.worst_fitness:10.2f} | "
              f"Div: {stats.diversity:.3f}")
    
    def get_best_solution(self) -> Optional[Chromosome]:
        """Retorna a melhor solução encontrada."""
        return self._best_ever
    
    def get_solution_details(self) -> Dict[str, Any]:
        """
        Retorna detalhes da melhor solução.
        
        Returns:
            Dicionário com informações detalhadas
        """
        if self._best_ever is None:
            return {}
        
        routes = self._best_ever.get_routes()
        components = self.fitness_func.get_components(self._best_ever)
        
        
        # Compila resumo do histórico se disponível
        history_summary = []
        if hasattr(self.population, 'history') and self.population.history:
            for stat in self.population.history:
                history_summary.append({
                    "generation": stat.generation,
                    "best_fitness": stat.best_fitness,
                    "avg_fitness": stat.avg_fitness,
                    "diversity": stat.diversity
                })

        details = {
            'fitness': self._best_ever.fitness,
            'initial_fitness': getattr(self, 'initial_best_fitness', None),
            'initial_components': getattr(self, 'initial_components_dict', {}),
            'total_distance': components.total_distance,
            'final_components': {
                'total_distance': components.total_distance,
                'priority_penalty': components.priority_penalty,
                'capacity_violation': components.capacity_violation,
                'autonomy_violation': components.autonomy_violation,
                'time_window_violation': components.time_window_violation
            },
            'num_routes': len(routes),
            'history_summary': history_summary,
            'routes': []
        }
        
        for i, route in enumerate(routes):
            route_info = {
                'route_id': i + 1,
                'vehicle_id': route.vehicle.id,
                'num_stops': len(route.points),
                'distance': route.total_distance,
                'demand': route.total_demand,
                'load': route.total_demand, # Alias para compatibilidade
                'capacity_used': route.total_demand / route.vehicle.capacity * 100,
                'stops': [
                    {
                        "id": p.id,
                        "name": p.name,
                        "priority": p.priority,
                        "demand": p.demand,
                        "arrival_time": 0 # TODO: Implementar tempo
                    }
                    for p in route.points
                ]
            }
            details['routes'].append(route_info)
        
        return details


class GAExperiment:
    """
    Classe para executar experimentos com diferentes configurações.
    
    Permite comparar diferentes combinações de operadores e parâmetros.
    """
    
    def __init__(self, delivery_points: List[DeliveryPoint],
                 vehicles: Optional[List[Vehicle]] = None,
                 depot_index: int = 0):
        """
        Inicializa o experimento.
        
        Args:
            delivery_points: Pontos de entrega
            vehicles: Veículos disponíveis
            depot_index: Índice do depósito
        """
        self.delivery_points = delivery_points
        self.vehicles = vehicles
        self.depot_index = depot_index
        self.results: List[Tuple[str, GAResult]] = []
    
    def run_experiment(self, name: str, config: GAConfig) -> GAResult:
        """
        Executa um experimento com configuração específica.
        
        Args:
            name: Nome do experimento
            config: Configuração do AG
        
        Returns:
            Resultado do experimento
        """
        print(f"\n{'='*60}")
        print(f"Experimento: {name}")
        print(f"{'='*60}")
        
        ga = GeneticAlgorithm(
            config=config,
            delivery_points=self.delivery_points,
            vehicles=self.vehicles,
            depot_index=self.depot_index
        )
        
        result = ga.run()
        self.results.append((name, result))
        
        return result
    
    def compare_selection_methods(self, base_config: GAConfig) -> List[GAResult]:
        """
        Compara diferentes métodos de seleção.
        
        Args:
            base_config: Configuração base
        
        Returns:
            Lista de resultados
        """
        methods = [
            SelectionMethod.ROULETTE_WHEEL,
            SelectionMethod.TOURNAMENT,
            SelectionMethod.RANK,
            SelectionMethod.SUS,
            SelectionMethod.BOLTZMANN,
        ]
        
        results = []
        for method in methods:
            config = GAConfig(
                population_size=base_config.population_size,
                max_generations=base_config.max_generations,
                crossover_rate=base_config.crossover_rate,
                mutation_rate=base_config.mutation_rate,
                selection_method=method,
                crossover_method=base_config.crossover_method,
                mutation_method=base_config.mutation_method,
                verbose=False
            )
            result = self.run_experiment(f"Selection: {method.value}", config)
            results.append(result)
        
        return results
    
    def compare_crossover_methods(self, base_config: GAConfig) -> List[GAResult]:
        """
        Compara diferentes métodos de crossover.
        
        Args:
            base_config: Configuração base
        
        Returns:
            Lista de resultados
        """
        methods = [
            CrossoverMethod.PMX,
            CrossoverMethod.OX,
            CrossoverMethod.CX,
            CrossoverMethod.ERX,
            CrossoverMethod.SCX,
        ]
        
        results = []
        for method in methods:
            config = GAConfig(
                population_size=base_config.population_size,
                max_generations=base_config.max_generations,
                crossover_rate=base_config.crossover_rate,
                mutation_rate=base_config.mutation_rate,
                selection_method=base_config.selection_method,
                crossover_method=method,
                mutation_method=base_config.mutation_method,
                verbose=False
            )
            result = self.run_experiment(f"Crossover: {method.value}", config)
            results.append(result)
        
        return results
    
    def compare_mutation_methods(self, base_config: GAConfig) -> List[GAResult]:
        """
        Compara diferentes métodos de mutação.
        
        Args:
            base_config: Configuração base
        
        Returns:
            Lista de resultados
        """
        methods = [
            MutationMethod.SWAP,
            MutationMethod.INVERSION,
            MutationMethod.SCRAMBLE,
            MutationMethod.INSERT,
            MutationMethod.DISPLACEMENT,
            MutationMethod.HYBRID,
        ]
        
        results = []
        for method in methods:
            config = GAConfig(
                population_size=base_config.population_size,
                max_generations=base_config.max_generations,
                crossover_rate=base_config.crossover_rate,
                mutation_rate=base_config.mutation_rate,
                selection_method=base_config.selection_method,
                crossover_method=base_config.crossover_method,
                mutation_method=method,
                verbose=False
            )
            result = self.run_experiment(f"Mutation: {method.value}", config)
            results.append(result)
        
        return results
    
    def get_summary(self) -> str:
        """
        Gera resumo dos experimentos.
        
        Returns:
            String com resumo formatado
        """
        if not self.results:
            return "Nenhum experimento executado."
        
        lines = [
            "\n" + "=" * 70,
            "RESUMO DOS EXPERIMENTOS",
            "=" * 70,
            f"{'Experimento':<30} {'Fitness':>12} {'Gerações':>10} {'Tempo':>10}",
            "-" * 70
        ]
        
        for name, result in sorted(self.results, key=lambda x: x[1].best_fitness):
            lines.append(
                f"{name:<30} {result.best_fitness:>12.2f} "
                f"{result.generations_run:>10} {result.execution_time:>9.2f}s"
            )
        
        lines.append("=" * 70)
        
        return "\n".join(lines)

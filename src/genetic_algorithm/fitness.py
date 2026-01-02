"""
Módulo de Funções de Fitness
============================

Este módulo implementa funções de fitness para avaliar a qualidade
das soluções no problema de otimização de rotas hospitalares.

A função de fitness considera múltiplos objetivos:
- Distância total percorrida (minimizar)
- Prioridade das entregas (medicamentos críticos primeiro)
- Violações de restrições (capacidade, autonomia, janelas de tempo)

Referências:
-----------
- Deb, K. (2001). Multi-Objective Optimization using Evolutionary Algorithms.
- Coello, C. A. C. (2006). Evolutionary multi-objective optimization.
"""

import numpy as np
from typing import List, Callable, Optional, Tuple
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass

from .chromosome import Chromosome, DeliveryPoint, Route


class FitnessType(Enum):
    """Tipos de função de fitness disponíveis."""
    DISTANCE_ONLY = "distance_only"
    WEIGHTED_MULTI = "weighted_multi_objective"
    PENALTY_BASED = "penalty_based"
    PRIORITY_AWARE = "priority_aware"


@dataclass
class FitnessComponents:
    """
    Componentes individuais do fitness.
    
    Armazena os valores de cada componente para análise detalhada.
    """
    total_distance: float
    priority_penalty: float
    capacity_violation: float
    autonomy_violation: float
    time_window_violation: float
    total_fitness: float


class FitnessFunction(ABC):
    """
    Classe base abstrata para funções de fitness.
    
    Define a interface comum que todas as funções de fitness
    devem implementar.
    """
    
    @abstractmethod
    def evaluate(self, chromosome: Chromosome) -> float:
        """
        Avalia o fitness de um cromossomo.
        
        Args:
            chromosome: Cromossomo a ser avaliado
        
        Returns:
            Valor de fitness (menor é melhor para minimização)
        """
        pass
    
    @abstractmethod
    def get_components(self, chromosome: Chromosome) -> FitnessComponents:
        """
        Retorna os componentes individuais do fitness.
        
        Args:
            chromosome: Cromossomo a ser avaliado
        
        Returns:
            Objeto FitnessComponents com valores detalhados
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Retorna o nome da função de fitness."""
        pass


class DistanceOnlyFitness(FitnessFunction):
    """
    Fitness baseado apenas na distância total.
    
    A função mais simples de fitness para o TSP, considerando
    apenas a distância total da rota.
    
    Fitness = Distância total da rota
    
    Características:
    - Simples e rápido de calcular
    - Não considera restrições
    - Adequado para TSP básico
    """
    
    @property
    def name(self) -> str:
        return "Distance Only Fitness"
    
    def evaluate(self, chromosome: Chromosome) -> float:
        """
        Calcula o fitness baseado na distância.
        
        Args:
            chromosome: Cromossomo a ser avaliado
        
        Returns:
            Distância total da rota
        """
        routes = chromosome.get_routes()
        
        if not routes:
            return float('inf')
        
        total_distance = sum(route.total_distance for route in routes)
        return total_distance
    
    def get_components(self, chromosome: Chromosome) -> FitnessComponents:
        """Retorna componentes do fitness."""
        distance = self.evaluate(chromosome)
        return FitnessComponents(
            total_distance=distance,
            priority_penalty=0.0,
            capacity_violation=0.0,
            autonomy_violation=0.0,
            time_window_violation=0.0,
            total_fitness=distance
        )


class WeightedMultiObjectiveFitness(FitnessFunction):
    """
    Fitness multi-objetivo com pesos.
    
    Combina múltiplos objetivos usando uma soma ponderada.
    Permite balancear diferentes aspectos da solução.
    
    Fitness = w1*distância + w2*prioridade + w3*violações
    
    Características:
    - Flexível e configurável
    - Permite trade-offs entre objetivos
    - Requer ajuste de pesos
    """
    
    def __init__(self, 
                 distance_weight: float = 1.0,
                 priority_weight: float = 10.0,
                 capacity_penalty: float = 100.0,
                 autonomy_penalty: float = 100.0,
                 time_window_penalty: float = 50.0):
        """
        Inicializa a função de fitness multi-objetivo.
        
        Args:
            distance_weight: Peso para distância
            priority_weight: Peso para penalidade de prioridade
            capacity_penalty: Penalidade por violação de capacidade
            autonomy_penalty: Penalidade por violação de autonomia
            time_window_penalty: Penalidade por violação de janela de tempo
        """
        self.distance_weight = distance_weight
        self.priority_weight = priority_weight
        self.capacity_penalty = capacity_penalty
        self.autonomy_penalty = autonomy_penalty
        self.time_window_penalty = time_window_penalty
    
    @property
    def name(self) -> str:
        return "Weighted Multi-Objective Fitness"
    
    def evaluate(self, chromosome: Chromosome) -> float:
        """
        Calcula o fitness multi-objetivo.
        
        Args:
            chromosome: Cromossomo a ser avaliado
        
        Returns:
            Valor de fitness ponderado
        """
        components = self.get_components(chromosome)
        return components.total_fitness
    
    def get_components(self, chromosome: Chromosome) -> FitnessComponents:
        """
        Calcula e retorna todos os componentes do fitness.
        
        Args:
            chromosome: Cromossomo a ser avaliado
        
        Returns:
            Objeto FitnessComponents com valores detalhados
        """
        routes = chromosome.get_routes()
        
        if not routes:
            return FitnessComponents(
                total_distance=float('inf'),
                priority_penalty=float('inf'),
                capacity_violation=float('inf'),
                autonomy_violation=float('inf'),
                time_window_violation=float('inf'),
                total_fitness=float('inf')
            )
        
        # Calcula distância total
        total_distance = sum(route.total_distance for route in routes)
        
        # Calcula penalidade de prioridade
        priority_penalty = self._calculate_priority_penalty(routes)
        
        # Calcula violações de restrições
        capacity_violation = self._calculate_capacity_violation(routes)
        autonomy_violation = self._calculate_autonomy_violation(routes)
        time_window_violation = self._calculate_time_window_violation(routes)
        
        # Calcula fitness total
        total_fitness = (
            self.distance_weight * total_distance +
            self.priority_weight * priority_penalty +
            self.capacity_penalty * capacity_violation +
            self.autonomy_penalty * autonomy_violation +
            self.time_window_penalty * time_window_violation
        )
        
        return FitnessComponents(
            total_distance=total_distance,
            priority_penalty=priority_penalty,
            capacity_violation=capacity_violation,
            autonomy_violation=autonomy_violation,
            time_window_violation=time_window_violation,
            total_fitness=total_fitness
        )
    
    def _calculate_priority_penalty(self, routes: List[Route]) -> float:
        """
        Calcula penalidade por não atender prioridades.
        
        Entregas de alta prioridade devem ser feitas primeiro.
        Penaliza quando entregas críticas aparecem tarde na rota.
        
        Args:
            routes: Lista de rotas
        
        Returns:
            Valor da penalidade de prioridade
        """
        penalty = 0.0
        
        for route in routes:
            for i, point in enumerate(route.points):
                # Prioridade 1 = crítico, 2 = urgente, 3 = regular
                # Penaliza se crítico não está no início
                if point.priority == 1:  # Crítico
                    penalty += i * 2.0  # Penalidade proporcional à posição
                elif point.priority == 2:  # Urgente
                    penalty += max(0, i - len(route.points) // 3) * 1.0
        
        return penalty
    
    def _calculate_capacity_violation(self, routes: List[Route]) -> float:
        """
        Calcula violação de capacidade dos veículos.
        
        Args:
            routes: Lista de rotas
        
        Returns:
            Soma das violações de capacidade
        """
        violation = 0.0
        
        for route in routes:
            excess = route.total_demand - route.vehicle.capacity
            if excess > 0:
                violation += excess
        
        return violation
    
    def _calculate_autonomy_violation(self, routes: List[Route]) -> float:
        """
        Calcula violação de autonomia dos veículos.
        
        Args:
            routes: Lista de rotas
        
        Returns:
            Soma das violações de autonomia
        """
        violation = 0.0
        
        for route in routes:
            excess = route.total_distance - route.vehicle.max_distance
            if excess > 0:
                violation += excess
        
        return violation
    
    def _calculate_time_window_violation(self, routes: List[Route]) -> float:
        """
        Calcula violação de janelas de tempo.
        
        Args:
            routes: Lista de rotas
        
        Returns:
            Soma das violações de janela de tempo
        """
        violation = 0.0
        
        for route in routes:
            current_time = 0.0  # Tempo de partida do depósito
            
            for i, point in enumerate(route.points):
                # Calcula tempo de chegada
                if i == 0:
                    travel_time = route.depot.distance_to(point) / route.vehicle.speed
                else:
                    travel_time = route.points[i-1].distance_to(point) / route.vehicle.speed
                
                current_time += travel_time
                
                # Verifica janela de tempo
                start, end = point.time_window
                if current_time < start:
                    # Chegou cedo, espera
                    current_time = start
                elif current_time > end:
                    # Chegou tarde, penaliza
                    violation += current_time - end
                
                # Adiciona tempo de serviço (assumindo 5 minutos por entrega)
                current_time += 5
        
        return violation


class PenaltyBasedFitness(FitnessFunction):
    """
    Fitness baseado em penalidades.
    
    Usa penalidades adaptativas que aumentam ao longo das gerações
    para forçar soluções viáveis.
    
    Características:
    - Penalidades aumentam com o tempo
    - Permite exploração inicial de soluções inviáveis
    - Converge para soluções viáveis
    """
    
    def __init__(self, 
                 base_penalty: float = 100.0,
                 penalty_growth_rate: float = 1.1):
        """
        Inicializa a função de fitness com penalidades.
        
        Args:
            base_penalty: Penalidade base para violações
            penalty_growth_rate: Taxa de crescimento da penalidade por geração
        """
        self.base_penalty = base_penalty
        self.penalty_growth_rate = penalty_growth_rate
        self.current_generation = 0
    
    @property
    def name(self) -> str:
        return "Penalty-Based Fitness"
    
    def set_generation(self, generation: int):
        """Define a geração atual para ajuste de penalidades."""
        self.current_generation = generation
    
    def evaluate(self, chromosome: Chromosome) -> float:
        """
        Calcula o fitness com penalidades adaptativas.
        
        Args:
            chromosome: Cromossomo a ser avaliado
        
        Returns:
            Valor de fitness com penalidades
        """
        components = self.get_components(chromosome)
        return components.total_fitness
    
    def get_components(self, chromosome: Chromosome) -> FitnessComponents:
        """Calcula componentes do fitness."""
        routes = chromosome.get_routes()
        
        if not routes:
            return FitnessComponents(
                total_distance=float('inf'),
                priority_penalty=0.0,
                capacity_violation=float('inf'),
                autonomy_violation=float('inf'),
                time_window_violation=0.0,
                total_fitness=float('inf')
            )
        
        # Distância total
        total_distance = sum(route.total_distance for route in routes)
        
        # Calcula penalidade adaptativa
        penalty_multiplier = self.base_penalty * (
            self.penalty_growth_rate ** self.current_generation
        )
        
        # Violações
        capacity_violation = 0.0
        autonomy_violation = 0.0
        
        for route in routes:
            cap_excess = max(0, route.total_demand - route.vehicle.capacity)
            capacity_violation += cap_excess
            
            dist_excess = max(0, route.total_distance - route.vehicle.max_distance)
            autonomy_violation += dist_excess
        
        # Fitness total
        total_fitness = total_distance + penalty_multiplier * (
            capacity_violation + autonomy_violation
        )
        
        return FitnessComponents(
            total_distance=total_distance,
            priority_penalty=0.0,
            capacity_violation=capacity_violation,
            autonomy_violation=autonomy_violation,
            time_window_violation=0.0,
            total_fitness=total_fitness
        )


class PriorityAwareFitness(FitnessFunction):
    """
    Fitness com consciência de prioridade.
    
    Especialmente projetado para o contexto hospitalar, onde
    medicamentos críticos devem ter prioridade absoluta.
    
    Características:
    - Prioriza entregas críticas
    - Penaliza fortemente atrasos em medicamentos urgentes
    - Considera urgência médica
    """
    
    def __init__(self,
                 critical_priority_weight: float = 100.0,
                 urgent_priority_weight: float = 50.0,
                 regular_priority_weight: float = 10.0):
        """
        Inicializa a função de fitness com prioridades.
        
        Args:
            critical_priority_weight: Peso para entregas críticas
            urgent_priority_weight: Peso para entregas urgentes
            regular_priority_weight: Peso para entregas regulares
        """
        self.critical_weight = critical_priority_weight
        self.urgent_weight = urgent_priority_weight
        self.regular_weight = regular_priority_weight
    
    @property
    def name(self) -> str:
        return "Priority-Aware Fitness"
    
    def evaluate(self, chromosome: Chromosome) -> float:
        """
        Calcula o fitness considerando prioridades.
        
        Args:
            chromosome: Cromossomo a ser avaliado
        
        Returns:
            Valor de fitness
        """
        components = self.get_components(chromosome)
        return components.total_fitness
    
    def get_components(self, chromosome: Chromosome) -> FitnessComponents:
        """Calcula componentes do fitness com prioridades."""
        routes = chromosome.get_routes()
        
        if not routes:
            return FitnessComponents(
                total_distance=float('inf'),
                priority_penalty=float('inf'),
                capacity_violation=0.0,
                autonomy_violation=0.0,
                time_window_violation=0.0,
                total_fitness=float('inf')
            )
        
        total_distance = 0.0
        priority_penalty = 0.0
        
        for route in routes:
            total_distance += route.total_distance
            
            # Calcula tempo acumulado e penalidade de prioridade
            current_time = 0.0
            
            for i, point in enumerate(route.points):
                # Tempo de viagem
                if i == 0:
                    travel_time = route.depot.distance_to(point) / route.vehicle.speed
                else:
                    travel_time = route.points[i-1].distance_to(point) / route.vehicle.speed
                
                current_time += travel_time
                
                # Penalidade baseada na prioridade e tempo de chegada
                if point.priority == 1:  # Crítico
                    # Penaliza qualquer atraso fortemente
                    priority_penalty += current_time * self.critical_weight / 100
                elif point.priority == 2:  # Urgente
                    priority_penalty += current_time * self.urgent_weight / 100
                else:  # Regular
                    priority_penalty += current_time * self.regular_weight / 100
                
                # Tempo de serviço
                current_time += 5
        
        # Fitness total
        total_fitness = total_distance + priority_penalty
        
        return FitnessComponents(
            total_distance=total_distance,
            priority_penalty=priority_penalty,
            capacity_violation=0.0,
            autonomy_violation=0.0,
            time_window_violation=0.0,
            total_fitness=total_fitness
        )


def create_fitness(fitness_type: FitnessType, **kwargs) -> FitnessFunction:
    """
    Factory function para criar funções de fitness.
    
    Args:
        fitness_type: Tipo de função de fitness
        **kwargs: Parâmetros específicos do tipo
    
    Returns:
        Instância da função de fitness
    
    Raises:
        ValueError: Se o tipo não for reconhecido
    """
    fitness_functions = {
        FitnessType.DISTANCE_ONLY: DistanceOnlyFitness,
        FitnessType.WEIGHTED_MULTI: WeightedMultiObjectiveFitness,
        FitnessType.PENALTY_BASED: PenaltyBasedFitness,
        FitnessType.PRIORITY_AWARE: PriorityAwareFitness,
    }
    
    if fitness_type not in fitness_functions:
        raise ValueError(f"Tipo de fitness desconhecido: {fitness_type}")
    
    return fitness_functions[fitness_type](**kwargs)

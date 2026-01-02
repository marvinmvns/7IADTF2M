"""
Módulo de População
===================

Este módulo gerencia a população de cromossomos no algoritmo genético,
incluindo inicialização, estatísticas e operações de gerenciamento.

A população pode ser inicializada de diferentes formas:
- Aleatória: todos os cromossomos são gerados aleatoriamente
- Heurística: parte da população usa heurísticas construtivas
- Híbrida: combinação de métodos aleatórios e heurísticos

Referências:
-----------
- Eiben, A. E., & Smith, J. E. (2015). Introduction to Evolutionary Computing.
- De Jong, K. A. (2006). Evolutionary Computation: A Unified Approach.
"""

import random
import numpy as np
from typing import List, Optional, Callable, Tuple
from dataclasses import dataclass

from .chromosome import Chromosome, DeliveryPoint, Vehicle


@dataclass
class PopulationStats:
    """
    Estatísticas da população.
    
    Attributes:
        generation: Número da geração atual
        best_fitness: Melhor fitness da população
        worst_fitness: Pior fitness da população
        avg_fitness: Fitness médio
        std_fitness: Desvio padrão do fitness
        diversity: Medida de diversidade genética
    """
    generation: int
    best_fitness: float
    worst_fitness: float
    avg_fitness: float
    std_fitness: float
    diversity: float


class Population:
    """
    Representa uma população de cromossomos.
    
    A população mantém um conjunto de soluções candidatas que evoluem
    ao longo das gerações através de operadores genéticos.
    
    Attributes:
        chromosomes: Lista de cromossomos na população
        size: Tamanho da população
        generation: Número da geração atual
        history: Histórico de estatísticas por geração
    """
    
    def __init__(self, size: int,
                 delivery_points: List[DeliveryPoint],
                 vehicles: Optional[List[Vehicle]] = None,
                 depot_index: int = 0):
        """
        Inicializa uma população vazia.
        
        Args:
            size: Tamanho desejado da população
            delivery_points: Lista de pontos de entrega
            vehicles: Lista de veículos disponíveis
            depot_index: Índice do ponto de depósito
        """
        self.size = size
        self.delivery_points = delivery_points
        self.vehicles = vehicles or [Vehicle(id=0)]
        self.depot_index = depot_index
        self.chromosomes: List[Chromosome] = []
        self.generation = 0
        self.history: List[PopulationStats] = []
        self._best_chromosome: Optional[Chromosome] = None
        self._best_ever: Optional[Chromosome] = None
    
    def initialize_random(self):
        """
        Inicializa a população com cromossomos aleatórios.
        
        Método mais simples de inicialização, onde cada cromossomo
        é uma permutação aleatória dos pontos de entrega.
        """
        num_points = len(self.delivery_points) - 1  # Exclui depósito
        self.chromosomes = [
            Chromosome.create_random(
                num_points=num_points,
                delivery_points=self.delivery_points,
                vehicles=self.vehicles,
                depot_index=self.depot_index
            )
            for _ in range(self.size)
        ]
        self.generation = 0
    
    def initialize_heuristic(self, heuristic_ratio: float = 0.2):
        """
        Inicializa a população com parte usando heurísticas.
        
        Uma fração da população é gerada usando a heurística do
        vizinho mais próximo, enquanto o restante é aleatório.
        Isso fornece um ponto de partida de maior qualidade.
        
        Args:
            heuristic_ratio: Fração da população usando heurísticas (0 a 1)
        """
        num_points = len(self.delivery_points) - 1
        num_heuristic = int(self.size * heuristic_ratio)
        
        self.chromosomes = []
        
        # Adiciona cromossomos heurísticos
        for _ in range(num_heuristic):
            chromosome = Chromosome.create_nearest_neighbor(
                num_points=num_points,
                delivery_points=self.delivery_points,
                vehicles=self.vehicles,
                depot_index=self.depot_index
            )
            # Adiciona pequena perturbação para diversidade
            if random.random() < 0.5:
                self._perturb_chromosome(chromosome)
            self.chromosomes.append(chromosome)
        
        # Completa com cromossomos aleatórios
        for _ in range(self.size - num_heuristic):
            self.chromosomes.append(
                Chromosome.create_random(
                    num_points=num_points,
                    delivery_points=self.delivery_points,
                    vehicles=self.vehicles,
                    depot_index=self.depot_index
                )
            )
        
        self.generation = 0
    
    def _perturb_chromosome(self, chromosome: Chromosome, num_swaps: int = 3):
        """
        Aplica pequenas perturbações a um cromossomo.
        
        Args:
            chromosome: Cromossomo a ser perturbado
            num_swaps: Número de trocas a realizar
        """
        genes = chromosome.genes
        for _ in range(num_swaps):
            i, j = random.sample(range(len(genes)), 2)
            genes[i], genes[j] = genes[j], genes[i]
        chromosome.invalidate_cache()
    
    def evaluate(self, fitness_function: Callable[[Chromosome], float]):
        """
        Avalia todos os cromossomos da população.
        
        Args:
            fitness_function: Função que calcula o fitness de um cromossomo
        """
        for chromosome in self.chromosomes:
            if chromosome._fitness is None:
                chromosome.fitness = fitness_function(chromosome)
        
        # Ordena por fitness (menor é melhor para minimização)
        self.chromosomes.sort(key=lambda c: c.fitness)
        
        # Atualiza melhor cromossomo
        self._best_chromosome = self.chromosomes[0]
        
        # Atualiza melhor de todos os tempos
        if (self._best_ever is None or 
            self._best_chromosome.fitness < self._best_ever.fitness):
            self._best_ever = self._best_chromosome.copy()
    
    def get_best(self) -> Optional[Chromosome]:
        """Retorna o melhor cromossomo da população atual."""
        return self._best_chromosome
    
    def get_best_ever(self) -> Optional[Chromosome]:
        """Retorna o melhor cromossomo encontrado em todas as gerações."""
        return self._best_ever
    
    def get_worst(self) -> Optional[Chromosome]:
        """Retorna o pior cromossomo da população atual."""
        if self.chromosomes:
            return max(self.chromosomes, key=lambda c: c.fitness)
        return None
    
    def calculate_stats(self) -> PopulationStats:
        """
        Calcula estatísticas da população atual.
        
        Returns:
            Objeto PopulationStats com métricas da população
        """
        if not self.chromosomes:
            return PopulationStats(
                generation=self.generation,
                best_fitness=float('inf'),
                worst_fitness=float('inf'),
                avg_fitness=float('inf'),
                std_fitness=0.0,
                diversity=0.0
            )
        
        fitness_values = [c.fitness for c in self.chromosomes]
        
        stats = PopulationStats(
            generation=self.generation,
            best_fitness=min(fitness_values),
            worst_fitness=max(fitness_values),
            avg_fitness=np.mean(fitness_values),
            std_fitness=np.std(fitness_values),
            diversity=self._calculate_diversity()
        )
        
        self.history.append(stats)
        return stats
    
    def _calculate_diversity(self) -> float:
        """
        Calcula a diversidade genética da população.
        
        Utiliza a distância de Hamming média entre pares de cromossomos
        como medida de diversidade.
        
        Returns:
            Valor de diversidade entre 0 e 1
        """
        if len(self.chromosomes) < 2:
            return 0.0
        
        total_distance = 0
        num_pairs = 0
        
        # Amostra aleatória para eficiência em populações grandes
        sample_size = min(50, len(self.chromosomes))
        sample = random.sample(self.chromosomes, sample_size)
        
        for i in range(len(sample)):
            for j in range(i + 1, len(sample)):
                # Distância de Hamming normalizada
                distance = sum(
                    1 for k in range(len(sample[i].genes))
                    if sample[i].genes[k] != sample[j].genes[k]
                )
                total_distance += distance / len(sample[i].genes)
                num_pairs += 1
        
        return total_distance / num_pairs if num_pairs > 0 else 0.0
    
    def replace(self, new_chromosomes: List[Chromosome]):
        """
        Substitui a população atual por novos cromossomos.
        
        Args:
            new_chromosomes: Lista de novos cromossomos
        """
        self.chromosomes = new_chromosomes
        self.generation += 1
        self._best_chromosome = None
    
    def add_chromosome(self, chromosome: Chromosome):
        """
        Adiciona um cromossomo à população.
        
        Args:
            chromosome: Cromossomo a ser adicionado
        """
        self.chromosomes.append(chromosome)
    
    def remove_worst(self, n: int = 1):
        """
        Remove os n piores cromossomos da população.
        
        Args:
            n: Número de cromossomos a remover
        """
        self.chromosomes.sort(key=lambda c: c.fitness)
        self.chromosomes = self.chromosomes[:-n] if n < len(self.chromosomes) else []
    
    def get_elite(self, n: int) -> List[Chromosome]:
        """
        Retorna os n melhores cromossomos (elite).
        
        Args:
            n: Número de cromossomos elite
        
        Returns:
            Lista dos n melhores cromossomos
        """
        sorted_pop = sorted(self.chromosomes, key=lambda c: c.fitness)
        return [c.copy() for c in sorted_pop[:n]]
    
    def __len__(self) -> int:
        return len(self.chromosomes)
    
    def __iter__(self):
        return iter(self.chromosomes)
    
    def __getitem__(self, index: int) -> Chromosome:
        return self.chromosomes[index]

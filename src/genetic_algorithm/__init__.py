"""
Módulo de Algoritmos Genéticos para Otimização de Rotas
=======================================================

Este módulo implementa um framework completo de algoritmos genéticos
para resolver o Problema do Caixeiro Viajante (TSP) aplicado à
distribuição de medicamentos e insumos hospitalares.

Autor: Projeto Acadêmico - Tech Challenge Fase 2
Data: Dezembro 2024
"""

from .chromosome import Chromosome, Route
from .population import Population
from .selection import SelectionOperator
from .crossover import CrossoverOperator
from .mutation import MutationOperator
from .fitness import FitnessFunction
from .genetic_algorithm import GeneticAlgorithm

__all__ = [
    'Chromosome',
    'Route',
    'Population',
    'SelectionOperator',
    'CrossoverOperator',
    'MutationOperator',
    'FitnessFunction',
    'GeneticAlgorithm'
]

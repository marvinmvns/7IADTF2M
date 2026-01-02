"""
Módulo de Utilitários
=====================

Este pacote contém funções utilitárias usadas em todo o projeto.

Módulos:
-------
- distance: Funções para cálculo de distância geodésica (Haversine)
"""

from .distance import (
    haversine_distance,
    euclidean_distance,
    manhattan_distance,
    bearing,
    destination_point,
    DistanceCalculator,
    DistanceMethod,
    calculate_distance,
    EARTH_RADIUS_KM,
    EARTH_RADIUS_MILES
)

__all__ = [
    'haversine_distance',
    'euclidean_distance',
    'manhattan_distance',
    'bearing',
    'destination_point',
    'DistanceCalculator',
    'DistanceMethod',
    'calculate_distance',
    'EARTH_RADIUS_KM',
    'EARTH_RADIUS_MILES'
]

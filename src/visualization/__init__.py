"""
Módulo de Visualização
======================

Este módulo fornece ferramentas de visualização para o algoritmo genético
de otimização de rotas, utilizando Pygame para renderização interativa.

Componentes:
-----------
- RouteVisualizer: Visualização das rotas em mapa 2D
- EvolutionVisualizer: Gráficos de evolução do fitness
- InteractiveViewer: Interface interativa completa
"""

from .route_visualizer import RouteVisualizer
from .evolution_visualizer import EvolutionVisualizer
from .interactive_viewer import InteractiveViewer

__all__ = [
    'RouteVisualizer',
    'EvolutionVisualizer',
    'InteractiveViewer'
]

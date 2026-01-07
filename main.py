#!/usr/bin/env python3
"""
==============================================================================
PROJETO 2: OTIMIZAÇÃO DE ROTAS PARA DISTRIBUIÇÃO DE MEDICAMENTOS E INSUMOS
==============================================================================

Tech Challenge - Fase 2 - Inteligência Artificial e Data-Driven

Este script inicia a visualização interativa com Pygame para o sistema de
otimização de rotas usando Algoritmos Genéticos.

Uso:
----
    python main.py

Requisitos:
----------
    pip install -r requirements.txt
"""

import os
import sys
from typing import List

# Adiciona diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Imports do projeto
from src.genetic_algorithm.chromosome import DeliveryPoint, Vehicle
from src.genetic_algorithm.selection import SelectionMethod
from src.genetic_algorithm.crossover import CrossoverMethod
from src.genetic_algorithm.mutation import MutationMethod
from src.genetic_algorithm.genetic_algorithm import GAConfig
from data.hospitais_sp import (
    scenario_small, scenario_medium, scenario_large, scenario_critical_only, HospitalData
)


def create_delivery_points(hospitals: List[HospitalData]) -> List[DeliveryPoint]:
    """
    Converte dados de hospitais para pontos de entrega.

    Args:
        hospitals: Lista de dados de hospitais

    Returns:
        Lista de DeliveryPoint
    """
    points = []

    for h in hospitals:
        point = DeliveryPoint(
            id=h.id,
            name=h.name,
            x=h.longitude,
            y=h.latitude,
            demand=h.demand,
            priority=h.priority,
            time_window=(0, 480)  # 8 horas
        )
        points.append(point)

    return points


def run_visualization():
    """Inicia a visualização interativa com Pygame."""
    print("=" * 70)
    print("VISUALIZAÇÃO INTERATIVA - OTIMIZAÇÃO DE ROTAS")
    print("=" * 70)

    try:
        from src.visualization.interactive_viewer import InteractiveViewer
    except ImportError as e:
        print(f"\nErro: {e}")
        print("Instale pygame: pip install pygame")
        return

    # Carrega cenários
    scenarios = [
        ("Pequeno", create_delivery_points(scenario_small())),
        ("Médio", create_delivery_points(scenario_medium())),
        ("Grande", create_delivery_points(scenario_large())),
        ("Crítico", create_delivery_points(scenario_critical_only())),
    ]

    # Configuração padrão do AG
    config = GAConfig(
        population_size=80,
        max_generations=10000,
        crossover_rate=0.9,
        mutation_rate=0.15,
        selection_method=SelectionMethod.TOURNAMENT,
        crossover_method=CrossoverMethod.OX,
        mutation_method=MutationMethod.INVERSION,
        elite_size=2,
        stagnation_enabled=True,
        stagnation_limit=5000,
        heuristic_init_ratio=0.2,
        verbose=False
    )

    # Cria visualizador
    viewer = InteractiveViewer(width=1600, height=900)
    viewer.setup(
        depot_index=0,
        ga_config=config,
        scenarios=scenarios,
        initial_scenario=2,  # Grande
        vehicle_count=3,
        background_map_path=None
    )

    print("\nIniciando visualização...")
    print("Controles:")
    print("  - Ajuste os parâmetros e cenário antes de iniciar")
    print("  - Clique em 'Iniciar' para começar")
    print("  - ESPAÇO: Pausar/Continuar")
    print("  - ESC: Sair")
    print("  - 'Exportar Mapa': Gera HTML com mapa interativo")

    viewer.run()


if __name__ == "__main__":
    run_visualization()

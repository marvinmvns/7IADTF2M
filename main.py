#!/usr/bin/env python3
"""
==============================================================================
PROJETO 2: OTIMIZAÇÃO DE ROTAS PARA DISTRIBUIÇÃO DE MEDICAMENTOS E INSUMOS
==============================================================================

Tech Challenge - Fase 2 - Inteligência Artificial e Data-Driven

Este projeto implementa um sistema de otimização de rotas usando Algoritmos
Genéticos para a distribuição de medicamentos e insumos hospitalares no
estado de São Paulo.

Autor: Aluno FIAP
Data: 2024

Funcionalidades:
---------------
1. Múltiplas abordagens de Algoritmos Genéticos
2. Visualização interativa com Pygame
3. Mapas interativos com Folium (OpenStreetMap)
4. Dados reais de hospitais de São Paulo
5. Comparação de diferentes operadores genéticos

Uso:
----
    python main.py                    # Execução padrão
    python main.py --mode visual      # Com visualização Pygame
    python main.py --mode experiment  # Comparação de operadores
    python main.py --mode map         # Apenas gera mapa HTML

Requisitos:
----------
    pip install pygame folium matplotlib numpy
"""

import os
import sys
import argparse
import time
from typing import List, Optional

# Adiciona diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Imports do projeto
from src.genetic_algorithm.chromosome import Chromosome, DeliveryPoint, Vehicle
from src.genetic_algorithm.population import Population
from src.genetic_algorithm.selection import SelectionMethod
from src.genetic_algorithm.crossover import CrossoverMethod
from src.genetic_algorithm.mutation import MutationMethod
from src.genetic_algorithm.fitness import FitnessType
from src.genetic_algorithm.genetic_algorithm import (
    GeneticAlgorithm, GAConfig, GAResult, GAExperiment
)
from data.hospitais_sp import (
    get_all_hospitals, get_depot, scenario_small, scenario_medium,
    scenario_large, HospitalData, DEPOSITO_CENTRAL
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


def create_vehicles(num_vehicles: int = 3) -> List[Vehicle]:
    """
    Cria frota de veículos.
    
    Args:
        num_vehicles: Número de veículos
    
    Returns:
        Lista de Vehicle
    """
    vehicles = []
    
    for i in range(num_vehicles):
        vehicle = Vehicle(
            id=i,
            capacity=100.0,  # Capacidade em unidades
            max_distance=200.0,  # km
            speed=40.0  # km/h (velocidade média urbana)
        )
        vehicles.append(vehicle)
    
    return vehicles


def run_basic_optimization(verbose: bool = True) -> GAResult:
    """
    Executa otimização básica.
    
    Args:
        verbose: Se deve mostrar logs
    
    Returns:
        Resultado da otimização
    """
    print("=" * 70)
    print("OTIMIZAÇÃO DE ROTAS - HOSPITAIS DE SÃO PAULO")
    print("=" * 70)
    
    # Carrega dados
    print("\n[1] Carregando dados dos hospitais...")
    hospitals = scenario_large()  # Todos os hospitais cadastrados
    delivery_points = create_delivery_points(hospitals)
    vehicles = create_vehicles(3)
    
    print(f"    - Depósito: {hospitals[0].name}")
    print(f"    - Hospitais: {len(hospitals) - 1}")
    print(f"    - Veículos: {len(vehicles)}")
    
    # Configura AG
    print("\n[2] Configurando Algoritmo Genético...")
    config = GAConfig(
        population_size=100,
        max_generations=200,
        crossover_rate=0.9,
        mutation_rate=0.15,
        selection_method=SelectionMethod.TOURNAMENT,
        crossover_method=CrossoverMethod.OX,
        mutation_method=MutationMethod.INVERSION,
        replacement_strategy='elitist',
        elite_size=2,
        tournament_size=3,
        stagnation_limit=50,
        heuristic_init_ratio=0.3,
        verbose=verbose,
        log_interval=10
    )
    
    print(f"    - População: {config.population_size}")
    print(f"    - Gerações: {config.max_generations}")
    print(f"    - Seleção: {config.selection_method.value}")
    print(f"    - Crossover: {config.crossover_method.value}")
    print(f"    - Mutação: {config.mutation_method.value}")
    
    # Executa AG
    print("\n[3] Executando otimização...")
    print("-" * 70)
    
    ga = GeneticAlgorithm(
        config=config,
        delivery_points=delivery_points,
        vehicles=vehicles,
        depot_index=0
    )
    
    result = ga.run()
    
    # Mostra resultados
    print("\n" + "=" * 70)
    print("RESULTADOS")
    print("=" * 70)
    
    print(f"\nMelhor Fitness: {result.best_fitness:.2f}")
    print(f"Gerações: {result.generations_run}")
    print(f"Tempo de Execução: {result.execution_time:.2f}s")
    print(f"Convergência na Geração: {result.convergence_generation}")
    
    # Detalhes das rotas
    routes = result.best_chromosome.get_routes()
    print(f"\nNúmero de Rotas: {len(routes)}")
    
    total_distance = 0
    for i, route in enumerate(routes):
        print(f"\n  Rota {i+1}:")
        print(f"    - Veículo: {route.vehicle.id}")
        print(f"    - Distância: {route.total_distance:.2f} km")
        print(f"    - Demanda: {route.total_demand:.1f} unidades")
        print(f"    - Paradas: {len(route.points)}")
        
        # Lista hospitais
        print("    - Hospitais:")
        for j, point in enumerate(route.points):
            priority_text = {1: "CRÍTICO", 2: "URGENTE", 3: "REGULAR"}
            print(f"      {j+1}. {point.name[:40]}... [{priority_text.get(point.priority, '')}]")
        
        total_distance += route.total_distance
    
    print(f"\nDistância Total: {total_distance:.2f} km")
    
    return result


def run_with_visualization():
    """Executa com visualização Pygame."""
    print("=" * 70)
    print("MODO VISUALIZAÇÃO INTERATIVA")
    print("=" * 70)
    
    try:
        from src.visualization.interactive_viewer import InteractiveViewer
        from src.visualization.evolution_visualizer import EvolutionVisualizer
    except ImportError as e:
        print(f"\nErro: {e}")
        print("Instale pygame: pip install pygame")
        return
    
    # Carrega dados
    scenarios = [
        ("Pequeno", create_delivery_points(scenario_small())),
        ("Médio", create_delivery_points(scenario_medium())),
        ("Grande", create_delivery_points(scenario_large())),
    ]
    
    # Configura AG
    config = GAConfig(
        population_size=80,
        max_generations=300,
        crossover_rate=0.9,
        mutation_rate=0.15,
        selection_method=SelectionMethod.TOURNAMENT,
        crossover_method=CrossoverMethod.OX,
        mutation_method=MutationMethod.INVERSION,
        elite_size=2,
        stagnation_limit=60,
        heuristic_init_ratio=0.2,
        verbose=False
    )
    
    # Cria visualizador
    viewer = InteractiveViewer(width=1600, height=900)
    viewer.setup(
        depot_index=0,
        ga_config=config,
        scenarios=scenarios,
        initial_scenario=0,
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


def run_experiment_comparison():
    """Executa comparação de diferentes operadores."""
    print("=" * 70)
    print("EXPERIMENTO: COMPARAÇÃO DE OPERADORES GENÉTICOS")
    print("=" * 70)
    
    # Carrega dados
    hospitals = scenario_small()  # Cenário menor para experimentos
    delivery_points = create_delivery_points(hospitals)
    vehicles = create_vehicles(2)
    
    print(f"\nCenário: {len(hospitals) - 1} hospitais, {len(vehicles)} veículos")
    
    # Configuração base
    base_config = GAConfig(
        population_size=50,
        max_generations=100,
        crossover_rate=0.9,
        mutation_rate=0.1,
        selection_method=SelectionMethod.TOURNAMENT,
        crossover_method=CrossoverMethod.OX,
        mutation_method=MutationMethod.INVERSION,
        verbose=False
    )
    
    # Cria experimento
    experiment = GAExperiment(
        delivery_points=delivery_points,
        vehicles=vehicles,
        depot_index=0
    )
    
    # Compara métodos de seleção
    print("\n" + "-" * 70)
    print("COMPARAÇÃO DE MÉTODOS DE SELEÇÃO")
    print("-" * 70)
    experiment.compare_selection_methods(base_config)
    
    # Compara métodos de crossover
    print("\n" + "-" * 70)
    print("COMPARAÇÃO DE MÉTODOS DE CROSSOVER")
    print("-" * 70)
    experiment.compare_crossover_methods(base_config)
    
    # Compara métodos de mutação
    print("\n" + "-" * 70)
    print("COMPARAÇÃO DE MÉTODOS DE MUTAÇÃO")
    print("-" * 70)
    experiment.compare_mutation_methods(base_config)
    
    # Resumo
    print(experiment.get_summary())


def generate_map_only():
    """Gera apenas o mapa HTML."""
    print("=" * 70)
    print("GERANDO MAPA INTERATIVO")
    print("=" * 70)
    
    try:
        from src.visualization.route_visualizer import RouteVisualizer
    except ImportError:
        print("\nInstalando folium...")
        os.system("pip install folium")
        from src.visualization.route_visualizer import RouteVisualizer
    
    # Executa otimização rápida
    hospitals = scenario_large()
    delivery_points = create_delivery_points(hospitals)
    vehicles = create_vehicles(3)
    
    config = GAConfig(
        population_size=50,
        max_generations=100,
        verbose=False
    )
    
    print("\nExecutando otimização...")
    ga = GeneticAlgorithm(
        config=config,
        delivery_points=delivery_points,
        vehicles=vehicles,
        depot_index=0
    )
    result = ga.run()
    
    # Gera mapa
    print("\nGerando mapa...")
    visualizer = RouteVisualizer(delivery_points, depot_index=0)
    
    algorithm_info = (
        f"Seleção: {config.selection_method.value} | "
        f"Crossover: {config.crossover_method.value} | "
        f"Mutação: {config.mutation_method.value}<br>"
        f"Reposição: {config.replacement_strategy.value} | "
        f"Fitness: {config.fitness_type.value} | "
        f"População: {config.population_size} | "
        f"Gerações: {config.max_generations}"
    )
    output_path = visualizer.visualize_solution(
        result.best_chromosome,
        output_path="mapa_rotas_hospitais_sp.html",
        title="Rotas Otimizadas - Hospitais de São Paulo",
        algorithm_info=algorithm_info,
        animate_car=True
    )
    
    print(f"\nMapa salvo em: {os.path.abspath(output_path)}")
    print("Abra o arquivo HTML em um navegador para visualizar.")
    
    # Também gera versão matplotlib
    try:
        png_path = visualizer.plot_routes_matplotlib(
            result.best_chromosome,
            output_path="rotas_hospitais_sp.png"
        )
        print(f"Imagem salva em: {os.path.abspath(png_path)}")
    except Exception as e:
        print(f"Aviso: Não foi possível gerar imagem PNG: {e}")


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Otimização de Rotas para Distribuição de Medicamentos"
    )
    parser.add_argument(
        '--mode', '-m',
        choices=['basic', 'visual', 'experiment', 'map'],
        default='basic',
        help='Modo de execução'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Modo silencioso'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'basic':
        run_basic_optimization(verbose=not args.quiet)
    elif args.mode == 'visual':
        run_with_visualization()
    elif args.mode == 'experiment':
        run_experiment_comparison()
    elif args.mode == 'map':
        generate_map_only()


if __name__ == "__main__":
    main()

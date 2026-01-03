"""
Testes de validação do DEPÓSITO (Farmácia Central - Sé).

Este módulo testa se TODAS as rotas geradas pelo algoritmo genético:
1. Partem do depósito (Farmácia Central - Sé)
2. Retornam ao depósito
3. Calculam a distância corretamente incluindo ida e volta
4. Não incluem o depósito como ponto intermediário da rota

CRÍTICO: O depósito deve SEMPRE ser o ponto de partida e chegada!
"""

import pytest
import sys
import os

# Adiciona src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.genetic_algorithm.chromosome import (
    Chromosome, Route, DeliveryPoint, Vehicle
)
from src.genetic_algorithm.genetic_algorithm import GeneticAlgorithm, GAConfig
from src.genetic_algorithm.selection import SelectionMethod
from src.genetic_algorithm.crossover import CrossoverMethod
from src.genetic_algorithm.mutation import MutationMethod


@pytest.fixture
def sample_points_with_depot():
    """Cria pontos de entrega de teste com depósito."""
    points = [
        # Depósito (índice 0) - Farmácia Central - Sé
        DeliveryPoint(id=0, name="Farmácia Central - Sé (DEPÓSITO)",
                     x=-46.6333, y=-23.5505,  # São Paulo Centro
                     priority=3, demand=0.0),  # Depósito não tem demanda

        # Hospitais a serem atendidos
        DeliveryPoint(id=1, name="Hospital 1", x=-46.6500, y=-23.5600,
                     priority=1, demand=10.0),
        DeliveryPoint(id=2, name="Hospital 2", x=-46.6200, y=-23.5400,
                     priority=2, demand=15.0),
        DeliveryPoint(id=3, name="Hospital 3", x=-46.6400, y=-23.5300,
                     priority=3, demand=20.0),
        DeliveryPoint(id=4, name="Hospital 4", x=-46.6100, y=-23.5700,
                     priority=1, demand=12.0),
    ]
    return points


@pytest.fixture
def sample_vehicles():
    """Cria veículos de teste."""
    return [
        Vehicle(id=1, capacity=100, max_distance=200, speed=1.0),
        Vehicle(id=2, capacity=100, max_distance=200, speed=1.0),
    ]


class TestDepotValidation:
    """Testes de validação do depósito."""

    def test_depot_is_index_zero(self, sample_points_with_depot):
        """Testa que o depósito está no índice 0."""
        depot = sample_points_with_depot[0]
        assert depot.id == 0
        assert "DEPÓSITO" in depot.name
        assert depot.demand == 0.0  # Depósito não tem demanda

    def test_chromosome_genes_exclude_depot(self, sample_points_with_depot, sample_vehicles):
        """Testa que os genes do cromossomo NÃO incluem o depósito."""
        num_points = len(sample_points_with_depot) - 1  # Exclui depósito

        chromosome = Chromosome.create_random(
            num_points=num_points,
            delivery_points=sample_points_with_depot,
            vehicles=sample_vehicles,
            depot_index=0
        )

        # Genes não devem conter o índice do depósito (0)
        assert 0 not in chromosome.genes, "Genes NÃO devem conter o depósito!"
        assert len(chromosome.genes) == num_points
        assert set(chromosome.genes) == {1, 2, 3, 4}

    def test_single_route_starts_and_ends_at_depot(self, sample_points_with_depot,
                                                   sample_vehicles):
        """Testa que uma rota única parte e retorna ao depósito."""
        # Cria cromossomo com 1 veículo (TSP)
        chromosome = Chromosome(
            genes=[1, 2, 3, 4],
            delivery_points=sample_points_with_depot,
            vehicles=[sample_vehicles[0]],
            depot_index=0
        )

        routes = chromosome.get_routes()
        assert len(routes) == 1

        route = routes[0]
        depot = sample_points_with_depot[0]

        # Verifica que o depot está definido corretamente
        assert route.depot is not None
        assert route.depot.id == depot.id
        assert route.depot.name == depot.name

        # Verifica que os pontos da rota NÃO incluem o depósito
        point_ids = [p.id for p in route.points]
        assert 0 not in point_ids, "Pontos da rota NÃO devem incluir o depósito!"
        assert point_ids == [1, 2, 3, 4]

    def test_multiple_routes_all_use_same_depot(self, sample_points_with_depot,
                                                 sample_vehicles):
        """Testa que múltiplas rotas todas usam o mesmo depósito."""
        # Cria cromossomo com 2 veículos (VRP)
        chromosome = Chromosome(
            genes=[1, 2, 3, 4],
            delivery_points=sample_points_with_depot,
            vehicles=sample_vehicles,
            depot_index=0
        )

        routes = chromosome.get_routes()
        depot = sample_points_with_depot[0]

        # Todas as rotas devem ter o mesmo depósito
        for i, route in enumerate(routes):
            assert route.depot is not None, f"Rota {i} deve ter depósito!"
            assert route.depot.id == depot.id, f"Rota {i} deve usar o depósito correto!"

            # Nenhuma rota deve incluir o depósito nos pontos intermediários
            point_ids = [p.id for p in route.points]
            assert 0 not in point_ids, f"Rota {i} não deve incluir depósito nos pontos!"

    def test_route_distance_includes_depot_trips(self, sample_points_with_depot):
        """Testa que a distância da rota inclui ida e volta ao depósito."""
        depot = sample_points_with_depot[0]
        hospital1 = sample_points_with_depot[1]
        hospital2 = sample_points_with_depot[2]

        # Cria rota simples: Depósito -> Hospital1 -> Hospital2 -> Depósito
        route = Route(
            points=[hospital1, hospital2],
            vehicle=Vehicle(id=1),
            depot=depot
        )

        # Calcula distâncias manualmente
        dist_depot_to_h1 = depot.distance_to(hospital1)
        dist_h1_to_h2 = hospital1.distance_to(hospital2)
        dist_h2_to_depot = hospital2.distance_to(depot)

        expected_total = dist_depot_to_h1 + dist_h1_to_h2 + dist_h2_to_depot

        # Verifica que o cálculo automático está correto
        assert abs(route.total_distance - expected_total) < 0.01, \
            f"Distância calculada incorreta! Esperado: {expected_total}, Obtido: {route.total_distance}"

        # Garante que a distância > 0 (não é uma rota vazia)
        assert route.total_distance > 0

    def test_route_without_depot_raises_error(self):
        """Testa que criar rota sem depósito ainda funciona mas usa primeiro ponto."""
        hospital1 = DeliveryPoint(id=1, name="H1", x=-46.65, y=-23.56, demand=10)
        hospital2 = DeliveryPoint(id=2, name="H2", x=-46.62, y=-23.54, demand=15)

        # Cria rota SEM especificar depot
        route = Route(
            points=[hospital1, hospital2],
            vehicle=Vehicle(id=1),
            depot=None  # Sem depósito explícito
        )

        # Deve usar o primeiro ponto como depot (comportamento de fallback)
        assert route.depot == hospital1

    def test_ga_preserves_depot_through_evolution(self, sample_points_with_depot,
                                                  sample_vehicles):
        """
        Testa que o GA preserva o depósito correto através de toda a evolução.
        """
        config = GAConfig(
            population_size=20,
            max_generations=10,
            crossover_rate=0.9,
            mutation_rate=0.1,
            selection_method=SelectionMethod.TOURNAMENT,
            crossover_method=CrossoverMethod.OX,
            mutation_method=MutationMethod.INVERSION,
            elite_size=2,
            verbose=False
        )

        ga = GeneticAlgorithm(
            config=config,
            delivery_points=sample_points_with_depot,
            vehicles=sample_vehicles,
            depot_index=0
        )

        result = ga.run()

        # Verifica solução final
        best_chromosome = result.best_chromosome
        depot = sample_points_with_depot[0]

        # Genes não devem conter o depósito
        assert 0 not in best_chromosome.genes

        # Todas as rotas devem usar o depósito correto
        routes = best_chromosome.get_routes()
        assert len(routes) > 0

        for i, route in enumerate(routes):
            assert route.depot is not None, f"Rota {i} deve ter depósito após evolução!"
            assert route.depot.id == depot.id, \
                f"Rota {i} deve usar depósito correto após evolução!"

            # Pontos não devem incluir depósito
            point_ids = [p.id for p in route.points]
            assert 0 not in point_ids, \
                f"Rota {i} não deve ter depósito nos pontos após evolução!"

    def test_nearest_neighbor_respects_depot(self, sample_points_with_depot,
                                             sample_vehicles):
        """Testa que heurística nearest neighbor respeita o depósito."""
        num_points = len(sample_points_with_depot) - 1

        chromosome = Chromosome.create_nearest_neighbor(
            num_points=num_points,
            delivery_points=sample_points_with_depot,
            vehicles=sample_vehicles,
            depot_index=0
        )

        # Genes não devem conter depósito
        assert 0 not in chromosome.genes

        # Rotas devem usar depósito
        routes = chromosome.get_routes()
        depot = sample_points_with_depot[0]

        for route in routes:
            assert route.depot.id == depot.id

    def test_depot_demand_is_zero(self, sample_points_with_depot):
        """Testa que o depósito tem demanda zero (não consome recursos)."""
        depot = sample_points_with_depot[0]
        assert depot.demand == 0.0, "Depósito não deve ter demanda!"

    def test_depot_not_in_route_demand_calculation(self, sample_points_with_depot):
        """Testa que a demanda da rota NÃO inclui o depósito."""
        depot = sample_points_with_depot[0]
        hospitals = sample_points_with_depot[1:3]

        route = Route(points=hospitals, vehicle=Vehicle(id=1), depot=depot)

        # Demanda total deve ser apenas dos hospitais
        expected_demand = sum(h.demand for h in hospitals)
        assert route.total_demand == expected_demand

        # Garante que não está somando demanda do depósito (que é 0)
        assert depot.demand == 0.0


def test_depot_visual_inspection(sample_points_with_depot, sample_vehicles):
    """
    Teste visual/informativo que imprime informações do depósito.
    Não falha, apenas informa.
    """
    depot = sample_points_with_depot[0]

    print("\n" + "=" * 70)
    print("🏭 INFORMAÇÕES DO DEPÓSITO")
    print("=" * 70)
    print(f"ID:        {depot.id}")
    print(f"Nome:      {depot.name}")
    print(f"Latitude:  {depot.y}")
    print(f"Longitude: {depot.x}")
    print(f"Demanda:   {depot.demand} (deve ser 0)")
    print(f"Prioridade: {depot.priority}")

    # Cria rota de exemplo
    chromosome = Chromosome(
        genes=[1, 2, 3, 4],
        delivery_points=sample_points_with_depot,
        vehicles=sample_vehicles,
        depot_index=0
    )

    routes = chromosome.get_routes()

    print(f"\n📊 ROTAS GERADAS: {len(routes)}")
    for i, route in enumerate(routes):
        print(f"\nRota {i+1}:")
        print(f"  Depósito: {route.depot.name}")
        print(f"  Veículo: {route.vehicle.id}")
        print(f"  Hospitais: {[p.name for p in route.points]}")
        print(f"  Distância total: {route.total_distance:.2f} km")
        print(f"  Demanda total: {route.total_demand:.1f}")

        # Calcula distâncias parciais para visualizar
        dist_to_first = route.depot.distance_to(route.points[0]) if route.points else 0
        dist_to_last = route.points[-1].distance_to(route.depot) if route.points else 0

        print(f"  └─ Depósito → Primeiro: {dist_to_first:.2f} km")
        print(f"  └─ Último → Depósito: {dist_to_last:.2f} km")

    print("=" * 70)


if __name__ == "__main__":
    # Executa testes com pytest
    pytest.main([__file__, "-v", "-s"])

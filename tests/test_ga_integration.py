import pytest
from src.genetic_algorithm.genetic_algorithm import GeneticAlgorithm, GAConfig
from src.genetic_algorithm.chromosome import DeliveryPoint, Vehicle
from src.genetic_algorithm.mutation import MutationMethod
from src.genetic_algorithm.crossover import CrossoverMethod

def test_ga_hybrid_run():
    # Setup small problem
    depot = DeliveryPoint(id=0, name="Depot", x=0, y=0)
    p1 = DeliveryPoint(id=1, name="P1", x=0.1, y=0.1)
    p2 = DeliveryPoint(id=2, name="P2", x=-0.1, y=0.2)
    delivery_points = [depot, p1, p2]
    vehicles = [Vehicle(id=0), Vehicle(id=1)]
    
    config = GAConfig(
        population_size=10,
        max_generations=5,
        mutation_method=MutationMethod.HYBRID,
        crossover_method=CrossoverMethod.HYBRID,
        elite_size=2
    )
    
    ga = GeneticAlgorithm(
        delivery_points=delivery_points,
        vehicles=vehicles,
        config=config
    )
    
    result = ga.run()
    
    assert result.best_chromosome is not None
    assert len(result.best_chromosome.genes) == 2
    assert len(result.best_chromosome.speed_factors) == 2
    assert result.generations_run > 0
    assert result.best_fitness <= result.history[0].best_fitness

def test_ga_invalid_config():
    with pytest.raises(ValueError):
        # Invalid method string (though Enum usually prevents this, create_mutation might raise it)
        from src.genetic_algorithm.mutation import create_mutation
        create_mutation("non_existent_method")

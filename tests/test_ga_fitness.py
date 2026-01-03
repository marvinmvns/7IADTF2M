import pytest
from src.genetic_algorithm.chromosome import Chromosome, Route
from src.genetic_algorithm.fitness import WeightedMultiObjectiveFitness, FitnessComponents
from src.genetic_algorithm.chromosome import Chromosome, Route, Vehicle, DeliveryPoint

@pytest.fixture
def mock_chromosome():
    # Setup a chromosome with 1 vehicle and simple route
    v = Vehicle(id=0, capacity=100, speed=1.0)
    p1 = DeliveryPoint(id=1, name="P1", x=0, y=0, demand=10)
    p2 = DeliveryPoint(id=2, name="P2", x=0.1, y=0, demand=10) # ~11km distance
    
    genes = [1, 2]
    # speed_factor 1.0
    c = Chromosome(genes=genes, vehicles=[v], speed_factors=[1.0])
    c.delivery_points = [DeliveryPoint(id=0, name="Depot", x=0, y=0), p1, p2] # id 0 is depot
    return c

def test_fitness_speed_impact(mock_chromosome):
    fitness_func = WeightedMultiObjectiveFitness(distance_weight=1.0)
    
    # 1. Base case: speed_factor = 1.0
    mock_chromosome.speed_factors = [1.0]
    mock_chromosome.invalidate_cache()
    f1 = fitness_func.evaluate(mock_chromosome)
    
    # 2. Faster case: speed_factor = 1.5
    # Time proxy (Dist / Speed) should go DOWN
    # Operational cost (Dist * Speed^2) should go UP
    mock_chromosome.speed_factors = [1.5]
    mock_chromosome.invalidate_cache()
    f_fast = fitness_func.evaluate(mock_chromosome)
    
    # 3. Slower case: speed_factor = 0.5
    mock_chromosome.speed_factors = [0.5]
    mock_chromosome.invalidate_cache()
    f_slow = fitness_func.evaluate(mock_chromosome)
    
    # Verification:
    # Fitness = w1 * (Dist/Speed) + w2 * (Dist * Speed^2)
    # w1 = 1.0, w2 = 0.5 (hardcoded in fitness.py)
    # Factor 1.0: 1*Dist + 0.5*Dist = 1.5*Dist
    # Factor 1.5: 1*(Dist/1.5) + 0.5*(Dist*2.25) = 0.66*Dist + 1.125*Dist = 1.79*Dist
    # Factor 0.5: 1*(Dist/0.5) + 0.5*(Dist*0.25) = 2*Dist + 0.125*Dist = 2.125*Dist
    
    # Slowest should be worst (highest fitness) in this specific setup because distance/speed grows fast
    assert f_slow > f_fast
    assert f_slow > f1
    
def test_fitness_components(mock_chromosome):
    fitness_func = WeightedMultiObjectiveFitness()
    components = fitness_func.get_components(mock_chromosome)
    
    assert isinstance(components, FitnessComponents)
    assert components.total_distance > 0
    assert components.total_fitness > 0

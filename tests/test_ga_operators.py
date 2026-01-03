import pytest
import random
from src.genetic_algorithm.chromosome import Chromosome
from src.genetic_algorithm.mutation import (
    GaussianMutation, HybridMutation, InversionMutation, SwapMutation
)
from src.genetic_algorithm.crossover import (
    ArithmeticCrossover, HybridCrossover, OXCrossover
)
from src.genetic_algorithm.chromosome import Chromosome, Vehicle

@pytest.fixture
def sample_chromosome():
    # 5 delivery points, 10 vehicles
    genes = [1, 2, 3, 4, 5]
    vehicles = [Vehicle(id=i) for i in range(10)]
    speed_factors = [1.0] * 10
    return Chromosome(genes=genes, vehicles=vehicles, speed_factors=speed_factors)

class TestMutationOperators:
    def test_gaussian_mutation(self, sample_chromosome):
        # Force mutation with rate 1.0
        mutator = GaussianMutation(mutation_rate=1.0, sigma=0.5)
        mutated = mutator.mutate(sample_chromosome)
        
        # Genes (route) should be the same
        assert mutated.genes == sample_chromosome.genes
        # Speed factors should be different
        assert mutated.speed_factors != sample_chromosome.speed_factors
        # Values should be within [0.5, 1.5]
        for speed in mutated.speed_factors:
            assert 0.5 <= speed <= 1.5

    def test_hybrid_mutation(self, sample_chromosome):
        # Hybrid applies both route and speed mutation
        # Using Inversion as base
        mutator = HybridMutation(mutation_rate=1.0)
        mutated = mutator.mutate(sample_chromosome)
        
        # At least one should be different (randomness might keep them same but highly unlikely with 1.0 rate)
        # Note: Inversion of [1,2,3,4,5] will definitely change it if i,j are selected
        assert mutated.genes != sample_chromosome.genes or mutated.speed_factors != sample_chromosome.speed_factors

    def test_swap_mutation(self, sample_chromosome):
        mutator = SwapMutation(mutation_rate=1.0)
        mutated = mutator.mutate(sample_chromosome)
        assert len(mutated.genes) == len(sample_chromosome.genes)
        assert set(mutated.genes) == set(sample_chromosome.genes)

class TestCrossoverOperators:
    def test_arithmetic_crossover(self):
        p1 = Chromosome(genes=[1,2,3], speed_factors=[1.0, 1.0])
        p2 = Chromosome(genes=[1,2,3], speed_factors=[1.4, 0.6])
        
        # alpha = 0.5 means average
        cross = ArithmeticCrossover(crossover_rate=1.0, alpha=0.5)
        c1, c2 = cross.crossover(p1, p2)
        
        # child1 speeds should be (1.0 + 1.4)/2 = 1.2 and (1.0 + 0.6)/2 = 0.8
        assert c1.speed_factors == [1.2, 0.8]
        assert c2.speed_factors == [1.2, 0.8]

    def test_hybrid_crossover(self):
        p1 = Chromosome(genes=[1,2,3,4,5], speed_factors=[1.0, 1.0])
        p2 = Chromosome(genes=[5,4,3,2,1], speed_factors=[1.5, 0.5])
        
        cross = HybridCrossover(crossover_rate=1.0)
        c1, c2 = cross.crossover(p1, p2)
        
        # Routes should be result of OX
        assert len(c1.genes) == 5
        assert set(c1.genes) == {1, 2, 3, 4, 5}
        # Speeds should be mixed (Arithmetic alpha=0.5)
        assert c1.speed_factors == [1.25, 0.75]

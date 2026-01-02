# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an academic project (FIAP Tech Challenge Phase 2) implementing a **Vehicle Routing Problem (VRP)** solution using **Genetic Algorithms** for optimizing medication and supply delivery routes to hospitals in São Paulo state.

The problem extends the classic Traveling Salesman Problem (TSP) to handle:
- Multiple vehicles with capacity and autonomy constraints
- Delivery priorities (critical, urgent, regular)
- Real hospital location data from São Paulo
- Multi-objective fitness function (distance, priority penalties, capacity/autonomy constraints)

This variant uses **Haversine distance calculations** for accurate geographic distances between latitude/longitude coordinates.

## Running the Project

### Installation
```bash
pip install -r requirements.txt
```

Dependencies: `numpy`, `matplotlib`, `pygame`, `folium`

### Execution Modes

```bash
# Basic optimization (terminal output)
python main.py --mode basic

# Interactive Pygame visualization
python main.py --mode visual

# Experiment mode: compare GA operators
python main.py --mode experiment

# Generate only interactive HTML map
python main.py --mode map

# Quiet mode (suppress logs)
python main.py --mode basic --quiet
```

### Running Experiments

```bash
python experimento_selecao.py
```

This compares the 8 selection methods and generates detailed visualizations and statistical analysis.

## Project Architecture

### Modular Structure

```
src/
├── genetic_algorithm/
│   ├── chromosome.py       # Chromosome representation (permutation-based)
│   ├── population.py       # Population management
│   ├── selection.py        # 8 selection methods (tournament, roulette, ranking, etc.)
│   ├── crossover.py        # 8 crossover operators (PMX, OX, CX, ERX, etc.)
│   ├── mutation.py         # 8 mutation operators (swap, inversion, 2-opt, 3-opt, etc.)
│   ├── fitness.py          # Multi-objective fitness function
│   └── genetic_algorithm.py # Main GA orchestrator
├── visualization/
│   ├── route_visualizer.py      # Folium/Matplotlib maps
│   ├── evolution_visualizer.py  # Pygame real-time visualization
│   └── interactive_viewer.py    # Full interactive GUI
└── utils/
    └── distance.py         # Haversine distance calculations

data/
└── hospitais_sp.py        # Hospital data with coordinates, demands, priorities
```

### Key Components

**Chromosome Representation:**
- Permutation of all delivery points (excluding depot, which is always index 0)
- Routes are divided dynamically during fitness evaluation when capacity/autonomy constraints are violated
- Example: `[3, 5, 1, 8, 2, 4, 6, 7]` → splits into multiple routes based on vehicle constraints

**Fitness Function:**
```
Fitness = w1*Distance + w2*PriorityPenalty + w3*CapacityPenalty + w4*AutonomyPenalty
```
- Lower fitness is better
- Priority penalty: heavily penalizes critical deliveries (priority=1) not served early
- Constraint penalties: discourage capacity/autonomy violations

**Distance Calculation:**
- Uses Haversine formula for accurate geographic distances (src/utils/distance.py)
- Also available in chromosome.py with `USE_HAVERSINE = True` flag
- Calculates great circle distance between lat/lon coordinates in kilometers

### Genetic Operators

**Selection (8 methods):**
Tournament, Roulette, Ranking, Truncation, Elitist, SUS (Stochastic Universal Sampling), Boltzmann, Steady-State

**Crossover (8 methods):**
PMX, OX, CX, AEX, ERX, SCX, OX2, POS
- All designed for permutation-based representations
- Preserve valid tours (no duplicates/missing cities)

**Mutation (8 methods):**
Swap, Inversion, Scramble, Insert, Displacement, 2-opt, 3-opt, RSM
- Maintain permutation validity
- 2-opt/3-opt are local search heuristics

### Configuration Parameters

When creating `GAConfig` in genetic_algorithm.py:

```python
config = GAConfig(
    population_size=80-100,        # Population size
    max_generations=200-300,       # Max generations
    crossover_rate=0.9,            # High recombination
    mutation_rate=0.1-0.15,        # Moderate exploration
    elite_size=2-5,                # Preserve best solutions
    tournament_size=3,             # Selection pressure
    stagnation_limit=50-60,        # Early stopping
    heuristic_init_ratio=0.2-0.3,  # Fraction initialized with nearest-neighbor
    selection_method=SelectionMethod.TOURNAMENT,
    crossover_method=CrossoverMethod.OX,
    mutation_method=MutationMethod.INVERSION
)
```

### Scenarios

Three predefined scenarios in `data/hospitais_sp.py`:
- `scenario_small()`: ~10 hospitals, 2 vehicles (quick experiments)
- `scenario_medium()`: ~20 hospitals, 3 vehicles (default)
- `scenario_large()`: All hospitals, 4-5 vehicles (computationally intensive)

## Implementation Notes

**Critical Design Decisions:**
- Depot is always index 0 in delivery_points list
- Chromosomes represent only non-depot points (depot is implicit)
- Routes are rebuilt dynamically during fitness evaluation
- Vehicle assignments happen during route construction based on constraint violations
- Interactive viewer runs GA in a separate thread for real-time visualization

**Haversine vs Euclidean Distance:**
- This variant (`projeto2_haversine`) uses Haversine formula for accurate geographic distances
- Original variant (`projeto2_otimizacao_rotas`) uses Euclidean distance on lat/lon (less accurate)
- Distance method can be changed via `USE_HAVERSINE` flag in chromosome.py or by using src/utils/distance.py

**Modifying Fitness Weights:**

Edit in fitness.py or pass custom weights:
```python
fitness = calculate_fitness(
    chromosome,
    w_distance=1.0,
    w_priority=500.0,
    w_capacity=1000.0,
    w_autonomy=1000.0
)
```

## Adding New Genetic Operators

1. Add enum value to the operator module (selection.py, crossover.py, or mutation.py)
2. Implement operator function following the signature pattern
3. Register in the factory function (create_selector, create_crossover, or create_mutation)
4. Add to experiment comparison if needed

## Academic Context

This is a learning project demonstrating:
- Implementation of multiple GA operator variants (8 of each type)
- Empirical comparison methodology for operator performance
- Real-world constraint handling (VRP vs simple TSP)
- Academic documentation and visualization standards

The codebase deliberately includes 8 variants of each operator type for comparative study, not because all are needed in production.

import sys
import os
import time
import json
import itertools
from datetime import datetime

sys.path.append(os.getcwd())

from src.controllers.experiment_manager import ExperimentManager

def run_grid_search_v2():
    manager = ExperimentManager()
    
    # Correct Enum values based on source code:
    # Selection: 'tournament', 'roulette_wheel', 'rank' (from selection.py)
    # Crossover: 'order_crossover' (OX), 'partially_mapped_crossover' (PMX), 'cycle_crossover' (CX) (from crossover.py)
    # Mutation: 'inversion', 'swap', 'scramble' (Assuming these are standard from mutation.py - let's trust previous knowledge or assume they are valid if not errored yet)
    
    # Wait, 'pmx' failed because it expects 'partially_mapped_crossover'.
    # 'cycle_crossover' seemed to work? No, 'cycle_crossover' worked in the script output for some? 
    # Let's check the output again. 
    # "Testing: tournament + cycle_crossover + inversion" -> "Result: Avg=1059.45" (Successful)
    # "Testing: tournament + pmx + scramble" -> ValueError: 'pmx' is not a valid CrossoverMethod
    # So 'cycle_crossover' IS valid. 'pmx' passed as string 'pmx' is INVALID. It should be 'partially_mapped_crossover'.
    
    selection_methods = ["tournament", "roulette_wheel", "rank"]
    crossover_methods = ["order_crossover", "partially_mapped_crossover", "cycle_crossover"]
    mutation_methods = ["inversion", "swap", "scramble"]
    
    # Base config for V2 context (Restart strategy compatible)
    # We use 1000 generations as the "short run" unit for restart strategy
    base_config = {
        "scenario": "medium",
        "population_size": 100,
        "max_generations": 1000,
        "crossover_rate": 0.9,
        "mutation_rate": 0.15,
        "replacement_strategy": "elitist",
        "fitness_type": "distance_only",
        "stagnation_enabled": True,
        "stagnation_limit": 300, 
        "elite_size": 2,
        "tournament_size": 3
    }
    
    combinations = list(itertools.product(selection_methods, crossover_methods, mutation_methods))
    
    print(f"Starting Grid Search V2: {len(combinations)} combinations")
    
    results = []
    
    for sel, cross, mut in combinations:
        print(f"Testing: {sel} + {cross} + {mut}")
        
        # Run 2 iterations to get an average
        run_fitnesses = []
        for i in range(2):
            config = base_config.copy()
            config["selection_method"] = sel
            config["crossover_method"] = cross
            config["mutation_method"] = mut
            
            try:
                exp = manager.create_experiment(config)
                # Run synchronously
                manager._run_process(exp.id)
                
                # Fetch result
                exp_data = manager.get_experiment(exp.id)
                # Need to be careful about None result
                if exp_data and exp_data.get('best_fitness'):
                     run_fitnesses.append(exp_data['best_fitness'])
                else:
                     print("  Warning: No fitness returned")
                     
            except Exception as e:
                print(f"Error: {e}")
        
        if run_fitnesses:
            avg_fitness = sum(run_fitnesses) / len(run_fitnesses)
            best_fitness = min(run_fitnesses)
            print(f"  Result: Avg={avg_fitness:.2f}, Best={best_fitness:.2f}")
            results.append({
                "selection": sel,
                "crossover": cross,
                "mutation": mut,
                "avg_fitness": avg_fitness,
                "best_fitness": best_fitness
            })
        else:
            print("  Failed or no valid results.")

    # Sort by best fitness
    results.sort(key=lambda x: x["best_fitness"])
    
    print("\nTop 5 Combinations:")
    for i, r in enumerate(results[:5]):
        print(f"{i+1}. {r['selection']} + {r['crossover']} + {r['mutation']} -> Best: {r['best_fitness']:.2f}, Avg: {r['avg_fitness']:.2f}")
        
    # Save to JSON for report generation
    with open("grid_search_v2_results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_grid_search_v2()

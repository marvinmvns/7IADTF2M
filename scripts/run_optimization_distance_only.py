import sys
import os
import time
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from src.controllers.experiment_manager import ExperimentManager

def run_batch():
    manager = ExperimentManager()
    
    # Configuration for the batch
    # DISTANCE ONLY to compare with conclusao_v2
    num_runs = 5
    base_config = {
        "scenario": "medium",
        "population_size": 100,
        "max_generations": 3000,
        "crossover_rate": 0.9,
        "mutation_rate": 0.15,
        "selection_method": "tournament",
        "crossover_method": "order_crossover", 
        "mutation_method": "inversion", 
        "replacement_strategy": "elitist",
        "fitness_type": "distance_only", # KEY CHANGE
        "stagnation_enabled": True,
        "stagnation_limit": 1000, 
        "elite_size": 2,
        "tournament_size": 3
    }

    experiment_ids = []
    
    print(f"Starting batch of {num_runs} DISTANCE_ONLY experiments...")
    
    for i in range(num_runs):
        print(f"Submitting run {i+1}/{num_runs}...")
        try:
            exp = manager.create_experiment(base_config)
            # Run synchronously
            manager._run_process(exp.id)
            experiment_ids.append(exp.id)
            
            # Fetch result immediately to print
            completed_exp = manager.get_experiment(exp.id)
            print(f"Run {i+1} completed. ID: {exp.id} | Best: {completed_exp['best_fitness']:.2f} | Gens: {completed_exp['generations_run']} | Time: {completed_exp['execution_time']:.2f}s")
        except Exception as e:
            print(f"Error in run {i+1}: {e}")
            import traceback
            traceback.print_exc()

    # Collect results
    print("\nBatch Results Summary (Distance Only):")
    results = []
    for exp_id in experiment_ids:
        exp_data = manager.get_experiment(exp_id)
        if exp_data:
            results.append(exp_data)
            
    if results:
        fitnesses = [r['best_fitness'] for r in results if r['best_fitness'] is not None]
        if fitnesses:
            avg_fitness = sum(fitnesses) / len(fitnesses)
            best_of_batch = min(fitnesses)
            print(f"Experiments: {len(results)}")
            print(f"Average Best Fitness: {avg_fitness:.4f}")
            print(f"Best of Batch: {best_of_batch:.4f}")
            
            if best_of_batch < 1061.0:
                print("SUCCESS: New record found!")

if __name__ == "__main__":
    run_batch()

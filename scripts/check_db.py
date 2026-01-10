from src.controllers.experiment_manager import ExperimentManager
import json

manager = ExperimentManager()
stats = manager.get_statistics()
print("Statistics:", json.dumps(stats, indent=2))

experiments = manager.list_experiments(limit=5)
for exp in experiments:
    print(f"ID: {exp['id']}, Status: {exp['status']}, Gen: {exp['generations_run']}, Best: {exp['best_fitness']}")

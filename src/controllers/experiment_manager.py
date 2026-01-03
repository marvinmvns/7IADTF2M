from sqlalchemy.orm import Session
from src.database.database import engine, Base, SessionLocal
from src.database.models import Experiment
from src.genetic_algorithm.genetic_algorithm import GeneticAlgorithm, GAConfig, ReplacementStrategy
from src.genetic_algorithm.selection import SelectionMethod
from src.genetic_algorithm.crossover import CrossoverMethod
from src.genetic_algorithm.mutation import MutationMethod
from src.genetic_algorithm.fitness import FitnessType
from data.hospitais_sp import (
    scenario_large, scenario_medium, scenario_small, 
    scenario_critical_only, get_all_hospitals
)
from src.genetic_algorithm.chromosome import DeliveryPoint, Vehicle
import json
import threading
from datetime import datetime
import traceback

# Cria tabelas se não existirem
Base.metadata.create_all(bind=engine)

def create_delivery_points_from_data(hospitals):
    points = []
    for h in hospitals:
        point = DeliveryPoint(
            id=h.id,
            name=h.name,
            x=h.longitude,
            y=h.latitude,
            demand=h.demand,
            priority=h.priority,
            time_window=(0, 480)
        )
        points.append(point)
    return points

class ExperimentManager:
    def __init__(self):
        pass

    def get_db(self):
        return SessionLocal()

    def create_experiment(self, config_dict: dict):
        """Cria um registro de experimento no banco."""
        db = self.get_db()
        try:
            experiment = Experiment(
                status="pending",
                config=config_dict,
                created_at=datetime.utcnow()
            )
            db.add(experiment)
            db.commit()
            db.refresh(experiment)
            return experiment
        finally:
            db.close()

    def complete_experiment(self, experiment_id: int, result: dict):
        """Marca experimento como completo e salva resultados."""
        self.update_experiment_result(
            experiment_id=experiment_id,
            result_details=result,  # Save full result dict (incl. initial_fitness routes)
            best_fitness=result.get("best_fitness", 0.0),
            generations=result.get("generations_run", 0),
            execution_time=result.get("execution_time", 0.0),
            status="completed"
        )

    def update_experiment_result(self, experiment_id: int, result_details: dict, 
                               best_fitness: float, generations: int, 
                               execution_time: float, status: str = "completed"):
        """Atualiza o resultado de um experimento existente."""
        db = self.get_db()
        try:
            experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
            if experiment:
                experiment.status = status
                experiment.best_fitness = best_fitness
                experiment.generations_run = generations
                experiment.execution_time = execution_time
                experiment.result_details = result_details
                db.commit()
        except Exception as e:
            print(f"Erro ao atualizar experimento: {e}")
        finally:
            db.close()

    def run_experiment_background(self, experiment_id: int):
        """Inicia experimentos em background."""
        thread = threading.Thread(target=self._run_process, args=(experiment_id,))
        thread.start()

    def _run_process(self, experiment_id: int):
        """Lógica de execução do AG."""
        db = self.get_db()
        experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
        
        if not experiment:
            return

        try:
            experiment.status = "running"
            db.commit()

            conf = experiment.config
            
            # Converte dicionário para GAConfig
            ga_config = GAConfig(
                population_size=conf.get('population_size', 100),
                max_generations=conf.get('max_generations', 200),
                crossover_rate=conf.get('crossover_rate', 0.9),
                mutation_rate=conf.get('mutation_rate', 0.15),
                selection_method=SelectionMethod(conf.get('selection_method', 'tournament')),
                crossover_method=CrossoverMethod(conf.get('crossover_method', 'order_crossover')),
                mutation_method=MutationMethod(conf.get('mutation_method', 'inversion')),
                replacement_strategy=ReplacementStrategy(conf.get('replacement_strategy', 'elitist')), 
                fitness_type=FitnessType(conf.get('fitness_type', 'weighted_multi_objective')),
                elite_size=conf.get('elite_size', 2),
                tournament_size=conf.get('tournament_size', 3),
                stagnation_limit=conf.get('stagnation_limit', 50),
                heuristic_init_ratio=conf.get('heuristic_init_ratio', 0.2),
                verbose=False
            )

            # Seleciona o cenário
            scenario_name = conf.get('scenario', 'large')
            if scenario_name == 'small':
                hospitals = scenario_small()
            elif scenario_name == 'medium':
                hospitals = scenario_medium()
            elif scenario_name == 'critical':
                hospitals = scenario_critical_only()
            else:
                hospitals = scenario_large()

            delivery_points = create_delivery_points_from_data(hospitals)
            
            # Cria veículos com parâmetros configurados
            num_vehicles = conf.get('num_vehicles', 3)
            v_cap = conf.get('vehicle_capacity', 100.0)
            v_speed = conf.get('vehicle_speed', 40.0)
            v_dist = conf.get('vehicle_max_distance', 200.0)
            
            vehicles = []
            for i in range(num_vehicles):
                vehicles.append(Vehicle(
                    id=i,
                    capacity=v_cap,
                    max_distance=v_dist,
                    speed=v_speed
                ))

            ga = GeneticAlgorithm(
                config=ga_config,
                delivery_points=delivery_points,
                vehicles=vehicles,
                depot_index=0
            )

            result = ga.run()

            # Atualiza experimento com sucesso
            experiment.status = "completed"
            experiment.best_fitness = result.best_fitness
            experiment.generations_run = result.generations_run
            experiment.execution_time = result.execution_time
            experiment.result_details = ga.get_solution_details()
            
            db.commit()

        except Exception as e:
            print(f"Erro na execução do experimento {experiment_id}: {e}")
            traceback.print_exc()
            experiment.status = "failed"
            # Opcional: salvar erro no banco
            db.commit()
        finally:
            db.close()

    def list_experiments(self, limit=10):
        db = self.get_db()
        try:
            return db.query(Experiment).order_by(Experiment.created_at.desc()).limit(limit).all()
        finally:
            db.close()

    def get_experiment(self, experiment_id: int):
        db = self.get_db()
        try:
            return db.query(Experiment).filter(Experiment.id == experiment_id).first()
        finally:
            db.close()

    def get_scenario_data(self, scenario_name: str):
        """Retorna os pontos de um cenário específico."""
        if scenario_name == 'small':
            hospitals = scenario_small()
        elif scenario_name == 'medium':
            hospitals = scenario_medium()
        elif scenario_name == 'critical':
            hospitals = scenario_critical_only()
        else:
            hospitals = scenario_large()
            
        return [
            {
                "id": h.id,
                "name": h.name,
                "lat": h.latitude,
                "lon": h.longitude,
                "priority": h.priority,
                "type": "depot" if h.id == 0 else "hospital" # Assumindo Deposito ID 0
            }
            for h in hospitals
        ]

    def delete_experiment(self, experiment_id: int):
        """Remove um experimento pelo ID."""
        db = self.get_db()
        try:
            exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
            if exp:
                db.delete(exp)
                db.commit()
                return True
            return False
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()

    def delete_all_experiments(self):
        """Remove TODOS os experimentos."""
        db = self.get_db()
        try:
            db.query(Experiment).delete()
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()

    def delete_failed_experiments(self):
        """Remove experimentos falhados ou incompletos."""
        db = self.get_db()
        try:
            # Apaga failed ou pending/running antigos se necessário (aqui focamos em 'failed')
            db.query(Experiment).filter(Experiment.status == "failed").delete()
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()

from sqlalchemy.orm import Session
from src.database.database import SessionLocal
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
from datetime import datetime, timezone, timedelta
import traceback


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
                created_at=datetime.now(timezone.utc)
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
                max_generations=conf.get('max_generations', 10000),
                crossover_rate=conf.get('crossover_rate', 0.9),
                mutation_rate=conf.get('mutation_rate', 0.15),
                selection_method=SelectionMethod(conf.get('selection_method', 'tournament')),
                crossover_method=CrossoverMethod(conf.get('crossover_method', 'order_crossover')),
                mutation_method=MutationMethod(conf.get('mutation_method', 'inversion')),
                replacement_strategy=ReplacementStrategy(conf.get('replacement_strategy', 'elitist')), 
                fitness_type=FitnessType(conf.get('fitness_type', 'weighted_multi_objective')),
                elite_size=conf.get('elite_size', 2),
                tournament_size=conf.get('tournament_size', 3),
                stagnation_enabled=conf.get('stagnation_enabled', True),
                stagnation_limit=conf.get('stagnation_limit', 5000),
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
            for i in range(1, num_vehicles + 1):
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

    def list_experiments(self, limit=1000, offset=0, include_details=False):
        """
        Lista experimentos com suporte a paginação.

        Args:
            limit: Número máximo de experimentos (padrão: 1000)
            offset: Número de registros a pular para paginação (padrão: 0)
            include_details: Se True, carrega result_details (JSONs grandes)
        """
        db = self.get_db()
        try:
            experiments = (
                db.query(Experiment)
                .order_by(Experiment.created_at.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )

            # Converte para dicionários dentro da sessão para evitar DetachedInstanceError
            results = []
            for exp in experiments:
                exp_dict = {
                    "id": exp.id,
                    "created_at": exp.created_at,
                    "status": exp.status,
                    "config": exp.config,
                    "best_fitness": exp.best_fitness,
                    "generations_run": exp.generations_run,
                    "execution_time": exp.execution_time,
                    "result_details": exp.result_details if include_details else None
                }
                results.append(exp_dict)
            return results
        finally:
            db.close()

    def count_experiments(self, status: str = None):
        """
        Conta o total de experimentos, opcionalmente filtrado por status.

        Args:
            status: Filtrar por status ('completed', 'failed', 'running', 'pending') ou None para todos
        """
        db = self.get_db()
        try:
            query = db.query(Experiment)
            if status:
                query = query.filter(Experiment.status == status)
            return query.count()
        finally:
            db.close()

    def get_statistics(self):
        """
        Retorna estatísticas agregadas de TODOS os experimentos no banco.

        Returns:
            dict com:
            - total: total de experimentos
            - completed: experimentos completados
            - failed: experimentos falhados
            - running: experimentos em execução
            - pending: experimentos pendentes
            - best_fitness: melhor fitness global (menor valor)
            - avg_fitness: fitness médio final (apenas completados)
            - avg_initial_fitness: fitness inicial médio
            - avg_improvement: melhoria percentual média
            - avg_generations: média de gerações (apenas completados)
            - avg_execution_time: tempo médio de execução (apenas completados)
        """
        db = self.get_db()
        try:
            from sqlalchemy import func
            import json

            # Contadores por status
            total = db.query(Experiment).count()
            completed = db.query(Experiment).filter(Experiment.status == 'completed').count()
            failed = db.query(Experiment).filter(Experiment.status == 'failed').count()
            running = db.query(Experiment).filter(Experiment.status == 'running').count()
            pending = db.query(Experiment).filter(Experiment.status == 'pending').count()

            # Estatísticas de experimentos completados
            completed_query = db.query(Experiment).filter(Experiment.status == 'completed')

            # Melhor fitness global (menor valor)
            best_fitness = completed_query.with_entities(func.min(Experiment.best_fitness)).scalar()

            # Médias simples (SQL)
            avg_fitness = completed_query.with_entities(func.avg(Experiment.best_fitness)).scalar()
            avg_generations = completed_query.with_entities(func.avg(Experiment.generations_run)).scalar()
            avg_execution_time = completed_query.with_entities(func.avg(Experiment.execution_time)).scalar()

            # Para fitness inicial e melhoria, precisamos processar o JSON
            completed_experiments = completed_query.all()
            initial_fitnesses = []
            improvements = []

            for exp in completed_experiments:
                if exp.result_details:
                    try:
                        details = exp.result_details if isinstance(exp.result_details, dict) else json.loads(exp.result_details)
                        initial = details.get('initial_fitness', 0)
                        final = exp.best_fitness

                        if initial and initial > 0:
                            initial_fitnesses.append(initial)
                            improvement_pct = ((initial - final) / initial) * 100
                            improvements.append(improvement_pct)
                    except:
                        pass

            avg_initial_fitness = sum(initial_fitnesses) / len(initial_fitnesses) if initial_fitnesses else 0.0
            avg_improvement = sum(improvements) / len(improvements) if improvements else 0.0

            return {
                'total': total,
                'completed': completed,
                'failed': failed,
                'running': running,
                'pending': pending,
                'best_fitness': float(best_fitness) if best_fitness else 0.0,
                'avg_fitness': float(avg_fitness) if avg_fitness else 0.0,
                'avg_initial_fitness': float(avg_initial_fitness),
                'avg_improvement': float(avg_improvement),
                'avg_generations': float(avg_generations) if avg_generations else 0.0,
                'avg_execution_time': float(avg_execution_time) if avg_execution_time else 0.0
            }
        finally:
            db.close()

    def get_experiment(self, experiment_id: int):
        db = self.get_db()
        try:
            exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
            if exp is None:
                return None
            # Converte para dicionário dentro da sessão para evitar DetachedInstanceError
            return {
                "id": exp.id,
                "created_at": exp.created_at,
                "status": exp.status,
                "config": exp.config,
                "best_fitness": exp.best_fitness,
                "generations_run": exp.generations_run,
                "execution_time": exp.execution_time,
                "result_details": exp.result_details
            }
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
        """
        Remove experimentos problemáticos:
        1. Status 'failed'
        2. Status 'running' ou 'pending' há mais de 30 minutos (travados)
        3. best_fitness é NULL ou NaN (independente do status)
        """
        db = self.get_db()
        try:
            import math

            # 1. Remove experimentos com status 'failed'
            deleted_failed = db.query(Experiment).filter(Experiment.status == "failed").delete(synchronize_session=False)

            # 2. Remove experimentos 'running' ou 'pending' há mais de 30 minutos (travados)
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=30)
            deleted_stale = db.query(Experiment).filter(
                Experiment.status.in_(["running", "pending"]),
                Experiment.created_at < cutoff_time
            ).delete(synchronize_session=False)

            # 3. Remove experimentos com best_fitness NULL ou NaN
            # SQLite: NULL é detectado com is_(None)
            experiments_with_null = db.query(Experiment).filter(Experiment.best_fitness.is_(None)).all()
            deleted_null = 0
            for exp in experiments_with_null:
                db.delete(exp)
                deleted_null += 1

            # 4. Remove experimentos com best_fitness = NaN (representado como string 'NaN' no JSON ou float nan)
            all_experiments = db.query(Experiment).all()
            deleted_nan = 0
            for exp in all_experiments:
                if exp.best_fitness is not None:
                    try:
                        if math.isnan(exp.best_fitness) or math.isinf(exp.best_fitness):
                            db.delete(exp)
                            deleted_nan += 1
                    except (TypeError, ValueError):
                        # best_fitness não é numérico, ignora
                        pass

            db.commit()
            total_deleted = deleted_failed + deleted_stale + deleted_null + deleted_nan
            print(f"[CLEANUP] Failed: {deleted_failed} | Stale: {deleted_stale} | NULL: {deleted_null} | NaN/Inf: {deleted_nan} | Total: {total_deleted}")
            return True

        except Exception as e:
            print(f"[CLEANUP ERROR] {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
            return False
        finally:
            db.close()

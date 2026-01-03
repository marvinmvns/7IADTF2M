import requests
import time
import sys
import os
import json
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

# Adiciona o diretório raiz ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database.models import Experiment
from src.database.database import Base

# Configuração
API_URL = "http://localhost:8000"
DB_URL = "sqlite:///./data/experiments.db" # Caminho correto verificado em src/database/database.py

def get_db_session():
    engine = create_engine(DB_URL)
    Base.metadata.create_all(bind=engine)
    return Session(bind=engine)

def test_api_execution_and_persistence():
    print("=" * 60)
    print("TESTE DE INTEGRAÇÃO: API -> EXECUÇÃO -> BANCO DE DADOS")
    print("=" * 60)

    # 1. Configuração do Experimento (Rápido)
    payload = {
        "population_size": 20,
        "max_generations": 10,
        "crossover_rate": 0.8,
        "mutation_rate": 0.1,
        "scenario": "small",
        "num_vehicles": 2,
        "selection_method": "tournament",
        "crossover_method": "position_based_crossover", # Testando o novo Crossover também!
        "mutation_method": "inversion"
    }

    print("\n[1] Enviando requisição para iniciar experimento...")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(f"{API_URL}/run", json=payload)
        response.raise_for_status()
        data = response.json()
        experiment_id = data["id"]
        print(f"    -> Sucesso! Experimento ID: {experiment_id}, Status: {data['status']}")
    except Exception as e:
        print(f"    -> Falha ao iniciar experimento: {e}")
        return

    # 2. Polling de Status
    print(f"\n[2] Aguardando conclusão (Polling ID {experiment_id})...")
    status = "pending"
    max_retries = 30 # 30 segundos max
    retries = 0
    
    while status in ["pending", "running"] and retries < max_retries:
        time.sleep(1)
        try:
            resp = requests.get(f"{API_URL}/experiments/{experiment_id}")
            resp.raise_for_status()
            exp_data = resp.json()
            status = exp_data["status"]
            gen = exp_data.get("generations_run")
            fit = exp_data.get("best_fitness")
            print(f"    -> Tentativa {retries+1}: Status={status}, Geração={gen}, Fitness={fit}")
        except Exception as e:
            print(f"    -> Erro no polling: {e}")
            break
        retries += 1

    if status != "completed":
        print(f"\n[CRÍTICO] Experimento não completou. Status final: {status}")
        return

    # 3. Validação no Banco de Dados
    print("\n[3] Validando persistência direta no Banco de Dados...")
    try:
        session = get_db_session()
        db_exp = session.query(Experiment).filter(Experiment.id == experiment_id).first()
        
        if not db_exp:
            print(f"    -> [ERRO] Experimento {experiment_id} não encontrado no banco!")
        else:
            print(f"    -> Registro encontrado no banco!")
            print(f"       ID: {db_exp.id}")
            print(f"       Status: {db_exp.status}")
            print(f"       Best Fitness: {db_exp.best_fitness}")
            print(f"       Gerações: {db_exp.generations_run}")
            print(f"       JSON Config salvo: {db_exp.config is not None}")
            print(f"       JSON Detalhes salvo: {db_exp.result_details is not None}")
            
            if db_exp.status == "completed" and db_exp.best_fitness is not None:
                print("\n[SUCESSO] O fluxo completo API -> Execução -> Banco foi validado!")
            else:
                print("\n[FALHA] O registro no banco está incompleto ou incorreto.")
                
        session.close()

    except Exception as e:
        print(f"    -> Erro ao conectar no banco: {e}")

if __name__ == "__main__":
    test_api_execution_and_persistence()

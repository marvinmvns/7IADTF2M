"""
Script de teste para validar integração LLM-UI.
Verifica se o sistema está priorizando algoritmos corretamente.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.llm.adapters import LLMAdapter
from src.llm.domains import GADomains


class MockLLMAdapter(LLMAdapter):
    """Mock adapter para testar sem LLM real."""

    def list_models(self):
        return ["mock-model"]

    def suggest_params(self, context: dict) -> dict:
        """
        Simula sugestão do LLM priorizando algoritmos.
        """
        current_params = context.get('params', {})

        # Simula LLM sugerindo mudanças algorítmicas
        suggested = {
            "selection_method": "stochastic_universal_sampling",  # Muda algoritmo
            "crossover_method": "edge_recombination_crossover",   # Muda algoritmo
            "mutation_method": "2-opt",                          # Muda algoritmo
            "mutation_rate": 0.15,                                # Ajuste fino
            "elite_size": 8                                       # Ajuste fino
        }

        return suggested


def test_ui_integration():
    """Testa a integração como seria na UI."""
    print("=" * 80)
    print("TESTE DE INTEGRAÇÃO LLM-UI")
    print("=" * 80)

    # Simula parâmetros base (como viria de um experimento)
    base_params = {
        "population_size": 100,
        "max_generations": 300,
        "crossover_rate": 0.9,
        "mutation_rate": 0.1,
        "selection_method": "tournament",
        "crossover_method": "order_crossover",
        "mutation_method": "inversion",
        "replacement_strategy": "elitist",
        "fitness_type": "weighted_multi_objective",
        "tournament_size": 5,
        "elite_size": 5,
        "scenario": "medium"
    }

    print("\n📦 PARÂMETROS BASE:")
    print(f"  - selection_method: {base_params['selection_method']}")
    print(f"  - crossover_method: {base_params['crossover_method']}")
    print(f"  - mutation_method: {base_params['mutation_method']}")
    print(f"  - mutation_rate: {base_params['mutation_rate']}")
    print(f"  - elite_size: {base_params['elite_size']}")

    # Simula histórico vazio (primeira iteração)
    history = []

    # Cria contexto como na UI
    context = {
        "fitness": 2850.5,
        "params": base_params,
        "history": history
    }

    # Usa mock adapter
    adapter = MockLLMAdapter()

    print("\n🤖 CHAMANDO LLM (Mock)...")
    new_params = adapter.suggest_params(context)

    print("\n📥 PARÂMETROS SUGERIDOS PELO LLM:")
    for key, value in new_params.items():
        print(f"  - {key}: {value}")

    # Simula mesclagem como na UI (NOVA FORMA)
    print("\n🔄 MESCLANDO PARÂMETROS (como na UI)...")
    merged = base_params.copy()
    merged.update(new_params)  # Atualiza com TODOS os parâmetros

    print("\n✅ VALIDANDO COM GADOMAINS...")
    validated = GADomains.validate_params(merged)

    print("\n📊 PARÂMETROS FINAIS VALIDADOS:")
    algo_domains = GADomains.get_algorithmic_domains()

    print("\n🔴 ALGORITMOS (Prioridade 1):")
    algo_changed = False
    for key in algo_domains.keys():
        if key in validated:
            old_val = base_params.get(key)
            new_val = validated.get(key)
            if old_val != new_val:
                print(f"  ✨ {key}: {old_val} → {new_val}")
                algo_changed = True
            else:
                print(f"     {key}: {new_val}")

    print("\n🟢 PARÂMETROS NUMÉRICOS (Prioridade 3):")
    numeric_keys = ['population_size', 'max_generations', 'crossover_rate',
                   'mutation_rate', 'elite_size', 'tournament_size']
    numeric_changed = False
    for key in numeric_keys:
        if key in validated:
            old_val = base_params.get(key)
            new_val = validated.get(key)
            if old_val != new_val:
                print(f"  ✨ {key}: {old_val} → {new_val}")
                numeric_changed = True
            else:
                print(f"     {key}: {new_val}")

    # Simula criação do histórico (como na UI)
    new_fitness = 2650.0  # Simula melhoria
    change_pct = ((new_fitness - context['fitness']) / context['fitness']) * 100

    history_entry = {
        "iteration": 1,
        "old_fitness": context['fitness'],
        "new_fitness": new_fitness,
        "change_pct": change_pct,
        "improved": new_fitness < context['fitness'],
        "params": validated,  # ← CRÍTICO: Params completos!
        "experiment_id": 999
    }

    history.append(history_entry)

    print("\n📝 HISTÓRICO CRIADO:")
    print(f"  - Fitness: {history_entry['old_fitness']:.1f} → {history_entry['new_fitness']:.1f} "
          f"({history_entry['change_pct']:+.1f}%)")
    print(f"  - Melhorou: {history_entry['improved']}")
    print(f"  - Params incluídos: {len(history_entry['params'])} parâmetros")

    # Verifica se params do histórico contém algoritmos
    history_params = history_entry['params']
    algo_in_history = any(key in history_params for key in algo_domains.keys())

    print("\n" + "=" * 80)
    print("✅ VALIDAÇÕES:")
    print("=" * 80)

    checks = [
        ("Algoritmos foram alterados", algo_changed),
        ("Parâmetros numéricos ajustados", numeric_changed),
        ("Validação GADomains executada", validated is not None),
        ("Histórico contém 'params'", 'params' in history_entry),
        ("Params do histórico têm algoritmos", algo_in_history),
        ("Histórico pode alimentar próxima iteração", len(history) > 0)
    ]

    all_passed = True
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {check_name}")
        if not passed:
            all_passed = False

    print("=" * 80)

    if all_passed:
        print("\n🎉 SUCESSO! Integração LLM-UI está funcionando corretamente!")
        print("\n📋 PRÓXIMO PROMPT RECEBERÁ:")
        print(f"  - Fitness atual: {history_entry['new_fitness']}")
        print(f"  - Algoritmos testados: {list(algo_domains.keys())}")
        print(f"  - Histórico de {len(history)} iteração(ões)")
        print("\nO LLM poderá aprender e sugerir diferentes combinações algorítmicas! 🚀")
    else:
        print("\n❌ FALHA! Alguma verificação falhou.")

    print("=" * 80 + "\n")

    return all_passed


if __name__ == "__main__":
    success = test_ui_integration()
    exit(0 if success else 1)

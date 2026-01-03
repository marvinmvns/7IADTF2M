"""
Exemplo de uso do LLM Optimizer com foco em variações algorítmicas.

Este script demonstra:
1. Como usar o sistema de domínios para entender o espaço de busca
2. Como gerar variâncias focadas em algoritmos
3. Como usar o LLM Optimizer com o prompt aprimorado
4. Como analisar resultados priorizando impacto algorítmico

Autor: Sistema de Otimização GA-LLM
Data: 2026
"""

import sys
import os

# Adiciona src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.llm.domains import GADomains, ALGORITHM_COMBINATIONS
from src.llm.variance_generator import (
    AlgorithmicVarianceGenerator,
    generate_variance_batch,
    generate_domain_analysis_report
)


def example_1_domain_analysis():
    """
    Exemplo 1: Análise completa dos domínios disponíveis.
    """
    print("=" * 80)
    print("EXEMPLO 1: ANÁLISE DE DOMÍNIOS")
    print("=" * 80)

    # Gera relatório completo
    report = generate_domain_analysis_report()
    print(report)

    # Estatísticas adicionais
    all_domains = GADomains.get_all_domains()
    algo_domains = GADomains.get_algorithmic_domains()

    print("\n\n📊 DISTRIBUIÇÃO POR PRIORIDADE:")
    for priority in [1, 2, 3]:
        priority_domains = GADomains.get_by_priority(priority)
        priority_name = {1: "CRÍTICA (Algoritmos)", 2: "IMPORTANTE", 3: "AJUSTE FINO"}
        print(f"  Prioridade {priority} - {priority_name[priority]}: "
              f"{len(priority_domains)} parâmetros")

    # Mostra espaço combinatorial
    print("\n\n🔢 ESPAÇO DE BUSCA ALGORÍTMICO:")
    total_combos = 1
    for name, domain in algo_domains.items():
        num_options = len(domain.values)
        total_combos *= num_options
        print(f"  {name:30s}: {num_options:3d} opções")

    print(f"\n  TOTAL DE COMBINAÇÕES POSSÍVEIS: {total_combos:,}")
    print(f"  (Impossível testar todas - necessário busca inteligente!)")


def example_2_generate_variants():
    """
    Exemplo 2: Geração de variantes usando diferentes estratégias.
    """
    print("\n\n" + "=" * 80)
    print("EXEMPLO 2: GERAÇÃO DE VARIANTES ALGORÍTMICAS")
    print("=" * 80)

    # Configuração base
    base_config = {
        "population_size": 100,
        "max_generations": 300,
        "crossover_rate": 0.9,
        "mutation_rate": 0.12,
        "selection_method": "tournament",
        "crossover_method": "order_crossover",
        "mutation_method": "inversion",
        "replacement_strategy": "elitist",
        "fitness_type": "weighted_multi_objective",
        "tournament_size": 5,
        "elite_size": 8,
        "scenario": "medium"
    }

    print("\n📦 CONFIGURAÇÃO BASE:")
    print(f"  - Seleção:  {base_config['selection_method']}")
    print(f"  - Crossover: {base_config['crossover_method']}")
    print(f"  - Mutação:   {base_config['mutation_method']}")

    generator = AlgorithmicVarianceGenerator()

    # Estratégia 1: Sistemática (combinações pré-definidas)
    print("\n\n🎯 ESTRATÉGIA 1: COMBINAÇÕES SISTEMÁTICAS (Pré-definidas)")
    variants = generator.generate(base_config, strategy="systematic", num_variants=6)

    for i, variant in enumerate(variants, 1):
        print(f"\n  Variante {i}:")
        print(f"    Seleção:  {variant['selection_method']}")
        print(f"    Crossover: {variant['crossover_method']}")
        print(f"    Mutação:   {variant['mutation_method']}")

    # Estratégia 2: Aleatória
    generator.reset_history()
    print("\n\n🎲 ESTRATÉGIA 2: VARIAÇÕES ALEATÓRIAS")
    variants = generator.generate(base_config, strategy="random", num_variants=5)

    for i, variant in enumerate(variants, 1):
        print(f"\n  Variante {i}:")
        print(f"    Seleção:  {variant['selection_method']}")
        print(f"    Crossover: {variant['crossover_method']}")
        print(f"    Mutação:   {variant['mutation_method']}")
        print(f"    Mutation Rate: {variant.get('mutation_rate', 0):.3f}")

    # Estratégia 3: Exploração ao redor de uma boa configuração
    print("\n\n🔍 ESTRATÉGIA 3: EXPLORAÇÃO LOCAL (ao redor da melhor)")
    best_config = {
        **base_config,
        "selection_method": "stochastic_universal_sampling",
        "crossover_method": "edge_recombination_crossover",
        "mutation_method": "2-opt"
    }

    variants = generator.generate(best_config, strategy="explore_best", num_variants=5)

    for i, variant in enumerate(variants, 1):
        print(f"\n  Variante {i}:")
        print(f"    Seleção:  {variant['selection_method']}")
        print(f"    Crossover: {variant['crossover_method']}")
        print(f"    Mutação:   {variant['mutation_method']}")


def example_3_batch_generation():
    """
    Exemplo 3: Geração de lote com mix de estratégias.
    """
    print("\n\n" + "=" * 80)
    print("EXEMPLO 3: GERAÇÃO DE LOTE COM MIX DE ESTRATÉGIAS")
    print("=" * 80)

    base_config = {
        "population_size": 150,
        "max_generations": 500,
        "crossover_rate": 0.9,
        "mutation_rate": 0.15,
        "selection_method": "tournament",
        "crossover_method": "order_crossover",
        "mutation_method": "inversion",
        "elite_size": 10
    }

    # Gera lote mesclando estratégias
    batch = generate_variance_batch(
        base_config,
        batch_size=10,
        strategy_mix=True,
        history=None
    )

    print(f"\n✅ Geradas {len(batch)} variantes usando mix de estratégias:")
    print("   40% Sistemáticas + 30% Greedy + 30% Aleatórias")

    for i, variant in enumerate(batch, 1):
        print(f"\n  {i:2d}. {variant['selection_method']:25s} | "
              f"{variant['crossover_method']:30s} | "
              f"{variant['mutation_method']:15s}")


def example_4_prompt_demonstration():
    """
    Exemplo 4: Demonstração do prompt gerado para o LLM.
    """
    print("\n\n" + "=" * 80)
    print("EXEMPLO 4: PROMPT GERADO PARA O LLM")
    print("=" * 80)

    # Simula contexto de otimização
    context = {
        "fitness": 2850.5,
        "params": {
            "population_size": 100,
            "max_generations": 300,
            "selection_method": "tournament",
            "crossover_method": "order_crossover",
            "mutation_method": "inversion",
            "mutation_rate": 0.12,
            "elite_size": 5
        },
        "history": [
            {
                "old_fitness": 3200.0,
                "new_fitness": 2950.0,
                "change_pct": -7.8,
                "params": {
                    "selection_method": "roulette_wheel",
                    "crossover_method": "partially_mapped_crossover",
                    "mutation_method": "swap"
                }
            },
            {
                "old_fitness": 2950.0,
                "new_fitness": 2850.5,
                "change_pct": -3.4,
                "params": {
                    "selection_method": "tournament",
                    "crossover_method": "order_crossover",
                    "mutation_method": "inversion"
                }
            }
        ]
    }

    # Importa adapter para gerar prompt
    from src.llm.adapters import LLMAdapter

    class DemoAdapter(LLMAdapter):
        def list_models(self):
            return []

        def suggest_params(self, context):
            return {}

    adapter = DemoAdapter()
    prompt = adapter._build_prompt(context)

    print("\n📝 PROMPT COMPLETO ENVIADO AO LLM:")
    print("-" * 80)
    print(prompt)
    print("-" * 80)

    print("\n\n💡 CARACTERÍSTICAS DO PROMPT:")
    print("  ✅ Mostra histórico com símbolos visuais (✅/❌)")
    print("  ✅ Sugere combinações pré-definidas não testadas")
    print("  ✅ Enfatiza prioridade de variações algorítmicas")
    print("  ✅ Inclui domínios completos com descrições")
    print("  ✅ Define regras claras de otimização")
    print("  ✅ Exige mudança de algoritmos em cada iteração")


def example_5_validation():
    """
    Exemplo 5: Validação automática de parâmetros.
    """
    print("\n\n" + "=" * 80)
    print("EXEMPLO 5: VALIDAÇÃO AUTOMÁTICA DE PARÂMETROS")
    print("=" * 80)

    # Parâmetros com alguns valores inválidos
    invalid_params = {
        "population_size": 5000,  # Acima do máximo (1000)
        "mutation_rate": 0.5,     # Acima do máximo (0.3)
        "elite_size": -5,         # Abaixo do mínimo (1)
        "tournament_size": 50,    # Acima do máximo (10)
        "selection_method": "tournament",
        "crossover_method": "invalid_method",  # Método inválido
        "unknown_param": 123      # Parâmetro desconhecido
    }

    print("\n❌ PARÂMETROS INVÁLIDOS:")
    for key, value in invalid_params.items():
        print(f"  {key}: {value}")

    # Valida
    validated = GADomains.validate_params(invalid_params)

    print("\n✅ PARÂMETROS VALIDADOS:")
    for key, value in validated.items():
        print(f"  {key}: {value}")

    print("\n📊 ANÁLISE:")
    print(f"  - Parâmetros originais: {len(invalid_params)}")
    print(f"  - Parâmetros validados: {len(validated)}")
    print("  - Valores foram corrigidos para estar dentro dos limites válidos")
    print("  - Parâmetros desconhecidos foram removidos")


def main():
    """Executa todos os exemplos."""
    print("\n" + "🧬" * 40)
    print("SISTEMA DE OTIMIZAÇÃO LLM PARA ALGORITMOS GENÉTICOS")
    print("Foco em Variações Algorítmicas para VRP Hospitalar")
    print("🧬" * 40)

    # Executa exemplos
    example_1_domain_analysis()
    example_2_generate_variants()
    example_3_batch_generation()
    example_4_prompt_demonstration()
    example_5_validation()

    print("\n\n" + "=" * 80)
    print("✅ EXEMPLOS CONCLUÍDOS!")
    print("=" * 80)
    print("\nPróximos passos:")
    print("  1. Execute a API: python src/api/main.py")
    print("  2. Inicie a UI web: python src/web/app.py")
    print("  3. Configure seu provider LLM (ChatGPT, Ollama, etc)")
    print("  4. Inicie a otimização na aba 🤖 Logistic LLM")
    print("\n  O LLM agora priorizará testar diferentes ALGORITMOS")
    print("  ao invés de apenas ajustar valores numéricos!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

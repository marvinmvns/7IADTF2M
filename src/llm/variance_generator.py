"""
Gerador de Variâncias para Algoritmos Genéticos.
Cria combinações inteligentes de parâmetros priorizando variações algorítmicas.
"""
import random
import itertools
from typing import List, Dict, Any, Tuple, Optional
from .domains import GADomains, ALGORITHM_COMBINATIONS


class VarianceStrategy:
    """Estratégias de geração de variância."""

    @staticmethod
    def random_algorithmic(base_params: dict, num_variants: int = 10) -> List[dict]:
        """
        Gera variantes focando em combinações algorítmicas aleatórias.

        Args:
            base_params: Parâmetros base
            num_variants: Número de variantes a gerar

        Returns:
            Lista de configurações variadas
        """
        variants = []
        algo_domains = GADomains.get_algorithmic_domains()

        for _ in range(num_variants):
            variant = base_params.copy()

            # Altera 2-3 algoritmos aleatoriamente
            num_changes = random.randint(2, 3)
            domains_to_change = random.sample(list(algo_domains.keys()), num_changes)

            for domain_name in domains_to_change:
                domain = algo_domains[domain_name]
                current_value = variant.get(domain_name)

                # Escolhe valor diferente do atual
                options = [v for v in domain.values if v != current_value]
                if options:
                    variant[domain_name] = random.choice(options)

            # Pequenas variações numéricas (10-20% de chance)
            if random.random() < 0.2:
                numeric_params = ['mutation_rate', 'crossover_rate', 'elite_size']
                param = random.choice(numeric_params)
                if param in variant:
                    domain = GADomains.get_all_domains().get(param)
                    if domain and domain.range:
                        min_val, max_val = domain.range
                        variant[param] = random.uniform(min_val, max_val)

            variants.append(variant)

        return variants

    @staticmethod
    def systematic_combinations(base_params: dict, max_variants: int = 20) -> List[dict]:
        """
        Gera variantes testando combinações sistemáticas de algoritmos.
        Usa as combinações pré-definidas como ponto de partida.

        Args:
            base_params: Parâmetros base
            max_variants: Número máximo de variantes

        Returns:
            Lista de configurações variadas
        """
        variants = []

        # Adiciona todas as combinações pré-definidas
        for combo_name, combo_data in ALGORITHM_COMBINATIONS.items():
            variant = base_params.copy()
            variant['selection_method'] = combo_data['selection_method']
            variant['crossover_method'] = combo_data['crossover_method']
            variant['mutation_method'] = combo_data['mutation_method']
            variants.append(variant)

        # Se precisar de mais variantes, cria combinações sistemáticas
        if len(variants) < max_variants:
            selection_methods = GADomains.SELECTION_METHODS.values
            crossover_methods = GADomains.CROSSOVER_METHODS.values
            mutation_methods = GADomains.MUTATION_METHODS.values

            # Amostra aleatória de combinações
            all_combos = list(itertools.product(
                random.sample(selection_methods, min(3, len(selection_methods))),
                random.sample(crossover_methods, min(4, len(crossover_methods))),
                random.sample(mutation_methods, min(4, len(mutation_methods)))
            ))

            random.shuffle(all_combos)

            for sel, cross, mut in all_combos[:max_variants - len(variants)]:
                variant = base_params.copy()
                variant['selection_method'] = sel
                variant['crossover_method'] = cross
                variant['mutation_method'] = mut
                variants.append(variant)

        return variants[:max_variants]

    @staticmethod
    def explore_around_best(best_params: dict, num_variants: int = 5) -> List[dict]:
        """
        Gera variantes explorando ao redor da melhor configuração encontrada.
        Mantém 1-2 algoritmos e varia os outros.

        Args:
            best_params: Melhores parâmetros encontrados
            num_variants: Número de variantes

        Returns:
            Lista de configurações variadas
        """
        variants = []
        algo_domains = GADomains.get_algorithmic_domains()
        algo_keys = list(algo_domains.keys())

        for _ in range(num_variants):
            variant = best_params.copy()

            # Mantém 1-2 algoritmos, muda os outros
            num_to_keep = random.randint(1, 2)
            to_keep = set(random.sample(algo_keys, num_to_keep))

            for algo_key in algo_keys:
                if algo_key not in to_keep:
                    domain = algo_domains[algo_key]
                    current_value = variant.get(algo_key)
                    options = [v for v in domain.values if v != current_value]
                    if options:
                        variant[algo_key] = random.choice(options)

            # Pequenas variações numéricas também
            numeric_domains = GADomains.get_by_priority(3)
            for param_name in ['mutation_rate', 'elite_size', 'tournament_size']:
                if param_name in numeric_domains and param_name in variant:
                    domain = numeric_domains[param_name]
                    if domain.range:
                        current_val = variant[param_name]
                        min_val, max_val = domain.range
                        # Variação de ±20%
                        delta = (max_val - min_val) * 0.2
                        new_val = current_val + random.uniform(-delta, delta)
                        variant[param_name] = max(min_val, min(max_val, new_val))

            variants.append(variant)

        return variants

    @staticmethod
    def greedy_improvement(current_params: dict, history: List[dict],
                          num_variants: int = 5) -> List[dict]:
        """
        Gera variantes baseado no histórico, priorizando direções promissoras.

        Args:
            current_params: Parâmetros atuais
            history: Histórico de tentativas anteriores
            num_variants: Número de variantes

        Returns:
            Lista de configurações variadas
        """
        variants = []

        if not history:
            # Sem histórico, usa estratégia aleatória
            return VarianceStrategy.random_algorithmic(current_params, num_variants)

        # Identifica combinações que melhoraram
        improvements = []
        for entry in history:
            if entry.get('improved', False):
                improvements.append(entry.get('params', {}))

        if not improvements:
            # Nenhuma melhoria ainda, explora drasticamente
            return VarianceStrategy.random_algorithmic(current_params, num_variants)

        # Explora ao redor das melhores
        for best_params in improvements[-3:]:  # Últimas 3 melhorias
            variants.extend(VarianceStrategy.explore_around_best(
                best_params, num_variants=max(1, num_variants // len(improvements[-3:]))
            ))

        # Completa com algumas aleatórias
        if len(variants) < num_variants:
            variants.extend(VarianceStrategy.random_algorithmic(
                current_params, num_variants - len(variants)
            ))

        return variants[:num_variants]


class AlgorithmicVarianceGenerator:
    """
    Gerador principal de variâncias focado em algoritmos.
    Orquestra diferentes estratégias de geração.
    """

    def __init__(self):
        self.tested_combinations = set()

    def generate(self, base_params: dict, strategy: str = "random",
                 num_variants: int = 10, history: Optional[List[dict]] = None) -> List[dict]:
        """
        Gera variantes de configuração baseado na estratégia escolhida.

        Args:
            base_params: Parâmetros base
            strategy: Estratégia ("random", "systematic", "greedy", "explore_best")
            num_variants: Número de variantes a gerar
            history: Histórico de execuções (para estratégia greedy)

        Returns:
            Lista de configurações variadas
        """
        if strategy == "random":
            variants = VarianceStrategy.random_algorithmic(base_params, num_variants)
        elif strategy == "systematic":
            variants = VarianceStrategy.systematic_combinations(base_params, num_variants)
        elif strategy == "explore_best":
            variants = VarianceStrategy.explore_around_best(base_params, num_variants)
        elif strategy == "greedy":
            variants = VarianceStrategy.greedy_improvement(
                base_params, history or [], num_variants
            )
        else:
            raise ValueError(f"Estratégia desconhecida: {strategy}")

        # Filtra duplicatas
        unique_variants = []
        for variant in variants:
            combo = self._get_combo_signature(variant)
            if combo not in self.tested_combinations:
                self.tested_combinations.add(combo)
                unique_variants.append(variant)

        return unique_variants

    def _get_combo_signature(self, params: dict) -> Tuple:
        """Cria assinatura única de uma combinação de algoritmos."""
        return (
            params.get('selection_method', ''),
            params.get('crossover_method', ''),
            params.get('mutation_method', ''),
            params.get('fitness_type', ''),
            params.get('replacement_strategy', '')
        )

    def reset_history(self):
        """Reseta o histórico de combinações testadas."""
        self.tested_combinations.clear()

    def get_untested_combinations(self, base_params: dict,
                                 num_combinations: int = 5) -> List[dict]:
        """
        Retorna combinações pré-definidas que ainda não foram testadas.

        Args:
            base_params: Parâmetros base
            num_combinations: Número de combinações desejadas

        Returns:
            Lista de configurações não testadas
        """
        untested = []

        for combo_name, combo_data in ALGORITHM_COMBINATIONS.items():
            variant = base_params.copy()
            variant['selection_method'] = combo_data['selection_method']
            variant['crossover_method'] = combo_data['crossover_method']
            variant['mutation_method'] = combo_data['mutation_method']

            combo_sig = self._get_combo_signature(variant)
            if combo_sig not in self.tested_combinations:
                untested.append(variant)

        return untested[:num_combinations]


def generate_variance_batch(base_params: dict, batch_size: int = 10,
                           strategy_mix: bool = True,
                           history: Optional[List[dict]] = None) -> List[dict]:
    """
    Função auxiliar para gerar um lote de variações.

    Args:
        base_params: Parâmetros base
        batch_size: Tamanho do lote
        strategy_mix: Se True, mistura diferentes estratégias
        history: Histórico para estratégia greedy

    Returns:
        Lista de configurações variadas
    """
    generator = AlgorithmicVarianceGenerator()

    if not strategy_mix:
        return generator.generate(base_params, "random", batch_size, history)

    # Mistura estratégias
    variants = []

    # 40% sistemáticas
    variants.extend(generator.generate(
        base_params, "systematic", int(batch_size * 0.4), history
    ))

    # 30% greedy (se tiver histórico)
    if history:
        variants.extend(generator.generate(
            base_params, "greedy", int(batch_size * 0.3), history
        ))

    # 30% aleatórias
    remaining = batch_size - len(variants)
    variants.extend(generator.generate(
        base_params, "random", remaining, history
    ))

    return variants[:batch_size]


# Função para criar documento de análise de domínio
def generate_domain_analysis_report() -> str:
    """
    Gera relatório completo de análise de domínios para documentação.

    Returns:
        String com relatório formatado
    """
    all_domains = GADomains.get_all_domains()
    algo_domains = GADomains.get_algorithmic_domains()

    report = []
    report.append("=" * 80)
    report.append("RELATÓRIO DE ANÁLISE DE DOMÍNIOS - ALGORITMO GENÉTICO VRP")
    report.append("=" * 80)
    report.append("")

    # Estatísticas gerais
    report.append("📊 ESTATÍSTICAS GERAIS:")
    report.append(f"  - Total de parâmetros: {len(all_domains)}")
    report.append(f"  - Parâmetros algorítmicos (enums): {len(algo_domains)}")
    report.append(f"  - Parâmetros numéricos: {len(all_domains) - len(algo_domains)}")
    report.append("")

    # Espaço de busca combinatório
    total_combinations = 1
    for domain in algo_domains.values():
        total_combinations *= len(domain.values)

    report.append("🔢 ESPAÇO DE BUSCA ALGORÍTMICO:")
    report.append(f"  - Combinações possíveis (algoritmos): {total_combinations:,}")
    report.append("")

    for name, domain in algo_domains.items():
        report.append(f"  - {name}: {len(domain.values)} opções")

    report.append("")
    report.append("=" * 80)
    report.append("💡 COMBINAÇÕES PRÉ-DEFINIDAS RECOMENDADAS:")
    report.append("=" * 80)

    for combo_name, combo_data in ALGORITHM_COMBINATIONS.items():
        report.append(f"\n🎯 {combo_name.upper().replace('_', ' ')}")
        report.append(f"   Descrição: {combo_data['description']}")
        report.append(f"   - Seleção:  {combo_data['selection_method']}")
        report.append(f"   - Crossover: {combo_data['crossover_method']}")
        report.append(f"   - Mutação:   {combo_data['mutation_method']}")

    report.append("")
    report.append("=" * 80)
    report.append(GADomains.get_domain_description())
    report.append("=" * 80)

    return "\n".join(report)


if __name__ == "__main__":
    # Exemplo de uso
    print(generate_domain_analysis_report())

    print("\n\n" + "=" * 80)
    print("EXEMPLO DE GERAÇÃO DE VARIÂNCIAS")
    print("=" * 80)

    base_config = {
        "population_size": 100,
        "max_generations": 300,
        "crossover_rate": 0.9,
        "mutation_rate": 0.1,
        "selection_method": "tournament",
        "crossover_method": "order_crossover",
        "mutation_method": "inversion",
        "elite_size": 5
    }

    generator = AlgorithmicVarianceGenerator()

    print("\n📋 Variantes Sistemáticas:")
    variants = generator.generate(base_config, strategy="systematic", num_variants=5)
    for i, var in enumerate(variants, 1):
        print(f"{i}. {var['selection_method'][:10]} | "
              f"{var['crossover_method'][:15]} | "
              f"{var['mutation_method'][:10]}")

    print("\n🎲 Variantes Aleatórias:")
    variants = generator.generate(base_config, strategy="random", num_variants=5)
    for i, var in enumerate(variants, 1):
        print(f"{i}. {var['selection_method'][:10]} | "
              f"{var['crossover_method'][:15]} | "
              f"{var['mutation_method'][:10]}")

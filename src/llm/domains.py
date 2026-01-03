"""
Domínios completos de parâmetros para otimização do GA via LLM.
Define todos os espaços de busca válidos, priorizando variações algorítmicas.
"""
from enum import Enum
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass


@dataclass
class ParameterDomain:
    """Define o domínio de um parâmetro."""
    name: str
    type: str  # "enum", "int", "float"
    values: List[Any]  # Para enums, lista de valores válidos
    range: Tuple[Any, Any] = None  # Para numéricos, (min, max)
    default: Any = None
    priority: int = 1  # 1=HIGH (algoritmos), 2=MEDIUM (híbridos), 3=LOW (numéricos)
    description: str = ""


class GADomains:
    """Define todos os domínios de parâmetros do GA."""

    # ===== PRIORIDADE 1: ALGORITMOS FUNDAMENTAIS =====
    # Estes têm maior impacto no comportamento do GA

    SELECTION_METHODS = ParameterDomain(
        name="selection_method",
        type="enum",
        values=[
            "roulette_wheel",          # Seleção proporcional ao fitness
            "tournament",              # Torneio (k indivíduos)
            "rank",                    # Baseado em ranking
            "truncation",              # Seleciona top T%
            "elitist",                 # Preserva elite + base selector
            "stochastic_universal_sampling",  # SUS (baixa variância)
            "boltzmann",               # Temperatura adaptativa
            "steady_state"             # Substituição parcial
        ],
        default="tournament",
        priority=1,
        description="Método de seleção de pais para reprodução. Tournament é robusto, SUS tem menor variância."
    )

    CROSSOVER_METHODS = ParameterDomain(
        name="crossover_method",
        type="enum",
        values=[
            "partially_mapped_crossover",     # PMX - preserva posição/ordem parcial
            "order_crossover",                # OX - preserva ordem relativa
            "cycle_crossover",                # CX - preserva posições absolutas
            "alternating_edges_crossover",    # AEX - alterna arestas dos pais
            "edge_recombination_crossover",   # ERX - alta preservação de arestas
            "sequential_constructive_crossover",  # SCX - considera distâncias
            "order_based_crossover",          # OX2 - posições aleatórias
            "position_based_crossover",       # POS - preserva posições
            "arithmetic",                     # Aritmético (para velocidades)
            "hybrid"                          # Híbrido (rotas + velocidades)
        ],
        default="order_crossover",
        priority=1,
        description="Operador de recombinação. OX e PMX são clássicos. ERX preserva adjacências. Hybrid para codificação dupla."
    )

    MUTATION_METHODS = ParameterDomain(
        name="mutation_method",
        type="enum",
        values=[
            "swap",              # Troca 2 genes
            "inversion",         # Inverte segmento
            "scramble",          # Embaralha segmento
            "insert",            # Move gene
            "displacement",      # Move segmento
            "gaussian",          # Ruído gaussiano (para velocidades)
            "hybrid",            # Híbrido (rotas + velocidades)
            "2-opt",             # Melhoria local (remove cruzamentos)
            "3-opt",             # Melhoria local (3 arestas)
            "reverse_sequence"   # RSM - inverte sequência
        ],
        default="inversion",
        priority=1,
        description="Operador de mutação. Inversion e 2-opt são eficientes. Hybrid para codificação dupla."
    )

    REPLACEMENT_STRATEGIES = ParameterDomain(
        name="replacement_strategy",
        type="enum",
        values=[
            "generational",  # Substitui toda população
            "steady_state",  # Substitui poucos
            "elitist"        # Preserva elite (recomendado)
        ],
        default="elitist",
        priority=1,
        description="Estratégia de substituição geracional. Elitist garante monotonia."
    )

    FITNESS_TYPES = ParameterDomain(
        name="fitness_type",
        type="enum",
        values=[
            "distance_only",              # Apenas distância (TSP puro)
            "weighted_multi_objective",   # Soma ponderada (VRP completo)
            "penalty_based",              # Penalidades adaptativas
            "priority_aware"              # Foco em prioridades hospitalares
        ],
        default="weighted_multi_objective",
        priority=1,
        description="Função de fitness. weighted_multi para VRP com restrições."
    )

    # ===== PRIORIDADE 2: PARÂMETROS ALGORÍTMICOS SECUNDÁRIOS =====

    SCENARIOS = ParameterDomain(
        name="scenario",
        type="enum",
        values=["small", "medium", "large"],
        default="medium",
        priority=2,
        description="Tamanho do problema (10, 20 ou todos os hospitais)."
    )

    # ===== PRIORIDADE 3: PARÂMETROS NUMÉRICOS =====
    # Ajustes finos, menor impacto relativo

    POPULATION_SIZE = ParameterDomain(
        name="population_size",
        type="int",
        values=None,
        range=(50, 1000),
        default=100,
        priority=3,
        description="Tamanho da população. Maior = mais diversidade, mais custo."
    )

    MAX_GENERATIONS = ParameterDomain(
        name="max_generations",
        type="int",
        values=None,
        range=(50, 1000),
        default=500,
        priority=3,
        description="Máximo de gerações. Limite superior de iterações."
    )

    CROSSOVER_RATE = ParameterDomain(
        name="crossover_rate",
        type="float",
        values=None,
        range=(0.7, 1.0),
        default=0.9,
        priority=3,
        description="Taxa de crossover. Geralmente alta (0.8-0.95)."
    )

    MUTATION_RATE = ParameterDomain(
        name="mutation_rate",
        type="float",
        values=None,
        range=(0.01, 0.3),
        default=0.1,
        priority=3,
        description="Taxa de mutação. 0.05-0.15 é típico."
    )

    ELITE_SIZE = ParameterDomain(
        name="elite_size",
        type="int",
        values=None,
        range=(1, 20),
        default=5,
        priority=3,
        description="Número de indivíduos elite preservados."
    )

    TOURNAMENT_SIZE = ParameterDomain(
        name="tournament_size",
        type="int",
        values=None,
        range=(2, 10),
        default=3,
        priority=3,
        description="Tamanho do torneio (para selection_method=tournament)."
    )

    STAGNATION_LIMIT = ParameterDomain(
        name="stagnation_limit",
        type="int",
        values=None,
        range=(20, 200),
        default=50,
        priority=3,
        description="Gerações sem melhoria antes de parar."
    )

    HEURISTIC_INIT_RATIO = ParameterDomain(
        name="heuristic_init_ratio",
        type="float",
        values=None,
        range=(0.0, 0.5),
        default=0.2,
        priority=3,
        description="Fração da população inicializada com heurística nearest-neighbor."
    )

    TRUNCATION_THRESHOLD = ParameterDomain(
        name="truncation_threshold",
        type="float",
        values=None,
        range=(0.1, 0.8),
        default=0.5,
        priority=3,
        description="Fração da população truncada (para selection_method=truncation)."
    )

    BOLTZMANN_TEMPERATURE = ParameterDomain(
        name="boltzmann_temperature",
        type="float",
        values=None,
        range=(10.0, 200.0),
        default=100.0,
        priority=3,
        description="Temperatura inicial (para selection_method=boltzmann)."
    )

    STEADY_STATE_RATIO = ParameterDomain(
        name="steady_state_ratio",
        type="float",
        values=None,
        range=(0.1, 0.5),
        default=0.2,
        priority=3,
        description="Fração substituída por geração (para selection_method=steady_state)."
    )

    # ===== PARÂMETROS DE VEÍCULOS =====

    NUM_VEHICLES = ParameterDomain(
        name="num_vehicles",
        type="int",
        values=None,
        range=(2, 10),
        default=3,
        priority=3,
        description="Número de veículos disponíveis."
    )

    VEHICLE_CAPACITY = ParameterDomain(
        name="vehicle_capacity",
        type="int",
        values=None,
        range=(50, 200),
        default=100,
        priority=3,
        description="Capacidade de carga de cada veículo."
    )

    VEHICLE_SPEED = ParameterDomain(
        name="vehicle_speed",
        type="float",
        values=None,
        range=(30.0, 80.0),
        default=40.0,
        priority=3,
        description="Velocidade média dos veículos (km/h)."
    )

    VEHICLE_MAX_DISTANCE = ParameterDomain(
        name="vehicle_max_distance",
        type="float",
        values=None,
        range=(100.0, 500.0),
        default=200.0,
        priority=3,
        description="Autonomia máxima dos veículos (km)."
    )

    # ===== PESOS DE FITNESS (Multi-Objetivo) =====

    W_DISTANCE = ParameterDomain(
        name="w_distance",
        type="float",
        values=None,
        range=(0.5, 2.0),
        default=1.0,
        priority=3,
        description="Peso para distância total no fitness."
    )

    W_PRIORITY = ParameterDomain(
        name="w_priority",
        type="float",
        values=None,
        range=(0.0, 50.0),
        default=10.0,
        priority=3,
        description="Peso para penalidade de prioridade."
    )

    W_CAPACITY = ParameterDomain(
        name="w_capacity",
        type="float",
        values=None,
        range=(50.0, 500.0),
        default=100.0,
        priority=3,
        description="Penalidade para violação de capacidade."
    )

    W_AUTONOMY = ParameterDomain(
        name="w_autonomy",
        type="float",
        values=None,
        range=(50.0, 500.0),
        default=100.0,
        priority=3,
        description="Penalidade para violação de autonomia."
    )

    W_WINDOW = ParameterDomain(
        name="w_window",
        type="float",
        values=None,
        range=(0.0, 100.0),
        default=50.0,
        priority=3,
        description="Penalidade para violação de janelas de tempo."
    )

    @classmethod
    def get_all_domains(cls) -> Dict[str, ParameterDomain]:
        """Retorna todos os domínios como dicionário."""
        domains = {}
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, ParameterDomain):
                domains[attr.name] = attr
        return domains

    @classmethod
    def get_by_priority(cls, priority: int) -> Dict[str, ParameterDomain]:
        """Retorna domínios de uma prioridade específica."""
        all_domains = cls.get_all_domains()
        return {k: v for k, v in all_domains.items() if v.priority == priority}

    @classmethod
    def get_algorithmic_domains(cls) -> Dict[str, ParameterDomain]:
        """Retorna apenas domínios de algoritmos (enums de prioridade 1)."""
        all_domains = cls.get_all_domains()
        return {k: v for k, v in all_domains.items()
                if v.type == "enum" and v.priority == 1}

    @classmethod
    def validate_params(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """Valida e corrige parâmetros contra os domínios."""
        validated = {}
        all_domains = cls.get_all_domains()

        for key, value in params.items():
            if key not in all_domains:
                continue  # Ignora parâmetros desconhecidos

            domain = all_domains[key]

            if domain.type == "enum":
                if value in domain.values:
                    validated[key] = value
            elif domain.type == "int":
                min_val, max_val = domain.range
                validated[key] = max(min_val, min(max_val, int(value)))
            elif domain.type == "float":
                min_val, max_val = domain.range
                validated[key] = max(min_val, min(max_val, float(value)))

        return validated

    @classmethod
    def get_domain_description(cls) -> str:
        """Gera descrição textual de todos os domínios para o prompt LLM."""
        all_domains = sorted(cls.get_all_domains().values(),
                           key=lambda d: (d.priority, d.name))

        lines = []
        current_priority = None

        for domain in all_domains:
            if domain.priority != current_priority:
                current_priority = domain.priority
                priority_name = {1: "CRÍTICOS", 2: "IMPORTANTES", 3: "AJUSTES FINOS"}
                lines.append(f"\n=== PRIORIDADE {current_priority} - {priority_name.get(current_priority, 'OUTROS')} ===")

            if domain.type == "enum":
                values_str = ", ".join(f'"{v}"' for v in domain.values)
                lines.append(f"- {domain.name}: [{values_str}]")
            else:
                min_val, max_val = domain.range
                lines.append(f"- {domain.name}: {domain.type}({min_val}-{max_val})")

            lines.append(f"  → {domain.description}")

        return "\n".join(lines)


# Combinações recomendadas de algoritmos
ALGORITHM_COMBINATIONS = {
    "classic_tsp": {
        "selection_method": "tournament",
        "crossover_method": "order_crossover",
        "mutation_method": "inversion",
        "description": "Combinação clássica para TSP/VRP"
    },
    "edge_preserving": {
        "selection_method": "tournament",
        "crossover_method": "edge_recombination_crossover",
        "mutation_method": "2-opt",
        "description": "Foco em preservar arestas adjacentes"
    },
    "explorative": {
        "selection_method": "roulette_wheel",
        "crossover_method": "partially_mapped_crossover",
        "mutation_method": "scramble",
        "description": "Alta exploração do espaço de busca"
    },
    "exploitative": {
        "selection_method": "truncation",
        "crossover_method": "cycle_crossover",
        "mutation_method": "2-opt",
        "description": "Convergência rápida, exploitation"
    },
    "balanced": {
        "selection_method": "stochastic_universal_sampling",
        "crossover_method": "sequential_constructive_crossover",
        "mutation_method": "displacement",
        "description": "Balanceado entre exploração e exploitation"
    },
    "hybrid_coding": {
        "selection_method": "tournament",
        "crossover_method": "hybrid",
        "mutation_method": "hybrid",
        "description": "Para codificação híbrida (rotas + velocidades)"
    }
}

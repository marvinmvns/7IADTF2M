"""
Módulo de Operadores de Seleção
===============================

Este módulo implementa diversos métodos de seleção para algoritmos genéticos.
A seleção é responsável por escolher quais indivíduos serão usados como
pais para gerar a próxima geração.

Métodos Implementados:
---------------------
1. Roulette Wheel Selection (Seleção por Roleta)
2. Tournament Selection (Seleção por Torneio)
3. Rank Selection (Seleção por Ranking)
4. Truncation Selection (Seleção por Truncamento)
5. Elitist Selection (Seleção Elitista)
6. Stochastic Universal Sampling (SUS)
7. Boltzmann Selection (Seleção de Boltzmann)
8. Steady State Selection (Seleção Estado Estacionário)

Referências:
-----------
- Goldberg, D. E., & Deb, K. (1991). A comparative analysis of selection schemes.
- Blickle, T., & Thiele, L. (1996). A comparison of selection schemes used in EAs.
- Baker, J. E. (1987). Reducing bias and inefficiency in the selection algorithm.
"""

import random
import math
import numpy as np
from typing import List, Tuple, Optional
from abc import ABC, abstractmethod
from enum import Enum

from .chromosome import Chromosome


class SelectionMethod(Enum):
    """Enumeração dos métodos de seleção disponíveis."""
    ROULETTE_WHEEL = "roulette_wheel"
    TOURNAMENT = "tournament"
    RANK = "rank"
    TRUNCATION = "truncation"
    ELITIST = "elitist"
    SUS = "stochastic_universal_sampling"
    BOLTZMANN = "boltzmann"
    STEADY_STATE = "steady_state"


class SelectionOperator(ABC):
    """
    Classe base abstrata para operadores de seleção.
    
    Define a interface comum que todos os operadores de seleção
    devem implementar.
    """
    
    @abstractmethod
    def select(self, population: List[Chromosome], 
               num_parents: int) -> List[Chromosome]:
        """
        Seleciona indivíduos da população para reprodução.
        
        Args:
            population: Lista de cromossomos da população
            num_parents: Número de pais a selecionar
        
        Returns:
            Lista de cromossomos selecionados
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Retorna o nome do operador de seleção."""
        pass


class RouletteWheelSelection(SelectionOperator):
    """
    Seleção por Roleta (Roulette Wheel Selection).
    
    A probabilidade de seleção de cada indivíduo é proporcional ao
    seu fitness. Indivíduos mais aptos têm maior probabilidade de
    serem selecionados.
    
    Nota: Para problemas de minimização, o fitness é invertido.
    
    Vantagens:
    - Simples de implementar
    - Mantém pressão seletiva proporcional ao fitness
    
    Desvantagens:
    - Pode levar à convergência prematura se houver super-indivíduos
    - Sensível à escala do fitness
    """
    
    @property
    def name(self) -> str:
        return "Roulette Wheel Selection"
    
    def select(self, population: List[Chromosome], 
               num_parents: int) -> List[Chromosome]:
        """
        Seleciona pais usando o método da roleta.
        
        Args:
            population: Lista de cromossomos
            num_parents: Número de pais a selecionar
        
        Returns:
            Lista de cromossomos selecionados
        """
        if not population:
            return []
        
        # Inverte fitness para minimização (menor fitness = maior probabilidade)
        fitness_values = [c.fitness for c in population]
        max_fitness = max(fitness_values)
        
        # Converte para maximização
        inverted_fitness = [max_fitness - f + 1 for f in fitness_values]
        total_fitness = sum(inverted_fitness)
        
        # Calcula probabilidades
        probabilities = [f / total_fitness for f in inverted_fitness]
        
        # Seleciona pais
        selected = []
        for _ in range(num_parents):
            r = random.random()
            cumulative = 0
            for i, prob in enumerate(probabilities):
                cumulative += prob
                if r <= cumulative:
                    selected.append(population[i].copy())
                    break
        
        return selected


class TournamentSelection(SelectionOperator):
    """
    Seleção por Torneio (Tournament Selection).
    
    Seleciona k indivíduos aleatoriamente e escolhe o melhor entre eles.
    O parâmetro k (tamanho do torneio) controla a pressão seletiva.
    
    Parâmetros:
    - tournament_size: Número de indivíduos em cada torneio
    
    Vantagens:
    - Não é sensível à escala do fitness
    - Fácil de ajustar pressão seletiva
    - Eficiente computacionalmente
    
    Desvantagens:
    - Torneios muito grandes podem eliminar diversidade rapidamente
    """
    
    def __init__(self, tournament_size: int = 3):
        """
        Inicializa o operador de seleção por torneio.
        
        Args:
            tournament_size: Tamanho do torneio (padrão: 3)
        """
        self.tournament_size = tournament_size
    
    @property
    def name(self) -> str:
        return f"Tournament Selection (k={self.tournament_size})"
    
    def select(self, population: List[Chromosome], 
               num_parents: int) -> List[Chromosome]:
        """
        Seleciona pais usando torneios.
        
        Args:
            population: Lista de cromossomos
            num_parents: Número de pais a selecionar
        
        Returns:
            Lista de cromossomos selecionados
        """
        selected = []
        
        for _ in range(num_parents):
            # Seleciona participantes do torneio
            tournament_size = min(self.tournament_size, len(population))
            tournament = random.sample(population, tournament_size)
            
            # Escolhe o vencedor (menor fitness para minimização)
            winner = min(tournament, key=lambda c: c.fitness)
            selected.append(winner.copy())
        
        return selected


class RankSelection(SelectionOperator):
    """
    Seleção por Ranking (Rank Selection).
    
    Os indivíduos são ordenados por fitness e a probabilidade de
    seleção é baseada no ranking, não no valor absoluto do fitness.
    
    Vantagens:
    - Evita dominância de super-indivíduos
    - Mantém pressão seletiva constante
    - Não é sensível à escala do fitness
    
    Desvantagens:
    - Pode ser mais lento que outros métodos
    - Perde informação sobre a magnitude das diferenças de fitness
    """
    
    def __init__(self, selection_pressure: float = 2.0):
        """
        Inicializa o operador de seleção por ranking.
        
        Args:
            selection_pressure: Pressão seletiva (1.0 a 2.0)
        """
        self.selection_pressure = max(1.0, min(2.0, selection_pressure))
    
    @property
    def name(self) -> str:
        return f"Rank Selection (SP={self.selection_pressure})"
    
    def select(self, population: List[Chromosome], 
               num_parents: int) -> List[Chromosome]:
        """
        Seleciona pais baseado no ranking.
        
        Args:
            population: Lista de cromossomos
            num_parents: Número de pais a selecionar
        
        Returns:
            Lista de cromossomos selecionados
        """
        n = len(population)
        if n == 0:
            return []
        
        # Ordena por fitness (menor primeiro)
        sorted_pop = sorted(population, key=lambda c: c.fitness)
        
        # Calcula probabilidades baseadas no ranking
        # Ranking linear: P(i) = (2-s)/n + 2*i*(s-1)/(n*(n-1))
        s = self.selection_pressure
        probabilities = []
        for i in range(n):
            rank = n - i  # Melhor indivíduo tem maior rank
            prob = (2 - s) / n + 2 * (rank - 1) * (s - 1) / (n * (n - 1))
            probabilities.append(prob)
        
        # Normaliza probabilidades
        total = sum(probabilities)
        probabilities = [p / total for p in probabilities]
        
        # Seleciona usando roleta com probabilidades de ranking
        selected = []
        for _ in range(num_parents):
            r = random.random()
            cumulative = 0
            for i, prob in enumerate(probabilities):
                cumulative += prob
                if r <= cumulative:
                    selected.append(sorted_pop[i].copy())
                    break
        
        return selected


class TruncationSelection(SelectionOperator):
    """
    Seleção por Truncamento (Truncation Selection).
    
    Seleciona apenas os melhores T% da população para reprodução.
    Método simples e com alta pressão seletiva.
    
    Parâmetros:
    - truncation_threshold: Fração da população a considerar (0 a 1)
    
    Vantagens:
    - Muito simples de implementar
    - Alta pressão seletiva
    - Eficiente computacionalmente
    
    Desvantagens:
    - Pode perder diversidade rapidamente
    - Não considera diferenças de fitness entre os selecionados
    """
    
    def __init__(self, truncation_threshold: float = 0.5):
        """
        Inicializa o operador de seleção por truncamento.
        
        Args:
            truncation_threshold: Fração da população a considerar
        """
        self.truncation_threshold = max(0.1, min(1.0, truncation_threshold))
    
    @property
    def name(self) -> str:
        return f"Truncation Selection (T={self.truncation_threshold})"
    
    def select(self, population: List[Chromosome], 
               num_parents: int) -> List[Chromosome]:
        """
        Seleciona pais dos melhores T% da população.
        
        Args:
            population: Lista de cromossomos
            num_parents: Número de pais a selecionar
        
        Returns:
            Lista de cromossomos selecionados
        """
        # Ordena por fitness
        sorted_pop = sorted(population, key=lambda c: c.fitness)
        
        # Determina ponto de truncamento
        cutoff = max(1, int(len(sorted_pop) * self.truncation_threshold))
        eligible = sorted_pop[:cutoff]
        
        # Seleciona aleatoriamente dos elegíveis
        selected = [random.choice(eligible).copy() for _ in range(num_parents)]
        
        return selected


class ElitistSelection(SelectionOperator):
    """
    Seleção Elitista (Elitist Selection).
    
    Garante que os melhores indivíduos passem diretamente para a
    próxima geração, enquanto o restante é selecionado por outro método.
    
    Parâmetros:
    - elite_size: Número de indivíduos elite a preservar
    - base_selector: Método de seleção para os não-elite
    
    Vantagens:
    - Garante que a melhor solução nunca seja perdida
    - Acelera convergência
    
    Desvantagens:
    - Pode reduzir diversidade
    - Elite muito grande pode dominar a população
    """
    
    def __init__(self, elite_size: int = 2, 
                 base_selector: Optional[SelectionOperator] = None):
        """
        Inicializa o operador de seleção elitista.
        
        Args:
            elite_size: Número de indivíduos elite
            base_selector: Seletor para não-elite (padrão: Torneio)
        """
        self.elite_size = elite_size
        self.base_selector = base_selector or TournamentSelection()
    
    @property
    def name(self) -> str:
        return f"Elitist Selection (elite={self.elite_size})"
    
    def select(self, population: List[Chromosome], 
               num_parents: int) -> List[Chromosome]:
        """
        Seleciona pais com elitismo.
        
        Args:
            population: Lista de cromossomos
            num_parents: Número de pais a selecionar
        
        Returns:
            Lista de cromossomos selecionados
        """
        # Ordena por fitness
        sorted_pop = sorted(population, key=lambda c: c.fitness)
        
        # Seleciona elite
        elite = [c.copy() for c in sorted_pop[:self.elite_size]]
        
        # Seleciona restante usando método base
        remaining = num_parents - len(elite)
        if remaining > 0:
            others = self.base_selector.select(population, remaining)
            elite.extend(others)
        
        return elite[:num_parents]


class StochasticUniversalSampling(SelectionOperator):
    """
    Amostragem Universal Estocástica (Stochastic Universal Sampling - SUS).
    
    Variante da seleção por roleta que usa múltiplos ponteiros
    igualmente espaçados, reduzindo a variância na seleção.
    
    Vantagens:
    - Menor variância que roleta simples
    - Seleção mais justa
    - Zero bias
    
    Desvantagens:
    - Ainda sensível à escala do fitness
    """
    
    @property
    def name(self) -> str:
        return "Stochastic Universal Sampling (SUS)"
    
    def select(self, population: List[Chromosome], 
               num_parents: int) -> List[Chromosome]:
        """
        Seleciona pais usando SUS.
        
        Args:
            population: Lista de cromossomos
            num_parents: Número de pais a selecionar
        
        Returns:
            Lista de cromossomos selecionados
        """
        if not population:
            return []
        
        # Inverte fitness para minimização
        fitness_values = [c.fitness for c in population]
        max_fitness = max(fitness_values)
        inverted_fitness = [max_fitness - f + 1 for f in fitness_values]
        total_fitness = sum(inverted_fitness)
        
        # Calcula distância entre ponteiros
        pointer_distance = total_fitness / num_parents
        
        # Ponto de partida aleatório
        start = random.uniform(0, pointer_distance)
        
        # Seleciona usando múltiplos ponteiros
        selected = []
        cumulative = 0
        current_pointer = start
        
        for i, fitness in enumerate(inverted_fitness):
            cumulative += fitness
            while current_pointer <= cumulative and len(selected) < num_parents:
                selected.append(population[i].copy())
                current_pointer += pointer_distance
        
        # Completa se necessário
        while len(selected) < num_parents:
            selected.append(random.choice(population).copy())
        
        return selected


class BoltzmannSelection(SelectionOperator):
    """
    Seleção de Boltzmann (Boltzmann Selection).
    
    Inspirada em simulated annealing, usa uma temperatura que
    controla a pressão seletiva. Alta temperatura favorece
    exploração, baixa temperatura favorece exploitation.
    
    Parâmetros:
    - initial_temperature: Temperatura inicial
    - cooling_rate: Taxa de resfriamento
    
    Vantagens:
    - Controle dinâmico da pressão seletiva
    - Evita convergência prematura no início
    
    Desvantagens:
    - Requer ajuste de parâmetros de temperatura
    """
    
    def __init__(self, initial_temperature: float = 100.0,
                 cooling_rate: float = 0.95):
        """
        Inicializa o operador de seleção de Boltzmann.
        
        Args:
            initial_temperature: Temperatura inicial
            cooling_rate: Taxa de resfriamento por geração
        """
        self.temperature = initial_temperature
        self.initial_temperature = initial_temperature
        self.cooling_rate = cooling_rate
    
    @property
    def name(self) -> str:
        return f"Boltzmann Selection (T={self.temperature:.1f})"
    
    def select(self, population: List[Chromosome], 
               num_parents: int) -> List[Chromosome]:
        """
        Seleciona pais usando distribuição de Boltzmann.
        
        Args:
            population: Lista de cromossomos
            num_parents: Número de pais a selecionar
        
        Returns:
            Lista de cromossomos selecionados
        """
        if not population:
            return []
        
        # Calcula probabilidades de Boltzmann
        # P(i) = exp(-f(i)/T) / sum(exp(-f(j)/T))
        fitness_values = [c.fitness for c in population]
        min_fitness = min(fitness_values)
        
        # Normaliza para evitar overflow
        normalized = [f - min_fitness for f in fitness_values]
        
        # Calcula exponenciais
        exp_values = [math.exp(-f / max(self.temperature, 0.01)) 
                      for f in normalized]
        total = sum(exp_values)
        
        probabilities = [e / total for e in exp_values]
        
        # Seleciona usando as probabilidades
        selected = []
        for _ in range(num_parents):
            r = random.random()
            cumulative = 0
            for i, prob in enumerate(probabilities):
                cumulative += prob
                if r <= cumulative:
                    selected.append(population[i].copy())
                    break
        
        return selected
    
    def cool_down(self):
        """Reduz a temperatura (chamado a cada geração)."""
        self.temperature *= self.cooling_rate
    
    def reset_temperature(self):
        """Reseta a temperatura para o valor inicial."""
        self.temperature = self.initial_temperature


class SteadyStateSelection(SelectionOperator):
    """
    Seleção Estado Estacionário (Steady State Selection).
    
    Apenas uma pequena fração da população é substituída a cada
    geração, mantendo a maior parte da população estável.
    
    Parâmetros:
    - replacement_rate: Fração da população a substituir
    
    Vantagens:
    - Convergência mais suave
    - Mantém diversidade por mais tempo
    
    Desvantagens:
    - Convergência mais lenta
    """
    
    def __init__(self, replacement_rate: float = 0.2):
        """
        Inicializa o operador de seleção estado estacionário.
        
        Args:
            replacement_rate: Fração da população a substituir
        """
        self.replacement_rate = max(0.1, min(0.5, replacement_rate))
    
    @property
    def name(self) -> str:
        return f"Steady State Selection (rate={self.replacement_rate})"
    
    def select(self, population: List[Chromosome], 
               num_parents: int) -> List[Chromosome]:
        """
        Seleciona pais para substituição parcial.
        
        Args:
            population: Lista de cromossomos
            num_parents: Número de pais a selecionar
        
        Returns:
            Lista de cromossomos selecionados
        """
        # Número de indivíduos a substituir
        num_replace = max(2, int(len(population) * self.replacement_rate))
        
        # Seleciona pais usando torneio
        tournament = TournamentSelection(tournament_size=3)
        parents = tournament.select(population, min(num_parents, num_replace * 2))
        
        return parents


def create_selector(method: SelectionMethod, **kwargs) -> SelectionOperator:
    """
    Factory function para criar operadores de seleção.
    
    Args:
        method: Método de seleção desejado
        **kwargs: Parâmetros específicos do método
    
    Returns:
        Instância do operador de seleção
    
    Raises:
        ValueError: Se o método não for reconhecido
    """
    selectors = {
        SelectionMethod.ROULETTE_WHEEL: RouletteWheelSelection,
        SelectionMethod.TOURNAMENT: TournamentSelection,
        SelectionMethod.RANK: RankSelection,
        SelectionMethod.TRUNCATION: TruncationSelection,
        SelectionMethod.ELITIST: ElitistSelection,
        SelectionMethod.SUS: StochasticUniversalSampling,
        SelectionMethod.BOLTZMANN: BoltzmannSelection,
        SelectionMethod.STEADY_STATE: SteadyStateSelection,
    }
    
    if method not in selectors:
        raise ValueError(f"Método de seleção desconhecido: {method}")
    
    return selectors[method](**kwargs)

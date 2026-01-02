"""
Módulo de Operadores de Mutação
===============================

Este módulo implementa diversos operadores de mutação especializados
para problemas de permutação como o TSP (Travelling Salesman Problem).

Operadores Implementados:
------------------------
1. Swap Mutation - Troca dois genes de posição
2. Inversion Mutation - Inverte um segmento
3. Scramble Mutation - Embaralha um segmento
4. Insert Mutation - Move um gene para outra posição
5. Displacement Mutation - Move um segmento para outra posição
6. 2-opt Mutation - Remove e reconecta duas arestas
7. 3-opt Mutation - Remove e reconecta três arestas
8. Reverse Sequence Mutation (RSM) - Inverte sequência

Referências:
-----------
- Syswerda, G. (1991). Schedule optimization using genetic algorithms.
- Lin, S. (1965). Computer solutions of the traveling salesman problem.
- Croes, G. A. (1958). A method for solving traveling-salesman problems.
"""

import random
from typing import List, Tuple, Optional
from abc import ABC, abstractmethod
from enum import Enum

from .chromosome import Chromosome


class MutationMethod(Enum):
    """Enumeração dos métodos de mutação disponíveis."""
    SWAP = "swap"
    INVERSION = "inversion"
    SCRAMBLE = "scramble"
    INSERT = "insert"
    DISPLACEMENT = "displacement"
    TWO_OPT = "2-opt"
    THREE_OPT = "3-opt"
    RSM = "reverse_sequence"


class MutationOperator(ABC):
    """
    Classe base abstrata para operadores de mutação.
    
    Define a interface comum que todos os operadores de mutação
    devem implementar.
    """
    
    def __init__(self, mutation_rate: float = 0.1):
        """
        Inicializa o operador de mutação.
        
        Args:
            mutation_rate: Probabilidade de aplicar mutação (0 a 1)
        """
        self.mutation_rate = mutation_rate
    
    @abstractmethod
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        """
        Aplica mutação a um cromossomo.
        
        Args:
            chromosome: Cromossomo a ser mutado
        
        Returns:
            Cromossomo mutado (pode ser o mesmo ou uma cópia)
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Retorna o nome do operador de mutação."""
        pass
    
    def should_mutate(self) -> bool:
        """Determina se a mutação deve ser aplicada."""
        return random.random() < self.mutation_rate


class SwapMutation(MutationOperator):
    """
    Mutação por Troca (Swap Mutation).
    
    Seleciona duas posições aleatórias e troca os genes entre elas.
    É o operador de mutação mais simples para permutações.
    
    Funcionamento:
    1. Seleciona duas posições i e j aleatoriamente
    2. Troca genes[i] com genes[j]
    
    Características:
    - Simples e rápido
    - Alteração mínima na estrutura
    - Preserva a maior parte das adjacências
    
    Exemplo:
        Antes:  [1, 2, 3, 4, 5]
        Após:   [1, 4, 3, 2, 5]  (trocou posições 1 e 3)
    """
    
    @property
    def name(self) -> str:
        return "Swap Mutation"
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        """
        Aplica mutação por troca.
        
        Args:
            chromosome: Cromossomo a ser mutado
        
        Returns:
            Cromossomo mutado
        """
        if not self.should_mutate():
            return chromosome
        
        mutated = chromosome.copy()
        size = len(mutated.genes)
        
        if size < 2:
            return mutated
        
        # Seleciona duas posições diferentes
        i, j = random.sample(range(size), 2)
        
        # Troca os genes
        mutated.genes[i], mutated.genes[j] = mutated.genes[j], mutated.genes[i]
        mutated.invalidate_cache()
        
        return mutated


class InversionMutation(MutationOperator):
    """
    Mutação por Inversão (Inversion Mutation).
    
    Seleciona um segmento do cromossomo e inverte a ordem dos genes
    dentro desse segmento.
    
    Funcionamento:
    1. Seleciona dois pontos de corte i e j
    2. Inverte a sequência de genes entre i e j
    
    Características:
    - Preserva adjacências nas bordas do segmento
    - Pode fazer grandes alterações na estrutura
    - Equivalente a uma operação 2-opt
    
    Exemplo:
        Antes:  [1, 2, 3, 4, 5, 6]
        Após:   [1, 5, 4, 3, 2, 6]  (inverteu de 1 a 4)
    """
    
    @property
    def name(self) -> str:
        return "Inversion Mutation"
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        """
        Aplica mutação por inversão.
        
        Args:
            chromosome: Cromossomo a ser mutado
        
        Returns:
            Cromossomo mutado
        """
        if not self.should_mutate():
            return chromosome
        
        mutated = chromosome.copy()
        size = len(mutated.genes)
        
        if size < 2:
            return mutated
        
        # Seleciona pontos de corte
        i, j = sorted(random.sample(range(size), 2))
        
        # Inverte o segmento
        mutated.genes[i:j+1] = mutated.genes[i:j+1][::-1]
        mutated.invalidate_cache()
        
        return mutated


class ScrambleMutation(MutationOperator):
    """
    Mutação por Embaralhamento (Scramble Mutation).
    
    Seleciona um segmento do cromossomo e embaralha aleatoriamente
    os genes dentro desse segmento.
    
    Funcionamento:
    1. Seleciona dois pontos de corte i e j
    2. Embaralha aleatoriamente os genes entre i e j
    
    Características:
    - Alta perturbação local
    - Preserva genes fora do segmento
    - Útil para escapar de ótimos locais
    
    Exemplo:
        Antes:  [1, 2, 3, 4, 5, 6]
        Após:   [1, 4, 2, 5, 3, 6]  (embaralhou de 1 a 4)
    """
    
    @property
    def name(self) -> str:
        return "Scramble Mutation"
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        """
        Aplica mutação por embaralhamento.
        
        Args:
            chromosome: Cromossomo a ser mutado
        
        Returns:
            Cromossomo mutado
        """
        if not self.should_mutate():
            return chromosome
        
        mutated = chromosome.copy()
        size = len(mutated.genes)
        
        if size < 2:
            return mutated
        
        # Seleciona pontos de corte
        i, j = sorted(random.sample(range(size), 2))
        
        # Extrai e embaralha o segmento
        segment = mutated.genes[i:j+1]
        random.shuffle(segment)
        mutated.genes[i:j+1] = segment
        mutated.invalidate_cache()
        
        return mutated


class InsertMutation(MutationOperator):
    """
    Mutação por Inserção (Insert Mutation).
    
    Remove um gene de sua posição e o insere em outra posição,
    deslocando os genes intermediários.
    
    Funcionamento:
    1. Seleciona uma posição i (gene a mover)
    2. Seleciona uma posição j (destino)
    3. Remove gene de i e insere em j
    
    Características:
    - Altera a ordem relativa de alguns genes
    - Preserva mais estrutura que scramble
    - Movimento mais controlado
    
    Exemplo:
        Antes:  [1, 2, 3, 4, 5]
        Após:   [1, 3, 4, 2, 5]  (moveu 2 para depois de 4)
    """
    
    @property
    def name(self) -> str:
        return "Insert Mutation"
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        """
        Aplica mutação por inserção.
        
        Args:
            chromosome: Cromossomo a ser mutado
        
        Returns:
            Cromossomo mutado
        """
        if not self.should_mutate():
            return chromosome
        
        mutated = chromosome.copy()
        size = len(mutated.genes)
        
        if size < 2:
            return mutated
        
        # Seleciona posição de origem e destino
        i = random.randint(0, size - 1)
        j = random.randint(0, size - 1)
        
        if i == j:
            return mutated
        
        # Remove gene da posição i
        gene = mutated.genes.pop(i)
        
        # Insere na posição j
        mutated.genes.insert(j, gene)
        mutated.invalidate_cache()
        
        return mutated


class DisplacementMutation(MutationOperator):
    """
    Mutação por Deslocamento (Displacement Mutation).
    
    Remove um segmento do cromossomo e o insere em outra posição.
    É uma generalização da mutação por inserção.
    
    Funcionamento:
    1. Seleciona um segmento [i, j]
    2. Remove o segmento
    3. Insere em uma nova posição k
    
    Características:
    - Move blocos inteiros de genes
    - Preserva adjacências dentro do bloco
    - Pode causar grandes mudanças estruturais
    
    Exemplo:
        Antes:  [1, 2, 3, 4, 5, 6]
        Após:   [1, 5, 2, 3, 4, 6]  (moveu [2,3,4] para depois de 5)
    """
    
    @property
    def name(self) -> str:
        return "Displacement Mutation"
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        """
        Aplica mutação por deslocamento.
        
        Args:
            chromosome: Cromossomo a ser mutado
        
        Returns:
            Cromossomo mutado
        """
        if not self.should_mutate():
            return chromosome
        
        mutated = chromosome.copy()
        size = len(mutated.genes)
        
        if size < 3:
            return mutated
        
        # Seleciona segmento
        i, j = sorted(random.sample(range(size), 2))
        segment = mutated.genes[i:j+1]
        
        # Remove segmento
        del mutated.genes[i:j+1]
        
        # Seleciona nova posição
        new_size = len(mutated.genes)
        k = random.randint(0, new_size)
        
        # Insere segmento na nova posição
        mutated.genes[k:k] = segment
        mutated.invalidate_cache()
        
        return mutated


class TwoOptMutation(MutationOperator):
    """
    Mutação 2-opt.
    
    Remove duas arestas não adjacentes e reconecta os segmentos
    de forma diferente. É uma técnica clássica de melhoria local
    para o TSP.
    
    Funcionamento:
    1. Seleciona duas arestas (i, i+1) e (j, j+1)
    2. Remove as arestas
    3. Reconecta invertendo o segmento entre i+1 e j
    
    Características:
    - Operador de melhoria local muito eficiente
    - Preserva a estrutura geral da rota
    - Pode ser aplicado repetidamente para refinamento
    
    Exemplo:
        Rota: A-B-C-D-E-F-A
        Remove: (B,C) e (E,F)
        Resultado: A-B-E-D-C-F-A
    """
    
    @property
    def name(self) -> str:
        return "2-opt Mutation"
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        """
        Aplica mutação 2-opt.
        
        Args:
            chromosome: Cromossomo a ser mutado
        
        Returns:
            Cromossomo mutado
        """
        if not self.should_mutate():
            return chromosome
        
        mutated = chromosome.copy()
        size = len(mutated.genes)
        
        if size < 4:
            return mutated
        
        # Seleciona duas posições para o 2-opt
        i = random.randint(0, size - 3)
        j = random.randint(i + 2, size - 1)
        
        # Aplica 2-opt (inverte o segmento entre i+1 e j)
        mutated.genes[i+1:j+1] = mutated.genes[i+1:j+1][::-1]
        mutated.invalidate_cache()
        
        return mutated
    
    def apply_best_2opt(self, chromosome: Chromosome) -> Chromosome:
        """
        Aplica o melhor movimento 2-opt possível.
        
        Testa todos os movimentos 2-opt e aplica o que resulta
        na maior melhoria de fitness.
        
        Args:
            chromosome: Cromossomo a ser melhorado
        
        Returns:
            Cromossomo com o melhor 2-opt aplicado
        """
        best = chromosome.copy()
        best_distance = self._calculate_route_distance(best)
        improved = True
        
        while improved:
            improved = False
            size = len(best.genes)
            
            for i in range(size - 2):
                for j in range(i + 2, size):
                    # Cria candidato com 2-opt
                    candidate = best.copy()
                    candidate.genes[i+1:j+1] = candidate.genes[i+1:j+1][::-1]
                    
                    distance = self._calculate_route_distance(candidate)
                    
                    if distance < best_distance:
                        best = candidate
                        best_distance = distance
                        improved = True
                        break
                
                if improved:
                    break
        
        best.invalidate_cache()
        return best
    
    def _calculate_route_distance(self, chromosome: Chromosome) -> float:
        """Calcula a distância total da rota."""
        if not chromosome.delivery_points:
            return float('inf')
        
        points = chromosome.delivery_points
        depot = points[chromosome.depot_index]
        genes = chromosome.genes
        
        # Distância do depósito ao primeiro ponto
        distance = depot.distance_to(points[genes[0]])
        
        # Distância entre pontos consecutivos
        for i in range(len(genes) - 1):
            distance += points[genes[i]].distance_to(points[genes[i + 1]])
        
        # Distância do último ponto ao depósito
        distance += points[genes[-1]].distance_to(depot)
        
        return distance


class ThreeOptMutation(MutationOperator):
    """
    Mutação 3-opt.
    
    Remove três arestas e reconecta os segmentos de forma otimizada.
    É mais poderoso que 2-opt mas também mais custoso computacionalmente.
    
    Funcionamento:
    1. Seleciona três arestas não adjacentes
    2. Remove as arestas
    3. Reconecta os quatro segmentos de uma das formas possíveis
    
    Características:
    - Pode encontrar melhorias que 2-opt não consegue
    - Mais custoso computacionalmente
    - Útil para refinamento final
    """
    
    @property
    def name(self) -> str:
        return "3-opt Mutation"
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        """
        Aplica mutação 3-opt.
        
        Args:
            chromosome: Cromossomo a ser mutado
        
        Returns:
            Cromossomo mutado
        """
        if not self.should_mutate():
            return chromosome
        
        mutated = chromosome.copy()
        size = len(mutated.genes)
        
        if size < 6:
            return mutated
        
        # Seleciona três posições para o 3-opt
        positions = sorted(random.sample(range(size), 3))
        i, j, k = positions
        
        # Aplica uma das reconexões 3-opt aleatoriamente
        # Existem 8 formas de reconectar, escolhemos uma aleatória
        reconnection = random.randint(0, 3)
        
        segment1 = mutated.genes[:i+1]
        segment2 = mutated.genes[i+1:j+1]
        segment3 = mutated.genes[j+1:k+1]
        segment4 = mutated.genes[k+1:]
        
        if reconnection == 0:
            # Inverte segmento 2
            mutated.genes = segment1 + segment2[::-1] + segment3 + segment4
        elif reconnection == 1:
            # Inverte segmento 3
            mutated.genes = segment1 + segment2 + segment3[::-1] + segment4
        elif reconnection == 2:
            # Inverte segmentos 2 e 3
            mutated.genes = segment1 + segment2[::-1] + segment3[::-1] + segment4
        else:
            # Troca segmentos 2 e 3
            mutated.genes = segment1 + segment3 + segment2 + segment4
        
        mutated.invalidate_cache()
        return mutated


class ReverseSequenceMutation(MutationOperator):
    """
    Mutação por Reversão de Sequência (Reverse Sequence Mutation - RSM).
    
    Similar à mutação por inversão, mas com seleção de segmento
    baseada em tamanho aleatório.
    
    Funcionamento:
    1. Seleciona um ponto de início aleatório
    2. Seleciona um tamanho de segmento aleatório
    3. Inverte o segmento
    
    Características:
    - Variante da inversão com controle de tamanho
    - Pode ser configurado para segmentos menores ou maiores
    """
    
    def __init__(self, mutation_rate: float = 0.1,
                 min_segment_ratio: float = 0.1,
                 max_segment_ratio: float = 0.5):
        """
        Inicializa o operador RSM.
        
        Args:
            mutation_rate: Taxa de mutação
            min_segment_ratio: Tamanho mínimo do segmento (fração do cromossomo)
            max_segment_ratio: Tamanho máximo do segmento (fração do cromossomo)
        """
        super().__init__(mutation_rate)
        self.min_segment_ratio = min_segment_ratio
        self.max_segment_ratio = max_segment_ratio
    
    @property
    def name(self) -> str:
        return "RSM (Reverse Sequence Mutation)"
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        """
        Aplica mutação RSM.
        
        Args:
            chromosome: Cromossomo a ser mutado
        
        Returns:
            Cromossomo mutado
        """
        if not self.should_mutate():
            return chromosome
        
        mutated = chromosome.copy()
        size = len(mutated.genes)
        
        if size < 2:
            return mutated
        
        # Calcula tamanho do segmento
        min_size = max(2, int(size * self.min_segment_ratio))
        max_size = max(min_size, int(size * self.max_segment_ratio))
        segment_size = random.randint(min_size, max_size)
        
        # Seleciona ponto de início
        start = random.randint(0, size - segment_size)
        end = start + segment_size
        
        # Inverte o segmento
        mutated.genes[start:end] = mutated.genes[start:end][::-1]
        mutated.invalidate_cache()
        
        return mutated


class CompositeMutation(MutationOperator):
    """
    Mutação Composta.
    
    Combina múltiplos operadores de mutação, aplicando-os
    sequencialmente ou escolhendo um aleatoriamente.
    
    Características:
    - Flexível e configurável
    - Pode combinar diferentes estratégias
    - Útil para exploração diversificada
    """
    
    def __init__(self, operators: List[MutationOperator],
                 mutation_rate: float = 0.1,
                 sequential: bool = False):
        """
        Inicializa a mutação composta.
        
        Args:
            operators: Lista de operadores de mutação
            mutation_rate: Taxa de mutação geral
            sequential: Se True, aplica todos; se False, escolhe um
        """
        super().__init__(mutation_rate)
        self.operators = operators
        self.sequential = sequential
    
    @property
    def name(self) -> str:
        op_names = [op.name for op in self.operators]
        mode = "Sequential" if self.sequential else "Random"
        return f"Composite Mutation ({mode}: {', '.join(op_names)})"
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        """
        Aplica mutação composta.
        
        Args:
            chromosome: Cromossomo a ser mutado
        
        Returns:
            Cromossomo mutado
        """
        if not self.should_mutate():
            return chromosome
        
        mutated = chromosome.copy()
        
        if self.sequential:
            # Aplica todos os operadores em sequência
            for operator in self.operators:
                # Força a mutação (ignora taxa individual)
                temp_rate = operator.mutation_rate
                operator.mutation_rate = 1.0
                mutated = operator.mutate(mutated)
                operator.mutation_rate = temp_rate
        else:
            # Escolhe um operador aleatoriamente
            operator = random.choice(self.operators)
            temp_rate = operator.mutation_rate
            operator.mutation_rate = 1.0
            mutated = operator.mutate(mutated)
            operator.mutation_rate = temp_rate
        
        return mutated


def create_mutation(method: MutationMethod, 
                    mutation_rate: float = 0.1,
                    **kwargs) -> MutationOperator:
    """
    Factory function para criar operadores de mutação.
    
    Args:
        method: Método de mutação desejado
        mutation_rate: Taxa de mutação
        **kwargs: Parâmetros específicos do método
    
    Returns:
        Instância do operador de mutação
    
    Raises:
        ValueError: Se o método não for reconhecido
    """
    mutations = {
        MutationMethod.SWAP: SwapMutation,
        MutationMethod.INVERSION: InversionMutation,
        MutationMethod.SCRAMBLE: ScrambleMutation,
        MutationMethod.INSERT: InsertMutation,
        MutationMethod.DISPLACEMENT: DisplacementMutation,
        MutationMethod.TWO_OPT: TwoOptMutation,
        MutationMethod.THREE_OPT: ThreeOptMutation,
        MutationMethod.RSM: ReverseSequenceMutation,
    }
    
    if method not in mutations:
        raise ValueError(f"Método de mutação desconhecido: {method}")
    
    return mutations[method](mutation_rate=mutation_rate, **kwargs)

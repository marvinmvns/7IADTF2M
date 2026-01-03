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
    GAUSSIAN = "gaussian"
    HYBRID = "hybrid"
    TWO_OPT = "2-opt"
    THREE_OPT = "3-opt"
    REVERSE_SEQUENCE = "reverse_sequence"


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
    
    Exemplo:
        Antes:  [1, 2, 3, 4, 5]
        Após:   [1, 4, 3, 2, 5]  (trocou posições 1 e 3)
    """
    
    @property
    def name(self) -> str:
        return "Swap Mutation"
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        if not self.should_mutate():
            return chromosome
        
        mutated = chromosome.copy()
        size = len(mutated.genes)
        
        if size < 2:
            return mutated
        
        i, j = random.sample(range(size), 2)
        mutated.genes[i], mutated.genes[j] = mutated.genes[j], mutated.genes[i]
        mutated.invalidate_cache()
        
        return mutated


class InversionMutation(MutationOperator):
    """
    Mutação por Inversão (Inversion Mutation).
    
    Seleciona um segmento do cromossomo e inverte a ordem dos genes.
    
    Exemplo:
        Antes:  [1, 2, 3, 4, 5, 6]
        Após:   [1, 5, 4, 3, 2, 6]  (inverteu de 1 a 4)
    """
    
    @property
    def name(self) -> str:
        return "Inversion Mutation"
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        if not self.should_mutate():
            return chromosome
        
        mutated = chromosome.copy()
        size = len(mutated.genes)
        
        if size < 2:
            return mutated
        
        i, j = sorted(random.sample(range(size), 2))
        mutated.genes[i:j+1] = mutated.genes[i:j+1][::-1]
        mutated.invalidate_cache()
        
        return mutated


class ScrambleMutation(MutationOperator):
    """
    Mutação por Embaralhamento (Scramble Mutation).
    
    Seleciona um segmento do cromossomo e embaralha aleatoriamente.
    
    Exemplo:
        Antes:  [1, 2, 3, 4, 5, 6]
        Após:   [1, 4, 2, 5, 3, 6]  (embaralhou de 1 a 4)
    """
    
    @property
    def name(self) -> str:
        return "Scramble Mutation"
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        if not self.should_mutate():
            return chromosome
        
        mutated = chromosome.copy()
        size = len(mutated.genes)
        
        if size < 2:
            return mutated
        
        i, j = sorted(random.sample(range(size), 2))
        segment = mutated.genes[i:j+1]
        random.shuffle(segment)
        mutated.genes[i:j+1] = segment
        mutated.invalidate_cache()
        
        return mutated


class InsertMutation(MutationOperator):
    """
    Mutação por Inserção (Insert Mutation).
    
    Remove um gene de sua posição e o insere em outra.
    
    Exemplo:
        Antes:  [1, 2, 3, 4, 5]
        Após:   [1, 3, 4, 2, 5]  (moveu 2 para depois de 4)
    """
    
    @property
    def name(self) -> str:
        return "Insert Mutation"
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        if not self.should_mutate():
            return chromosome
        
        mutated = chromosome.copy()
        size = len(mutated.genes)
        
        if size < 2:
            return mutated
        
        i = random.randint(0, size - 1)
        j = random.randint(0, size - 1)
        
        if i == j:
            return mutated
        
        gene = mutated.genes.pop(i)
        mutated.genes.insert(j, gene)
        mutated.invalidate_cache()
        
        return mutated


class DisplacementMutation(MutationOperator):
    """
    Mutação por Deslocamento (Displacement Mutation).
    
    Remove um segmento do cromossomo e o insere em outra posição.
    
    Exemplo:
        Antes:  [1, 2, 3, 4, 5, 6]
        Após:   [1, 5, 2, 3, 4, 6]  (moveu [2,3,4] para depois de 5)
    """
    
    @property
    def name(self) -> str:
        return "Displacement Mutation"
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        if not self.should_mutate():
            return chromosome
        
        mutated = chromosome.copy()
        size = len(mutated.genes)
        
        if size < 3:
            return mutated
        
        i, j = sorted(random.sample(range(size), 2))
        segment = mutated.genes[i:j+1]
        del mutated.genes[i:j+1]
        
        new_size = len(mutated.genes)
        k = random.randint(0, new_size)
        mutated.genes[k:k] = segment
        mutated.invalidate_cache()
        
        return mutated


class GaussianMutation(MutationOperator):
    """
    Mutação Gaussiana (Gaussian Mutation).
    
    Adiciona ruído gaussiano (distribuição normal) aos genes reais.
    Aplicável para os fatores de velocidade no modo Híbrido.
    
    Funcionamento:
    1. Para cada fator de velocidade, adiciona um valor aleatório N(0, sigma)
    2. Garante que o valor permaneça nos limites [0.5, 1.5]
    """
    
    def __init__(self, mutation_rate: float = 0.1, sigma: float = 0.1):
        super().__init__(mutation_rate)
        self.sigma = sigma
    
    @property
    def name(self) -> str:
        return "Gaussian Mutation"
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        # Se não tiver speed_factors, não faz nada
        if not chromosome.speed_factors:
            return chromosome
            
        if not self.should_mutate():
            return chromosome
        
        mutated = chromosome.copy()
        
        # Aplica mutação em cada fator de velocidade
        new_speeds = []
        for speed in mutated.speed_factors:
            # Adiciona ruído com probabilidade (ou sempre? Geralmente mutação real altera um pouco tudo ou alguns)
            # Aqui vamos alterar com probabilidade 50% cada gene para variar
            if random.random() < 0.5:
                noise = random.gauss(0, self.sigma)
                new_speed = max(0.5, min(1.5, speed + noise)) # Clamp [0.5, 1.5]
                new_speeds.append(new_speed)
            else:
                new_speeds.append(speed)
        
        mutated.speed_factors = new_speeds
        mutated.invalidate_cache()
        return mutated


class TwoOptMutation(MutationOperator):
    """
    Mutação por 2-opt.
    Reconecta duas arestas para eliminar cruzamentos, invertendo um segmento.
    É equivalente à Inversion Mutation, mas com semântica de melhoria local.
    """
    
    @property
    def name(self) -> str:
        return "2-opt Mutation"
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        if not self.should_mutate():
            return chromosome
        
        mutated = chromosome.copy()
        size = len(mutated.genes)
        if size < 4:
            return mutated
            
        i, j = sorted(random.sample(range(size), 2))
        mutated.genes[i:j+1] = mutated.genes[i:j+1][::-1]
        mutated.invalidate_cache()
        return mutated


class ThreeOptMutation(MutationOperator):
    """
    Mutação por 3-opt.
    Remove três arestas e tenta reconectá-las de forma otimizada.
    Aqui implementada como uma mutação que embaralha ou inverte 3 segmentos.
    """
    
    @property
    def name(self) -> str:
        return "3-opt Mutation"
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        if not self.should_mutate():
            return chromosome
            
        mutated = chromosome.copy()
        size = len(mutated.genes)
        if size < 6:
            return mutated
            
        # Seleciona 3 cortes
        indices = sorted(random.sample(range(size), 3))
        i, j, k = indices
        
        # Existem várias formas de reconectar 3 segmentos (A, B, C, D)
        # Vamos usar uma simples inversão e troca de segmentos
        part1 = mutated.genes[:i]
        part2 = mutated.genes[i:j]
        part3 = mutated.genes[j:k]
        part4 = mutated.genes[k:]
        
        # Caso aleatório de 3-opt reconexão
        r = random.random()
        if r < 0.5:
            mutated.genes = part1 + part3 + part2 + part4
        else:
            mutated.genes = part1 + part3[::-1] + part2[::-1] + part4
            
        mutated.invalidate_cache()
        return mutated


class ReverseSequenceMutation(MutationOperator):
    """
    Reverse Sequence Mutation (RSM).
    Inverte a sequência de um segmento selecionado aleatoriamente.
    Semelhante à inversão simples.
    """
    
    @property
    def name(self) -> str:
        return "Reverse Sequence Mutation"
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        if not self.should_mutate():
            return chromosome
            
        mutated = chromosome.copy()
        size = len(mutated.genes)
        if size < 2: return mutated
        
        i, j = sorted(random.sample(range(size), 2))
        mutated.genes[i:j+1] = list(reversed(mutated.genes[i:j+1]))
        mutated.invalidate_cache()
        return mutated


class HybridMutation(MutationOperator):
    """
    Mutação Híbrida.
    
    Combina uma mutação combinatória (para as rotas) com 
    uma mutação gaussiana (para as velocidades).
    """
    
    def __init__(self, mutation_rate: float = 0.1, 
                 combinatorial_op: MutationOperator = None):
        super().__init__(mutation_rate)
        self.combinatorial_op = combinatorial_op or InversionMutation(mutation_rate=1.0) # Taxa controlada pelo pai
        self.gaussian_op = GaussianMutation(mutation_rate=1.0, sigma=0.1)
    
    @property
    def name(self) -> str:
        return f"Hybrid Mutation ({self.combinatorial_op.name} + Gaussian)"
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        if not self.should_mutate():
            return chromosome
        
        # Copia primeiro
        mutated = chromosome.copy()
        
        # Aplica mutação combinatória (rotas)
        # Note: passamos 'mutated' não 'chromosome' para acumular mudanças
        # Forçamos execução (taxa já testada no Hybrid)
        if self.combinatorial_op:
             mutated = self.combinatorial_op.mutate(mutated)
        
        # Aplica mutação gaussiana (velocidades)
        # O GaussianMutation.mutate faz verificação de taxa, mas instanciamos com rate=1.0
        # Entretanto, sua lógica interna pode ter randomness nos genes
        mutated = self.gaussian_op.mutate(mutated)
        
        return mutated


def create_mutation(method: MutationMethod, 
                    mutation_rate: float = 0.1,
                    **kwargs) -> MutationOperator:
    """
    Factory function para criar operadores de mutação.
    """
    if method == MutationMethod.SWAP:
        return SwapMutation(mutation_rate)
    elif method == MutationMethod.INVERSION:
        return InversionMutation(mutation_rate)
    elif method == MutationMethod.SCRAMBLE:
        return ScrambleMutation(mutation_rate)
    elif method == MutationMethod.INSERT:
        return InsertMutation(mutation_rate)
    elif method == MutationMethod.DISPLACEMENT:
        return DisplacementMutation(mutation_rate)
    elif method == MutationMethod.GAUSSIAN:
        return GaussianMutation(mutation_rate, sigma=kwargs.get('sigma', 0.1))
    elif method == MutationMethod.HYBRID:
        # Por padrão usa Inversion como base combinatória se não especificado
        base_op = InversionMutation(mutation_rate=1.0) # Always apply inside hybrid
        return HybridMutation(mutation_rate, combinatorial_op=base_op)
    elif method == MutationMethod.TWO_OPT:
        return TwoOptMutation(mutation_rate)
    elif method == MutationMethod.THREE_OPT:
        return ThreeOptMutation(mutation_rate)
    elif method == MutationMethod.REVERSE_SEQUENCE:
        return ReverseSequenceMutation(mutation_rate)
    
    raise ValueError(f"Método de mutação desconhecido: {method}")

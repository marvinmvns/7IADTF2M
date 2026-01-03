"""
Módulo de Operadores de Crossover
=================================

Este módulo implementa diversos operadores de crossover especializados
para problemas de permutação como o TSP (Travelling Salesman Problem).

Operadores Implementados:
------------------------
1. PMX - Partially Mapped Crossover
2. OX - Order Crossover
3. CX - Cycle Crossover
4. AEX - Alternating Edges Crossover
5. ERX - Edge Recombination Crossover
6. SCX - Sequential Constructive Crossover
7. OX2 - Order-Based Crossover
8. POS - Position-Based Crossover

Referências:
-----------
- Goldberg, D. E., & Lingle, R. (1985). Alleles, loci, and the TSP.
- Davis, L. (1985). Applying adaptive algorithms to epistatic domains.
- Oliver, I. M., et al. (1987). A study of permutation crossover operators.
- Whitley, D., et al. (1989). The traveling salesman and sequence scheduling.
"""

import random
from typing import List, Tuple, Optional, Set
from abc import ABC, abstractmethod
from enum import Enum
from collections import defaultdict

from .chromosome import Chromosome


class CrossoverMethod(Enum):
    """Enumeração dos métodos de crossover disponíveis."""
    PMX = "partially_mapped_crossover"
    OX = "order_crossover"
    CX = "cycle_crossover"
    AEX = "alternating_edges_crossover"
    ERX = "edge_recombination_crossover"
    SCX = "sequential_constructive_crossover"
    OX2 = "order_based_crossover"
    POS = "position_based_crossover"
    ARITHMETIC = "arithmetic"
    HYBRID = "hybrid"


class CrossoverOperator(ABC):
    """
    Classe base abstrata para operadores de crossover.
    
    Define a interface comum que todos os operadores de crossover
    devem implementar.
    """
    
    def __init__(self, crossover_rate: float = 0.9):
        """
        Inicializa o operador de crossover.
        
        Args:
            crossover_rate: Probabilidade de aplicar crossover (0 a 1)
        """
        self.crossover_rate = crossover_rate
    
    @abstractmethod
    def crossover(self, parent1: Chromosome, 
                  parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """
        Realiza o crossover entre dois pais.
        
        Args:
            parent1: Primeiro cromossomo pai
            parent2: Segundo cromossomo pai
        
        Returns:
            Tupla com dois cromossomos filhos
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Retorna o nome do operador de crossover."""
        pass
    
    def should_crossover(self) -> bool:
        """Determina se o crossover deve ser aplicado."""
        return random.random() < self.crossover_rate


class PMXCrossover(CrossoverOperator):
    """
    Partially Mapped Crossover (PMX).
    
    O PMX foi proposto por Goldberg e Lingle (1985) e é um dos
    operadores de crossover mais utilizados para TSP.
    
    Funcionamento:
    1. Seleciona dois pontos de corte aleatórios
    2. Copia o segmento entre os pontos do pai para o filho
    3. Mapeia os genes restantes usando a relação de mapeamento
    
    Características:
    - Preserva a ordem relativa e posição absoluta parcialmente
    - Garante que o resultado seja uma permutação válida
    - Transmite informação de adjacência dos pais
    """
    
    @property
    def name(self) -> str:
        return "PMX (Partially Mapped Crossover)"
    
    def crossover(self, parent1: Chromosome, 
                  parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """
        Realiza o crossover PMX.
        
        Args:
            parent1: Primeiro cromossomo pai
            parent2: Segundo cromossomo pai
        
        Returns:
            Tupla com dois cromossomos filhos
        """
        if not self.should_crossover():
            return parent1.copy(), parent2.copy()
        
        size = len(parent1.genes)
        
        # Seleciona pontos de corte
        point1, point2 = sorted(random.sample(range(size), 2))
        
        # Inicializa filhos
        child1_genes = [None] * size
        child2_genes = [None] * size
        
        # Copia segmentos entre os pontos de corte
        child1_genes[point1:point2] = parent1.genes[point1:point2]
        child2_genes[point1:point2] = parent2.genes[point1:point2]
        
        # Cria mapeamentos
        mapping1 = {}  # De parent2 para parent1
        mapping2 = {}  # De parent1 para parent2
        
        for i in range(point1, point2):
            mapping1[parent2.genes[i]] = parent1.genes[i]
            mapping2[parent1.genes[i]] = parent2.genes[i]
        
        # Preenche posições restantes do filho 1
        for i in list(range(0, point1)) + list(range(point2, size)):
            gene = parent2.genes[i]
            while gene in child1_genes[point1:point2]:
                gene = mapping1.get(gene, gene)
            child1_genes[i] = gene
        
        # Preenche posições restantes do filho 2
        for i in list(range(0, point1)) + list(range(point2, size)):
            gene = parent1.genes[i]
            while gene in child2_genes[point1:point2]:
                gene = mapping2.get(gene, gene)
            child2_genes[i] = gene
        
        # Cria cromossomos filhos
        child1 = Chromosome(
            genes=child1_genes,
            delivery_points=parent1.delivery_points,
            vehicles=parent1.vehicles,
            depot_index=parent1.depot_index
        )
        child2 = Chromosome(
            genes=child2_genes,
            delivery_points=parent2.delivery_points,
            vehicles=parent2.vehicles,
            depot_index=parent2.depot_index
        )
        
        return child1, child2


class OXCrossover(CrossoverOperator):
    """
    Order Crossover (OX).
    
    O OX foi proposto por Davis (1985) e preserva a ordem relativa
    dos genes dos pais.
    
    Funcionamento:
    1. Seleciona um segmento do primeiro pai
    2. Copia o segmento para o filho na mesma posição
    3. Preenche as posições restantes com genes do segundo pai,
       na ordem em que aparecem, pulando os já presentes
    
    Características:
    - Preserva a ordem relativa dos genes
    - Não preserva posições absolutas fora do segmento
    - Bom para problemas onde a ordem é mais importante que a posição
    """
    
    @property
    def name(self) -> str:
        return "OX (Order Crossover)"
    
    def crossover(self, parent1: Chromosome, 
                  parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """
        Realiza o crossover OX.
        
        Args:
            parent1: Primeiro cromossomo pai
            parent2: Segundo cromossomo pai
        
        Returns:
            Tupla com dois cromossomos filhos
        """
        if not self.should_crossover():
            return parent1.copy(), parent2.copy()
        
        size = len(parent1.genes)
        
        # Seleciona pontos de corte
        point1, point2 = sorted(random.sample(range(size), 2))
        
        # Cria filho 1
        child1_genes = self._ox_create_child(
            parent1.genes, parent2.genes, point1, point2
        )
        
        # Cria filho 2
        child2_genes = self._ox_create_child(
            parent2.genes, parent1.genes, point1, point2
        )
        
        child1 = Chromosome(
            genes=child1_genes,
            delivery_points=parent1.delivery_points,
            vehicles=parent1.vehicles,
            depot_index=parent1.depot_index
        )
        child2 = Chromosome(
            genes=child2_genes,
            delivery_points=parent2.delivery_points,
            vehicles=parent2.vehicles,
            depot_index=parent2.depot_index
        )
        
        return child1, child2
    
    def _ox_create_child(self, parent1: List[int], parent2: List[int],
                         point1: int, point2: int) -> List[int]:
        """Cria um filho usando a lógica do OX."""
        size = len(parent1)
        child = [None] * size
        
        # Copia segmento do pai 1
        segment = set(parent1[point1:point2])
        child[point1:point2] = parent1[point1:point2]
        
        # Preenche restante com genes do pai 2
        pos = point2 % size
        for gene in parent2[point2:] + parent2[:point2]:
            if gene not in segment:
                while child[pos] is not None:
                    pos = (pos + 1) % size
                child[pos] = gene
        
        return child


class CXCrossover(CrossoverOperator):
    """
    Cycle Crossover (CX).
    
    O CX foi proposto por Oliver et al. (1987) e preserva as
    posições absolutas dos genes.
    
    Funcionamento:
    1. Identifica ciclos de posições entre os dois pais
    2. Alterna entre copiar ciclos do pai 1 e pai 2
    
    Características:
    - Preserva posições absolutas
    - Cada gene vem de um dos pais na mesma posição
    - Pode resultar em filhos idênticos aos pais em alguns casos
    """
    
    @property
    def name(self) -> str:
        return "CX (Cycle Crossover)"
    
    def crossover(self, parent1: Chromosome, 
                  parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """
        Realiza o crossover CX.
        
        Args:
            parent1: Primeiro cromossomo pai
            parent2: Segundo cromossomo pai
        
        Returns:
            Tupla com dois cromossomos filhos
        """
        if not self.should_crossover():
            return parent1.copy(), parent2.copy()
        
        size = len(parent1.genes)
        child1_genes = [None] * size
        child2_genes = [None] * size
        
        # Encontra ciclos
        cycles = self._find_cycles(parent1.genes, parent2.genes)
        
        # Alterna ciclos entre os pais
        for i, cycle in enumerate(cycles):
            if i % 2 == 0:
                for pos in cycle:
                    child1_genes[pos] = parent1.genes[pos]
                    child2_genes[pos] = parent2.genes[pos]
            else:
                for pos in cycle:
                    child1_genes[pos] = parent2.genes[pos]
                    child2_genes[pos] = parent1.genes[pos]
        
        child1 = Chromosome(
            genes=child1_genes,
            delivery_points=parent1.delivery_points,
            vehicles=parent1.vehicles,
            depot_index=parent1.depot_index
        )
        child2 = Chromosome(
            genes=child2_genes,
            delivery_points=parent2.delivery_points,
            vehicles=parent2.vehicles,
            depot_index=parent2.depot_index
        )
        
        return child1, child2
    
    def _find_cycles(self, parent1: List[int], 
                     parent2: List[int]) -> List[List[int]]:
        """Encontra os ciclos entre dois pais."""
        size = len(parent1)
        visited = [False] * size
        cycles = []
        
        # Cria mapa de valor para posição no pai 1
        pos_map = {gene: i for i, gene in enumerate(parent1)}
        
        for start in range(size):
            if visited[start]:
                continue
            
            cycle = []
            pos = start
            
            while not visited[pos]:
                visited[pos] = True
                cycle.append(pos)
                # Encontra onde o gene do pai 2 está no pai 1
                gene = parent2[pos]
                pos = pos_map[gene]
            
            cycles.append(cycle)
        
        return cycles


class AEXCrossover(CrossoverOperator):
    """
    Alternating Edges Crossover (AEX).
    
    O AEX considera o cromossomo como um ciclo de arestas e
    cria filhos alternando arestas dos dois pais.
    
    Funcionamento:
    1. Começa com uma aresta do pai 1
    2. Alterna entre adicionar arestas do pai 1 e pai 2
    3. Se uma aresta criar ciclo inválido, escolhe aleatoriamente
    
    Características:
    - Preserva arestas (adjacências) dos pais
    - Bom para problemas onde adjacência é importante
    """
    
    @property
    def name(self) -> str:
        return "AEX (Alternating Edges Crossover)"
    
    def crossover(self, parent1: Chromosome, 
                  parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """
        Realiza o crossover AEX.
        
        Args:
            parent1: Primeiro cromossomo pai
            parent2: Segundo cromossomo pai
        
        Returns:
            Tupla com dois cromossomos filhos
        """
        if not self.should_crossover():
            return parent1.copy(), parent2.copy()
        
        child1_genes = self._aex_create_child(parent1.genes, parent2.genes)
        child2_genes = self._aex_create_child(parent2.genes, parent1.genes)
        
        child1 = Chromosome(
            genes=child1_genes,
            delivery_points=parent1.delivery_points,
            vehicles=parent1.vehicles,
            depot_index=parent1.depot_index
        )
        child2 = Chromosome(
            genes=child2_genes,
            delivery_points=parent2.delivery_points,
            vehicles=parent2.vehicles,
            depot_index=parent2.depot_index
        )
        
        return child1, child2
    
    def _aex_create_child(self, parent1: List[int], 
                          parent2: List[int]) -> List[int]:
        """Cria um filho usando a lógica do AEX."""
        size = len(parent1)
        child = []
        visited = set()
        
        # Cria mapas de adjacência
        adj1 = self._create_adjacency_map(parent1)
        adj2 = self._create_adjacency_map(parent2)
        
        # Começa com primeiro gene do pai 1
        current = parent1[0]
        child.append(current)
        visited.add(current)
        
        use_parent1 = False  # Alterna começando com pai 2
        
        while len(child) < size:
            adj_map = adj1 if use_parent1 else adj2
            neighbors = adj_map.get(current, [])
            
            # Encontra vizinho não visitado
            next_gene = None
            for neighbor in neighbors:
                if neighbor not in visited:
                    next_gene = neighbor
                    break
            
            # Se não encontrou, escolhe aleatoriamente
            if next_gene is None:
                unvisited = [g for g in parent1 if g not in visited]
                if unvisited:
                    next_gene = random.choice(unvisited)
                else:
                    break
            
            child.append(next_gene)
            visited.add(next_gene)
            current = next_gene
            use_parent1 = not use_parent1
        
        return child
    
    def _create_adjacency_map(self, genes: List[int]) -> dict:
        """Cria mapa de adjacência para um cromossomo."""
        adj = defaultdict(list)
        size = len(genes)
        
        for i in range(size):
            gene = genes[i]
            prev_gene = genes[(i - 1) % size]
            next_gene = genes[(i + 1) % size]
            adj[gene].extend([prev_gene, next_gene])
        
        return adj


class ERXCrossover(CrossoverOperator):
    """
    Edge Recombination Crossover (ERX).
    
    O ERX foi proposto por Whitley et al. (1989) e é baseado na
    preservação de arestas dos pais.
    
    Funcionamento:
    1. Constrói tabela de arestas combinando adjacências dos dois pais
    2. Escolhe gene inicial aleatoriamente
    3. Seleciona próximo gene priorizando aqueles com menos arestas
    
    Características:
    - Alta taxa de preservação de arestas
    - Bom desempenho em TSP
    - Mais complexo computacionalmente
    """
    
    @property
    def name(self) -> str:
        return "ERX (Edge Recombination Crossover)"
    
    def crossover(self, parent1: Chromosome, 
                  parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """
        Realiza o crossover ERX.
        
        Args:
            parent1: Primeiro cromossomo pai
            parent2: Segundo cromossomo pai
        
        Returns:
            Tupla com dois cromossomos filhos
        """
        if not self.should_crossover():
            return parent1.copy(), parent2.copy()
        
        child1_genes = self._erx_create_child(parent1.genes, parent2.genes)
        child2_genes = self._erx_create_child(parent2.genes, parent1.genes)
        
        child1 = Chromosome(
            genes=child1_genes,
            delivery_points=parent1.delivery_points,
            vehicles=parent1.vehicles,
            depot_index=parent1.depot_index
        )
        child2 = Chromosome(
            genes=child2_genes,
            delivery_points=parent2.delivery_points,
            vehicles=parent2.vehicles,
            depot_index=parent2.depot_index
        )
        
        return child1, child2
    
    def _erx_create_child(self, parent1: List[int], 
                          parent2: List[int]) -> List[int]:
        """Cria um filho usando a lógica do ERX."""
        # Constrói tabela de arestas
        edge_table = self._build_edge_table(parent1, parent2)
        
        child = []
        visited = set()
        
        # Escolhe gene inicial
        current = random.choice(parent1)
        child.append(current)
        visited.add(current)
        
        while len(child) < len(parent1):
            # Remove gene atual das listas de adjacência
            for gene in edge_table:
                edge_table[gene] = [g for g in edge_table[gene] 
                                    if g not in visited]
            
            # Encontra próximo gene
            neighbors = edge_table.get(current, [])
            
            if neighbors:
                # Escolhe vizinho com menor número de arestas
                next_gene = min(neighbors, 
                               key=lambda g: len(edge_table.get(g, [])))
            else:
                # Escolhe aleatoriamente dos não visitados
                unvisited = [g for g in parent1 if g not in visited]
                if not unvisited:
                    break
                next_gene = random.choice(unvisited)
            
            child.append(next_gene)
            visited.add(next_gene)
            current = next_gene
        
        return child
    
    def _build_edge_table(self, parent1: List[int], 
                          parent2: List[int]) -> dict:
        """Constrói tabela de arestas combinando dois pais."""
        edge_table = defaultdict(set)
        size = len(parent1)
        
        # Adiciona arestas do pai 1
        for i in range(size):
            gene = parent1[i]
            edge_table[gene].add(parent1[(i - 1) % size])
            edge_table[gene].add(parent1[(i + 1) % size])
        
        # Adiciona arestas do pai 2
        for i in range(size):
            gene = parent2[i]
            edge_table[gene].add(parent2[(i - 1) % size])
            edge_table[gene].add(parent2[(i + 1) % size])
        
        # Converte sets para listas
        return {k: list(v) for k, v in edge_table.items()}


class SCXCrossover(CrossoverOperator):
    """
    Sequential Constructive Crossover (SCX).
    
    O SCX constrói o filho de forma sequencial, escolhendo o
    próximo gene baseado em critérios de distância.
    
    Funcionamento:
    1. Começa com o primeiro gene do pai 1
    2. Para cada posição, considera os próximos genes de ambos os pais
    3. Escolhe o gene que resulta em menor distância
    
    Características:
    - Incorpora informação de distância na construção
    - Tende a produzir soluções de boa qualidade
    - Requer informação de distância entre genes
    """
    
    @property
    def name(self) -> str:
        return "SCX (Sequential Constructive Crossover)"
    
    def crossover(self, parent1: Chromosome, 
                  parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """
        Realiza o crossover SCX.
        
        Args:
            parent1: Primeiro cromossomo pai
            parent2: Segundo cromossomo pai
        
        Returns:
            Tupla com dois cromossomos filhos
        """
        if not self.should_crossover():
            return parent1.copy(), parent2.copy()
        
        # Usa pontos de entrega para calcular distâncias
        points = parent1.delivery_points
        
        child1_genes = self._scx_create_child(
            parent1.genes, parent2.genes, points
        )
        child2_genes = self._scx_create_child(
            parent2.genes, parent1.genes, points
        )
        
        child1 = Chromosome(
            genes=child1_genes,
            delivery_points=parent1.delivery_points,
            vehicles=parent1.vehicles,
            depot_index=parent1.depot_index
        )
        child2 = Chromosome(
            genes=child2_genes,
            delivery_points=parent2.delivery_points,
            vehicles=parent2.vehicles,
            depot_index=parent2.depot_index
        )
        
        return child1, child2
    
    def _scx_create_child(self, parent1: List[int], parent2: List[int],
                          points: list) -> List[int]:
        """Cria um filho usando a lógica do SCX."""
        size = len(parent1)
        child = []
        visited = set()
        
        # Cria mapas de posição
        pos1 = {gene: i for i, gene in enumerate(parent1)}
        pos2 = {gene: i for i, gene in enumerate(parent2)}
        
        # Começa com primeiro gene do pai 1
        current = parent1[0]
        child.append(current)
        visited.add(current)
        
        while len(child) < size:
            # Encontra próximos genes legítimos em cada pai
            next1 = self._find_next_unvisited(parent1, pos1[current], visited)
            next2 = self._find_next_unvisited(parent2, pos2[current], visited)
            
            # Escolhe baseado na distância
            if next1 is None and next2 is None:
                # Escolhe aleatoriamente dos não visitados
                unvisited = [g for g in parent1 if g not in visited]
                if not unvisited:
                    break
                next_gene = random.choice(unvisited)
            elif next1 is None:
                next_gene = next2
            elif next2 is None:
                next_gene = next1
            else:
                # Compara distâncias se temos pontos de entrega
                if points:
                    dist1 = points[current].distance_to(points[next1])
                    dist2 = points[current].distance_to(points[next2])
                    next_gene = next1 if dist1 <= dist2 else next2
                else:
                    next_gene = random.choice([next1, next2])
            
            child.append(next_gene)
            visited.add(next_gene)
            current = next_gene
        
        return child
    
    def _find_next_unvisited(self, parent: List[int], current_pos: int,
                             visited: Set[int]) -> Optional[int]:
        """Encontra o próximo gene não visitado após a posição atual."""
        size = len(parent)
        for i in range(1, size):
            pos = (current_pos + i) % size
            if parent[pos] not in visited:
                return parent[pos]
        return None


class OX2Crossover(CrossoverOperator):
    """
    Order-Based Crossover (OX2).
    
    Variante do OX que seleciona posições aleatórias ao invés de
    um segmento contínuo.
    
    Funcionamento:
    1. Seleciona posições aleatórias do pai 1
    2. Copia genes dessas posições para o filho
    3. Preenche restante com genes do pai 2 na ordem
    
    Características:
    - Mais flexível que OX
    - Preserva ordem relativa parcialmente
    """
    
    @property
    def name(self) -> str:
        return "OX2 (Order-Based Crossover)"
    
    def crossover(self, parent1: Chromosome, 
                  parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        if not self.should_crossover():
            return parent1.copy(), parent2.copy()
        
        size = len(parent1.genes)
        num_positions = random.randint(1, size - 1)
        positions = sorted(random.sample(range(size), num_positions))
        
        child1_genes = self._ox2_create_child(
            parent1.genes, parent2.genes, positions
        )
        child2_genes = self._ox2_create_child(
            parent2.genes, parent1.genes, positions
        )
        
        child1 = Chromosome(genes=child1_genes, delivery_points=parent1.delivery_points,
                           vehicles=parent1.vehicles, depot_index=parent1.depot_index)
        child2 = Chromosome(genes=child2_genes, delivery_points=parent2.delivery_points,
                           vehicles=parent2.vehicles, depot_index=parent2.depot_index)
        
        return child1, child2

    def _ox2_create_child(self, parent_genes: List[int], template_genes: List[int], 
                           positions: List[int]) -> List[int]:
        """Lógica auxiliar para criar filho no OX2."""
        size = len(parent_genes)
        child = [None] * size
        selected_genes = [parent_genes[i] for i in positions]
        for i in positions:
            child[i] = parent_genes[i]
        remaining_genes = [g for g in template_genes if g not in selected_genes]
        idx = 0
        for i in range(size):
            if child[i] is None:
                child[i] = remaining_genes[idx]
                idx += 1
        return child


class POSCrossover(CrossoverOperator):
    """
    Position-Based Crossover (POS).
    
    Similar ao OX2, mas foca em preservar a posição absoluta de genes
    selecionados aleatoriamente.
    
    Funcionamento:
    1. Seleciona um conjunto de posições aleatórias
    2. Copia os genes nessas posições do pai 1 para o filho nas mesmas posições
    3. Preenche as posições restantes com os genes do pai 2 na ordem em que aparecem
    """
    
    @property
    def name(self) -> str:
        return "POS (Position-Based Crossover)"
    
    def crossover(self, parent1: Chromosome, 
                  parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        if not self.should_crossover():
            return parent1.copy(), parent2.copy()
            
        size = len(parent1.genes)
        num_positions = random.randint(1, size - 1)
        positions = set(random.sample(range(size), num_positions))
        
        def create_child(p1_genes, p2_genes):
            child = [None] * size
            # Copia genes das posições selecionadas de p1
            for pos in positions:
                child[pos] = p1_genes[pos]
            
            # Pega genes de p2 que não foram usados
            p1_selected_set = {p1_genes[pos] for pos in positions}
            remaining = [g for g in p2_genes if g not in p1_selected_set]
            
            # Preenche o resto
            r_idx = 0
            for i in range(size):
                if child[i] is None:
                    child[i] = remaining[r_idx]
                    r_idx += 1
            return child

        c1_genes = create_child(parent1.genes, parent2.genes)
        c2_genes = create_child(parent2.genes, parent1.genes)
        
        child1 = Chromosome(genes=c1_genes, delivery_points=parent1.delivery_points,
                           vehicles=parent1.vehicles, depot_index=parent1.depot_index)
        child2 = Chromosome(genes=c2_genes, delivery_points=parent2.delivery_points,
                           vehicles=parent2.vehicles, depot_index=parent2.depot_index)
        
        return child1, child2

    
class ArithmeticCrossover(CrossoverOperator):
    """
    Crossover Aritmético (Arithmetic Crossover).
    
    Combina linearmente os valores numéricos dos pais.
    Usado para a parte Real (velocidade) na codificação híbrida.
    
    Filho = alpha * Pai1 + (1-alpha) * Pai2
    """
    
    def __init__(self, crossover_rate: float = 0.9, alpha: float = 0.5):
        super().__init__(crossover_rate)
        self.alpha = alpha
    
    @property
    def name(self) -> str:
        return "Arithmetic Crossover"
    
    def crossover(self, parent1: Chromosome, 
                  parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        # Se não tiver speed_factors, retorna cópia
        if not parent1.speed_factors:
            return parent1.copy(), parent2.copy()
            
        if not self.should_crossover():
            return parent1.copy(), parent2.copy()
        
        # Cria filhos copiando estrutura do pai 1 (genes não mudam neste operador puro)
        child1 = parent1.copy()
        child2 = parent2.copy()
        
        # Combina velocidades
        size = len(parent1.speed_factors)
        for i in range(size):
            p1_val = parent1.speed_factors[i]
            p2_val = parent2.speed_factors[i]
            
            # Filho 1 e 2 com média ponderada
            # Poderíamos fazer um aleatório para cada gene ou fixo alpha
            # Texto diz "combina valores... usando pesos"
            c1_val = self.alpha * p1_val + (1 - self.alpha) * p2_val
            c2_val = (1 - self.alpha) * p1_val + self.alpha * p2_val
            
            child1.speed_factors[i] = c1_val
            child2.speed_factors[i] = c2_val
        
        return child1, child2


class HybridCrossover(CrossoverOperator):
    """
    Crossover Híbrido.
    
    Aplica crossover combinatório nos genes (rotas) e
    crossover aritmético nas velocidades (real).
    """
    
    def __init__(self, crossover_rate: float = 0.9, 
                 combinatorial_op: CrossoverOperator = None):
        super().__init__(crossover_rate)
        self.combinatorial_op = combinatorial_op or OXCrossover(crossover_rate=1.0)
        self.arithmetic_op = ArithmeticCrossover(crossover_rate=1.0)
    
    @property
    def name(self) -> str:
        return f"Hybrid Crossover ({self.combinatorial_op.name} + Arithmetic)"
    
    def crossover(self, parent1: Chromosome, 
                  parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        if not self.should_crossover():
            return parent1.copy(), parent2.copy()
        
        # 1. Aplica Crossover Combinatório (Gera novos genes)
        child1, child2 = self.combinatorial_op.crossover(parent1, parent2)
        
        # 2. Aplica Crossover Aritmético (Gera novas velocidades)
        # Note: ArithmeticCrossover retorna cópia, então precisamos atualizar os childs gerados
        # Mas Arithmetic espera receber os pais originais para misturar os valores
        # Então chamamos Arithmetic nos pais originais apenas para pegar os valores
        temp_c1, temp_c2 = self.arithmetic_op.crossover(parent1, parent2)
        
        # Transfere as velocidades calculadas para os filhos combinatórios
        child1.speed_factors = temp_c1.speed_factors
        child2.speed_factors = temp_c2.speed_factors
        
        return child1, child2


def create_crossover(method: CrossoverMethod, 
                     crossover_rate: float = 0.9,
                     **kwargs) -> CrossoverOperator:
    """
    Factory function para criar operadores de crossover.
    """
    crossovers = {
        CrossoverMethod.PMX: PMXCrossover,
        CrossoverMethod.OX: OXCrossover,
        CrossoverMethod.CX: CXCrossover,
        CrossoverMethod.AEX: AEXCrossover,
        CrossoverMethod.ERX: ERXCrossover,
        CrossoverMethod.SCX: SCXCrossover,
        CrossoverMethod.OX2: OX2Crossover,
        CrossoverMethod.POS: POSCrossover,
        CrossoverMethod.ARITHMETIC: ArithmeticCrossover,
        CrossoverMethod.HYBRID: HybridCrossover,
    }
    
    # Handle Hybrid requiring sub-operator
    if method == CrossoverMethod.HYBRID:
        # Default to OX inside Hybrid
        base_op = OXCrossover(crossover_rate=1.0)
        return HybridCrossover(crossover_rate, combinatorial_op=base_op)
        
    if method not in crossovers:
        # Fallback genérico ou erro. POS não estava implementado na listagem anterior completa, mas estava no Enum?
        # Vou assumir que POS estava no Enum mas talvez não implementado classe. 
        # Vou checar o enum novamente.
        raise ValueError(f"Método de crossover desconhecido: {method}")
    
    return crossovers[method](crossover_rate=crossover_rate, **kwargs)

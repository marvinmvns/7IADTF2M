"""
Módulo de Representação de Cromossomos
======================================

Este módulo define a estrutura de dados para representar soluções
do problema de roteamento como cromossomos em um algoritmo genético.

A representação utilizada é a codificação por permutação, onde cada
gene representa um ponto de entrega e a ordem dos genes define a rota.

Referências:
-----------
- Goldberg, D. E. (1989). Genetic Algorithms in Search, Optimization, and Machine Learning.
- Larrañaga, P. et al. (1999). Genetic Algorithms for the Travelling Salesman Problem.
"""

import random
import math
import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass, field
from copy import deepcopy

# =============================================================================
# CONFIGURAÇÃO DE CÁLCULO DE DISTÂNCIA
# =============================================================================
# Por padrão, usa a fórmula de Haversine para calcular distâncias reais em km
# entre coordenadas geográficas (latitude/longitude).
# Altere USE_HAVERSINE para False para usar distância euclidiana.

USE_HAVERSINE = True
EARTH_RADIUS_KM = 6371.0  # Raio médio da Terra em quilômetros


def haversine_distance(lat1: float, lon1: float, 
                       lat2: float, lon2: float) -> float:
    """
    Calcula a distância entre dois pontos na Terra usando a fórmula de Haversine.
    
    A fórmula de Haversine determina a distância do grande círculo entre
    dois pontos em uma esfera dadas suas longitudes e latitudes.
    
    Args:
        lat1: Latitude do primeiro ponto em graus decimais
        lon1: Longitude do primeiro ponto em graus decimais
        lat2: Latitude do segundo ponto em graus decimais
        lon2: Longitude do segundo ponto em graus decimais
    
    Returns:
        Distância entre os dois pontos em quilômetros
    
    Example:
        >>> # Distância entre São Paulo e Rio de Janeiro
        >>> haversine_distance(-23.5505, -46.6333, -22.9068, -43.1729)
        357.89  # aproximadamente 358 km
    """
    # Converte graus para radianos
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    lon1_rad = math.radians(lon1)
    lon2_rad = math.radians(lon2)
    
    # Diferenças
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Fórmula de Haversine
    a = math.sin(dlat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = EARTH_RADIUS_KM * c
    
    return distance


@dataclass
class DeliveryPoint:
    """
    Representa um ponto de entrega no sistema hospitalar.
    
    Attributes:
        id: Identificador único do ponto
        name: Nome do local (hospital, unidade, residência)
        x: Coordenada X (longitude simplificada)
        y: Coordenada Y (latitude simplificada)
        priority: Prioridade da entrega (1=crítico, 2=urgente, 3=regular)
        demand: Quantidade de carga necessária (em unidades)
        time_window: Janela de tempo para entrega (início, fim) em minutos
    """
    id: int
    name: str
    x: float
    y: float
    priority: int = 3  # 1=crítico, 2=urgente, 3=regular
    demand: float = 1.0
    time_window: Tuple[int, int] = (0, 1440)  # 24 horas em minutos
    
    def distance_to(self, other: 'DeliveryPoint', 
                     use_haversine: bool = None) -> float:
        """
        Calcula a distância até outro ponto de entrega.
        
        Por padrão, usa a fórmula de Haversine para calcular a distância
        real em quilômetros entre dois pontos geográficos (latitude/longitude).
        
        Args:
            other: Outro ponto de entrega
            use_haversine: Se True, usa Haversine; se False, usa Euclidiana.
                          Se None, usa a configuração global USE_HAVERSINE.
        
        Returns:
            Distância em quilômetros (Haversine) ou unidades (Euclidiana)
        
        Note:
            - self.x representa a LONGITUDE do ponto
            - self.y representa a LATITUDE do ponto
            - Para Haversine: retorna distância em km
        """
        # Determina qual método usar
        if use_haversine is None:
            use_haversine = USE_HAVERSINE
        
        if use_haversine:
            # Usa Haversine para distância geodésica real
            # Nota: y = latitude, x = longitude
            return haversine_distance(
                lat1=self.y, lon1=self.x,
                lat2=other.y, lon2=other.x
            )
        else:
            # Distância euclidiana (para coordenadas cartesianas)
            return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


@dataclass
class Vehicle:
    """
    Representa um veículo de entrega.
    
    Attributes:
        id: Identificador do veículo
        capacity: Capacidade máxima de carga
        max_distance: Autonomia máxima (distância que pode percorrer)
        speed: Velocidade média (unidades de distância por minuto)
    """
    id: int
    capacity: float = 100.0
    max_distance: float = 500.0
    speed: float = 1.0  # unidades por minuto


class Route:
    """
    Representa uma rota completa de entrega.
    
    Uma rota é uma sequência ordenada de pontos de entrega que um
    veículo deve visitar, partindo e retornando ao depósito.
    
    Attributes:
        points: Lista de pontos de entrega na ordem de visitação
        vehicle: Veículo designado para esta rota
        depot: Ponto de partida/chegada (depósito central)
    """
    
    def __init__(self, points: List[DeliveryPoint], 
                 vehicle: Optional[Vehicle] = None,
                 depot: Optional[DeliveryPoint] = None):
        """
        Inicializa uma rota.
        
        Args:
            points: Lista de pontos de entrega
            vehicle: Veículo designado (opcional)
            depot: Ponto de depósito (opcional, usa primeiro ponto se não fornecido)
        """
        self.points = points
        self.vehicle = vehicle or Vehicle(id=0)
        self.depot = depot or (points[0] if points else None)
        self._total_distance: Optional[float] = None
        self._total_demand: Optional[float] = None
    
    @property
    def total_distance(self) -> float:
        """Calcula a distância total da rota (incluindo retorno ao depósito)."""
        if self._total_distance is None:
            self._calculate_metrics()
        return self._total_distance
    
    @property
    def total_demand(self) -> float:
        """Calcula a demanda total da rota."""
        if self._total_demand is None:
            self._calculate_metrics()
        return self._total_demand
    
    def _calculate_metrics(self):
        """Calcula métricas da rota (distância e demanda)."""
        if not self.points:
            self._total_distance = 0.0
            self._total_demand = 0.0
            return
        
        # Distância do depósito ao primeiro ponto
        distance = self.depot.distance_to(self.points[0]) if self.depot else 0.0
        
        # Distância entre pontos consecutivos
        for i in range(len(self.points) - 1):
            distance += self.points[i].distance_to(self.points[i + 1])
        
        # Distância do último ponto de volta ao depósito
        if self.depot:
            distance += self.points[-1].distance_to(self.depot)
        
        self._total_distance = distance
        self._total_demand = sum(p.demand for p in self.points)
    
    def invalidate_cache(self):
        """Invalida o cache de métricas após modificação da rota."""
        self._total_distance = None
        self._total_demand = None
    
    def is_feasible(self) -> Tuple[bool, List[str]]:
        """
        Verifica se a rota é viável considerando as restrições.
        
        Returns:
            Tupla (é_viável, lista_de_violações)
        """
        violations = []
        
        # Verificar capacidade do veículo
        if self.total_demand > self.vehicle.capacity:
            violations.append(
                f"Demanda ({self.total_demand:.1f}) excede capacidade ({self.vehicle.capacity:.1f})"
            )
        
        # Verificar autonomia do veículo
        if self.total_distance > self.vehicle.max_distance:
            violations.append(
                f"Distância ({self.total_distance:.1f}) excede autonomia ({self.vehicle.max_distance:.1f})"
            )
        
        return len(violations) == 0, violations
    
    def __len__(self) -> int:
        return len(self.points)
    
    def __repr__(self) -> str:
        point_ids = [p.id for p in self.points]
        return f"Route({point_ids}, dist={self.total_distance:.2f})"


class Chromosome:
    """
    Representa um cromossomo no algoritmo genético.
    
    Um cromossomo codifica uma solução completa para o problema de
    roteamento, podendo conter uma ou múltiplas rotas (para VRP).
    
    A codificação utilizada é a representação por permutação, onde
    cada gene é um índice de ponto de entrega e a ordem dos genes
    define a sequência de visitação.
    
    Attributes:
        genes: Lista de índices dos pontos de entrega
        routes: Lista de rotas (para problemas com múltiplos veículos)
        fitness: Valor de aptidão do cromossomo
    """
    
    def __init__(self, genes: List[int], 
                 delivery_points: Optional[List[DeliveryPoint]] = None,
                 vehicles: Optional[List[Vehicle]] = None,
                 depot_index: int = 0):
        """
        Inicializa um cromossomo.
        
        Args:
            genes: Lista de índices representando a ordem de visitação
            delivery_points: Lista de pontos de entrega disponíveis
            vehicles: Lista de veículos disponíveis
            depot_index: Índice do ponto que serve como depósito
        """
        self.genes = genes
        self.delivery_points = delivery_points or []
        self.vehicles = vehicles or [Vehicle(id=0)]
        self.depot_index = depot_index
        self._fitness: Optional[float] = None
        self._routes: Optional[List[Route]] = None
    
    @classmethod
    def create_random(cls, num_points: int, 
                      delivery_points: Optional[List[DeliveryPoint]] = None,
                      vehicles: Optional[List[Vehicle]] = None,
                      depot_index: int = 0) -> 'Chromosome':
        """
        Cria um cromossomo com genes aleatórios.
        
        Args:
            num_points: Número de pontos de entrega (excluindo depósito)
            delivery_points: Lista de pontos de entrega
            vehicles: Lista de veículos
            depot_index: Índice do depósito
        
        Returns:
            Novo cromossomo com permutação aleatória
        """
        # Gera índices excluindo o depósito
        indices = [i for i in range(num_points + 1) if i != depot_index]
        random.shuffle(indices)
        
        return cls(genes=indices, 
                   delivery_points=delivery_points,
                   vehicles=vehicles,
                   depot_index=depot_index)
    
    @classmethod
    def create_nearest_neighbor(cls, num_points: int,
                                delivery_points: List[DeliveryPoint],
                                vehicles: Optional[List[Vehicle]] = None,
                                depot_index: int = 0) -> 'Chromosome':
        """
        Cria um cromossomo usando heurística do vizinho mais próximo.
        
        Esta heurística construtiva gera uma solução inicial de qualidade
        razoável, começando do depósito e sempre visitando o ponto não
        visitado mais próximo.
        
        Args:
            num_points: Número de pontos de entrega
            delivery_points: Lista de pontos de entrega
            vehicles: Lista de veículos
            depot_index: Índice do depósito
        
        Returns:
            Cromossomo construído pela heurística
        """
        depot = delivery_points[depot_index]
        unvisited = set(i for i in range(len(delivery_points)) if i != depot_index)
        genes = []
        current = depot
        
        while unvisited:
            # Encontra o ponto não visitado mais próximo
            nearest = min(unvisited, 
                         key=lambda i: current.distance_to(delivery_points[i]))
            genes.append(nearest)
            current = delivery_points[nearest]
            unvisited.remove(nearest)
        
        return cls(genes=genes,
                   delivery_points=delivery_points,
                   vehicles=vehicles,
                   depot_index=depot_index)
    
    @property
    def fitness(self) -> float:
        """Retorna o valor de fitness do cromossomo."""
        return self._fitness if self._fitness is not None else float('inf')
    
    @fitness.setter
    def fitness(self, value: float):
        """Define o valor de fitness do cromossomo."""
        self._fitness = value
    
    def get_routes(self) -> List[Route]:
        """
        Converte os genes em rotas.
        
        Para TSP simples, retorna uma única rota.
        Para VRP, divide os genes entre múltiplos veículos.
        
        Returns:
            Lista de rotas
        """
        if self._routes is not None:
            return self._routes
        
        if not self.delivery_points:
            return []
        
        depot = self.delivery_points[self.depot_index]
        points = [self.delivery_points[i] for i in self.genes]
        
        # Para TSP simples (um veículo)
        if len(self.vehicles) == 1:
            self._routes = [Route(points=points, 
                                  vehicle=self.vehicles[0],
                                  depot=depot)]
        else:
            # Para VRP (múltiplos veículos) - divisão simples
            self._routes = self._split_routes_for_vrp(points, depot)
        
        return self._routes
    
    def _split_routes_for_vrp(self, points: List[DeliveryPoint], 
                               depot: DeliveryPoint) -> List[Route]:
        """
        Divide os pontos entre múltiplos veículos para VRP.
        
        Utiliza uma heurística de bin-packing baseada na capacidade
        dos veículos.
        
        Args:
            points: Lista de pontos a serem divididos
            depot: Ponto de depósito
        
        Returns:
            Lista de rotas, uma para cada veículo necessário
        """
        routes = []
        current_points = []
        current_demand = 0.0
        vehicle_idx = 0
        
        for point in points:
            # Verifica se adicionar este ponto excede a capacidade
            if (current_demand + point.demand > self.vehicles[vehicle_idx].capacity
                and current_points):
                # Cria rota com pontos atuais
                routes.append(Route(
                    points=current_points.copy(),
                    vehicle=self.vehicles[vehicle_idx],
                    depot=depot
                ))
                current_points = []
                current_demand = 0.0
                vehicle_idx = min(vehicle_idx + 1, len(self.vehicles) - 1)
            
            current_points.append(point)
            current_demand += point.demand
        
        # Adiciona última rota
        if current_points:
            routes.append(Route(
                points=current_points,
                vehicle=self.vehicles[vehicle_idx],
                depot=depot
            ))
        
        return routes
    
    def invalidate_cache(self):
        """Invalida caches após modificação dos genes."""
        self._fitness = None
        self._routes = None
    
    def copy(self) -> 'Chromosome':
        """Cria uma cópia profunda do cromossomo."""
        new_chromosome = Chromosome(
            genes=self.genes.copy(),
            delivery_points=self.delivery_points,
            vehicles=self.vehicles,
            depot_index=self.depot_index
        )
        new_chromosome._fitness = self._fitness
        return new_chromosome
    
    def is_valid(self) -> bool:
        """
        Verifica se o cromossomo representa uma permutação válida.
        
        Returns:
            True se todos os pontos aparecem exatamente uma vez
        """
        expected = set(i for i in range(len(self.delivery_points)) 
                      if i != self.depot_index)
        return set(self.genes) == expected
    
    def __len__(self) -> int:
        return len(self.genes)
    
    def __repr__(self) -> str:
        return f"Chromosome({self.genes[:5]}..., fitness={self.fitness:.2f})"
    
    def __eq__(self, other: 'Chromosome') -> bool:
        if not isinstance(other, Chromosome):
            return False
        return self.genes == other.genes
    
    def __hash__(self) -> int:
        return hash(tuple(self.genes))

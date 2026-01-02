"""
Módulo de Cálculo de Distância Geodésica
========================================

Este módulo implementa funções para calcular a distância real entre
dois pontos geográficos usando suas coordenadas de latitude e longitude.

A principal função implementada é a Fórmula de Haversine, que calcula
a distância do grande círculo entre dois pontos na superfície de uma
esfera (a Terra), dado suas latitudes e longitudes.

Fórmula de Haversine:
--------------------
a = sin²(Δφ/2) + cos(φ1) * cos(φ2) * sin²(Δλ/2)
c = 2 * atan2(√a, √(1-a))
d = R * c

Onde:
- φ é a latitude
- λ é a longitude
- R é o raio da Terra (6.371 km em média)

Referências:
-----------
- Sinnott, R. W. (1984). Virtues of the Haversine. Sky and Telescope, 68(2), 159.
- Vincenty, T. (1975). Direct and Inverse Solutions of Geodesics on the Ellipsoid.

Autor: Aluno FIAP
Data: Dezembro 2024
"""

import math
from typing import Tuple, Optional
from enum import Enum


class DistanceMethod(Enum):
    """Métodos disponíveis para cálculo de distância."""
    EUCLIDEAN = "euclidean"
    HAVERSINE = "haversine"
    MANHATTAN = "manhattan"
    VINCENTY = "vincenty"


# Raio médio da Terra em quilômetros
EARTH_RADIUS_KM = 6371.0

# Raio médio da Terra em milhas
EARTH_RADIUS_MILES = 3958.8


def haversine_distance(lat1: float, lon1: float, 
                       lat2: float, lon2: float,
                       unit: str = 'km') -> float:
    """
    Calcula a distância entre dois pontos na Terra usando a fórmula de Haversine.
    
    A fórmula de Haversine determina a distância do grande círculo entre
    dois pontos em uma esfera dadas suas longitudes e latitudes.
    
    Esta é a fórmula mais adequada para calcular distâncias entre
    coordenadas geográficas (latitude/longitude) em aplicações de
    roteamento e logística.
    
    Args:
        lat1: Latitude do primeiro ponto em graus decimais
        lon1: Longitude do primeiro ponto em graus decimais
        lat2: Latitude do segundo ponto em graus decimais
        lon2: Longitude do segundo ponto em graus decimais
        unit: Unidade de medida ('km' para quilômetros, 'mi' para milhas)
    
    Returns:
        Distância entre os dois pontos na unidade especificada
    
    Example:
        >>> # Distância entre São Paulo e Rio de Janeiro
        >>> haversine_distance(-23.5505, -46.6333, -22.9068, -43.1729)
        357.89  # aproximadamente 358 km
    
    Note:
        - Latitude: valores entre -90 (Sul) e +90 (Norte)
        - Longitude: valores entre -180 (Oeste) e +180 (Leste)
        - Para o Brasil, latitudes são negativas (hemisfério Sul)
        - Para o Brasil, longitudes são negativas (oeste de Greenwich)
    """
    # Seleciona o raio da Terra baseado na unidade
    if unit == 'mi':
        R = EARTH_RADIUS_MILES
    else:
        R = EARTH_RADIUS_KM
    
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
    
    distance = R * c
    
    return distance


def euclidean_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calcula a distância euclidiana entre dois pontos.
    
    Esta é a distância em linha reta no plano cartesiano.
    Útil para coordenadas projetadas ou quando a curvatura da Terra
    pode ser ignorada (distâncias muito curtas).
    
    Args:
        x1: Coordenada X do primeiro ponto
        y1: Coordenada Y do primeiro ponto
        x2: Coordenada X do segundo ponto
        y2: Coordenada Y do segundo ponto
    
    Returns:
        Distância euclidiana entre os pontos
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def manhattan_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calcula a distância de Manhattan entre dois pontos.
    
    Também conhecida como distância de táxi ou L1, representa a
    distância percorrida seguindo apenas direções ortogonais
    (como em uma grade de ruas).
    
    Args:
        x1: Coordenada X do primeiro ponto
        y1: Coordenada Y do primeiro ponto
        x2: Coordenada X do segundo ponto
        y2: Coordenada Y do segundo ponto
    
    Returns:
        Distância de Manhattan entre os pontos
    """
    return abs(x2 - x1) + abs(y2 - y1)


def bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula o azimute (bearing) inicial entre dois pontos.
    
    O azimute é o ângulo medido em graus a partir do norte verdadeiro,
    no sentido horário, indicando a direção inicial de viagem.
    
    Args:
        lat1: Latitude do ponto de origem em graus
        lon1: Longitude do ponto de origem em graus
        lat2: Latitude do ponto de destino em graus
        lon2: Longitude do ponto de destino em graus
    
    Returns:
        Azimute em graus (0-360)
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlon = math.radians(lon2 - lon1)
    
    x = math.sin(dlon) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - \
        math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)
    
    initial_bearing = math.atan2(x, y)
    
    # Converte para graus e normaliza para 0-360
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    
    return compass_bearing


def destination_point(lat: float, lon: float, 
                      distance: float, bearing_deg: float) -> Tuple[float, float]:
    """
    Calcula o ponto de destino dado um ponto inicial, distância e direção.
    
    Args:
        lat: Latitude do ponto inicial em graus
        lon: Longitude do ponto inicial em graus
        distance: Distância em quilômetros
        bearing_deg: Direção em graus (0 = Norte, 90 = Leste)
    
    Returns:
        Tupla (latitude, longitude) do ponto de destino
    """
    R = EARTH_RADIUS_KM
    
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    bearing_rad = math.radians(bearing_deg)
    
    lat2_rad = math.asin(
        math.sin(lat_rad) * math.cos(distance / R) +
        math.cos(lat_rad) * math.sin(distance / R) * math.cos(bearing_rad)
    )
    
    lon2_rad = lon_rad + math.atan2(
        math.sin(bearing_rad) * math.sin(distance / R) * math.cos(lat_rad),
        math.cos(distance / R) - math.sin(lat_rad) * math.sin(lat2_rad)
    )
    
    return math.degrees(lat2_rad), math.degrees(lon2_rad)


class DistanceCalculator:
    """
    Calculador de distâncias configurável.
    
    Esta classe encapsula diferentes métodos de cálculo de distância
    e permite alternar entre eles facilmente.
    
    Attributes:
        method: Método de cálculo a ser utilizado
        unit: Unidade de medida para distâncias geodésicas
    
    Example:
        >>> calc = DistanceCalculator(method=DistanceMethod.HAVERSINE)
        >>> dist = calc.calculate(-23.55, -46.63, -22.90, -43.17)
        >>> print(f"Distância: {dist:.2f} km")
    """
    
    def __init__(self, method: DistanceMethod = DistanceMethod.HAVERSINE,
                 unit: str = 'km'):
        """
        Inicializa o calculador de distâncias.
        
        Args:
            method: Método de cálculo (HAVERSINE, EUCLIDEAN, MANHATTAN)
            unit: Unidade de medida ('km' ou 'mi')
        """
        self.method = method
        self.unit = unit
    
    def calculate(self, lat1: float, lon1: float, 
                  lat2: float, lon2: float) -> float:
        """
        Calcula a distância entre dois pontos.
        
        Para coordenadas geográficas (latitude/longitude), use HAVERSINE.
        Para coordenadas cartesianas, use EUCLIDEAN ou MANHATTAN.
        
        Args:
            lat1: Latitude/Y do primeiro ponto
            lon1: Longitude/X do primeiro ponto
            lat2: Latitude/Y do segundo ponto
            lon2: Longitude/X do segundo ponto
        
        Returns:
            Distância calculada
        """
        if self.method == DistanceMethod.HAVERSINE:
            return haversine_distance(lat1, lon1, lat2, lon2, self.unit)
        elif self.method == DistanceMethod.EUCLIDEAN:
            return euclidean_distance(lon1, lat1, lon2, lat2)
        elif self.method == DistanceMethod.MANHATTAN:
            return manhattan_distance(lon1, lat1, lon2, lat2)
        else:
            # Default para Haversine
            return haversine_distance(lat1, lon1, lat2, lon2, self.unit)
    
    def calculate_total_route(self, points: list, 
                              return_to_start: bool = True) -> float:
        """
        Calcula a distância total de uma rota.
        
        Args:
            points: Lista de tuplas (latitude, longitude)
            return_to_start: Se deve incluir retorno ao ponto inicial
        
        Returns:
            Distância total da rota
        """
        if len(points) < 2:
            return 0.0
        
        total = 0.0
        for i in range(len(points) - 1):
            total += self.calculate(
                points[i][0], points[i][1],
                points[i+1][0], points[i+1][1]
            )
        
        if return_to_start and len(points) > 2:
            total += self.calculate(
                points[-1][0], points[-1][1],
                points[0][0], points[0][1]
            )
        
        return total


# Instância global padrão usando Haversine
default_calculator = DistanceCalculator(method=DistanceMethod.HAVERSINE)


def calculate_distance(lat1: float, lon1: float, 
                       lat2: float, lon2: float,
                       method: DistanceMethod = DistanceMethod.HAVERSINE) -> float:
    """
    Função de conveniência para calcular distância.
    
    Args:
        lat1: Latitude do primeiro ponto
        lon1: Longitude do primeiro ponto
        lat2: Latitude do segundo ponto
        lon2: Longitude do segundo ponto
        method: Método de cálculo (padrão: HAVERSINE)
    
    Returns:
        Distância em quilômetros (para HAVERSINE) ou unidades (para outros)
    """
    calc = DistanceCalculator(method=method)
    return calc.calculate(lat1, lon1, lat2, lon2)


# =============================================================================
# Exemplos e Testes
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DO MÓDULO DE CÁLCULO DE DISTÂNCIA")
    print("=" * 60)
    
    # Coordenadas de teste (São Paulo)
    sp_centro = (-23.5505, -46.6333)  # Centro de SP
    guarulhos = (-23.4543, -46.5337)  # Aeroporto de Guarulhos
    campinas = (-22.9099, -47.0626)   # Campinas
    rio = (-22.9068, -43.1729)        # Rio de Janeiro
    
    print("\n1. Distâncias usando Haversine (em km):")
    print("-" * 40)
    
    dist_gru = haversine_distance(*sp_centro, *guarulhos)
    print(f"   SP Centro -> Guarulhos: {dist_gru:.2f} km")
    
    dist_camp = haversine_distance(*sp_centro, *campinas)
    print(f"   SP Centro -> Campinas: {dist_camp:.2f} km")
    
    dist_rio = haversine_distance(*sp_centro, *rio)
    print(f"   SP Centro -> Rio de Janeiro: {dist_rio:.2f} km")
    
    print("\n2. Comparação de métodos:")
    print("-" * 40)
    
    calc_haver = DistanceCalculator(DistanceMethod.HAVERSINE)
    calc_euclid = DistanceCalculator(DistanceMethod.EUCLIDEAN)
    
    print(f"   Haversine SP->Guarulhos: {calc_haver.calculate(*sp_centro, *guarulhos):.2f} km")
    print(f"   Euclidiana SP->Guarulhos: {calc_euclid.calculate(*sp_centro, *guarulhos):.4f} (graus)")
    
    print("\n3. Azimute (direção):")
    print("-" * 40)
    
    azimute = bearing(*sp_centro, *rio)
    print(f"   Direção SP -> Rio: {azimute:.1f}° (NE)")
    
    print("\n4. Distância total de uma rota:")
    print("-" * 40)
    
    rota = [sp_centro, guarulhos, campinas, sp_centro]
    total = calc_haver.calculate_total_route(rota, return_to_start=False)
    print(f"   SP -> Guarulhos -> Campinas -> SP: {total:.2f} km")
    
    print("\n" + "=" * 60)
    print("Testes concluídos!")

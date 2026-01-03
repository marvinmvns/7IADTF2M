"""
Script para filtrar hospitais por distância ao depósito.
Remove hospitais com distância > 190km da Farmácia Central - Sé.
Adiciona novos hospitais próximos para manter quantidade adequada.
"""
import json
import math
import os
from typing import List, Dict, Tuple


# Coordenadas do DEPÓSITO
DEPOT_LAT = -23.5505
DEPOT_LON = -46.6333
MAX_DISTANCE_KM = 190.0  # Distância máxima permitida
EARTH_RADIUS_KM = 6371.0


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula distância Haversine entre dois pontos."""
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    lon1_rad = math.radians(lon1)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_KM * c


def calculate_distance_to_depot(hospital: Dict) -> float:
    """Calcula distância do hospital ao depósito."""
    return haversine_distance(
        DEPOT_LAT, DEPOT_LON,
        hospital['latitude'], hospital['longitude']
    )


def filter_hospitals(hospitals: List[Dict], max_distance: float) -> Tuple[List[Dict], List[Tuple[Dict, float]]]:
    """
    Filtra hospitais pela distância ao depósito.

    Returns:
        Tuple (hospitais_válidos, lista_de_(hospital, distância)_removidos)
    """
    valid = []
    removed = []

    for hospital in hospitals:
        distance = calculate_distance_to_depot(hospital)
        if distance <= max_distance:
            valid.append((hospital, distance))
        else:
            removed.append((hospital, distance))

    # Ordena por distância
    valid.sort(key=lambda x: x[1])
    removed.sort(key=lambda x: x[1])

    return [h for h, d in valid], removed  # Mantém removidos como tuplas


# Hospitais próximos de São Paulo para adicionar (todos < 100km)
NOVOS_HOSPITAIS_CAPITAL = [
    {
        "id": 100,
        "name": "Hospital Santa Marcelina",
        "city": "São Paulo",
        "latitude": -23.521389,
        "longitude": -46.510278,
        "type": "privado",
        "priority": 1,
        "demand": 45.0
    },
    {
        "id": 101,
        "name": "Hospital São Camilo Pompeia",
        "city": "São Paulo",
        "latitude": -23.535000,
        "longitude": -46.682778,
        "type": "privado",
        "priority": 1,
        "demand": 45.0
    },
    {
        "id": 102,
        "name": "Hospital Santa Catarina",
        "city": "São Paulo",
        "latitude": -23.568056,
        "longitude": -46.646944,
        "type": "privado",
        "priority": 2,
        "demand": 28.0
    },
    {
        "id": 103,
        "name": "Hospital Samaritano",
        "city": "São Paulo",
        "latitude": -23.561111,
        "longitude": -46.670278,
        "type": "privado",
        "priority": 2,
        "demand": 28.0
    },
    {
        "id": 104,
        "name": "Hospital Nove de Julho",
        "city": "São Paulo",
        "latitude": -23.561667,
        "longitude": -46.672222,
        "type": "privado",
        "priority": 2,
        "demand": 28.0
    },
    {
        "id": 105,
        "name": "Hospital Sírio-Libanês",
        "city": "São Paulo",
        "latitude": -23.555833,
        "longitude": -46.670556,
        "type": "privado",
        "priority": 1,
        "demand": 45.0
    },
    {
        "id": 106,
        "name": "Hospital A.C.Camargo Cancer Center",
        "city": "São Paulo",
        "latitude": -23.551111,
        "longitude": -46.647500,
        "type": "privado",
        "priority": 1,
        "demand": 45.0
    },
    {
        "id": 107,
        "name": "Hospital Israelita Albert Einstein - Morumbi",
        "city": "São Paulo",
        "latitude": -23.599444,
        "longitude": -46.715556,
        "type": "privado",
        "priority": 1,
        "demand": 45.0
    },
    {
        "id": 108,
        "name": "Hospital das Clínicas FMUSP",
        "city": "São Paulo",
        "latitude": -23.555556,
        "longitude": -46.671111,
        "type": "público",
        "priority": 1,
        "demand": 45.0
    },
    {
        "id": 109,
        "name": "INCOR - Instituto do Coração",
        "city": "São Paulo",
        "latitude": -23.560278,
        "longitude": -46.668611,
        "type": "público",
        "priority": 1,
        "demand": 45.0
    }
]

NOVOS_HOSPITAIS_METROPOLITANA = [
    {
        "id": 110,
        "name": "Hospital Municipal de Osasco",
        "city": "Osasco",
        "latitude": -23.532778,
        "longitude": -46.791944,
        "type": "público",
        "priority": 2,
        "demand": 28.0
    },
    {
        "id": 111,
        "name": "Hospital e Maternidade Sino-Brasileiro",
        "city": "Osasco",
        "latitude": -23.532222,
        "longitude": -46.792222,
        "type": "privado",
        "priority": 2,
        "demand": 28.0
    },
    {
        "id": 112,
        "name": "Hospital Presidente",
        "city": "Santo André",
        "latitude": -23.663056,
        "longitude": -46.533056,
        "type": "privado",
        "priority": 2,
        "demand": 28.0
    },
    {
        "id": 113,
        "name": "Hospital Municipal Universitário de São Bernardo do Campo",
        "city": "São Bernardo do Campo",
        "latitude": -23.690833,
        "longitude": -46.564167,
        "type": "público",
        "priority": 2,
        "demand": 28.0
    },
    {
        "id": 114,
        "name": "Hospital e Maternidade Brasil",
        "city": "Santo André",
        "latitude": -23.654444,
        "longitude": -46.528611,
        "type": "privado",
        "priority": 3,
        "demand": 16.0
    },
    {
        "id": 115,
        "name": "Hospital Mário Covas",
        "city": "Santo André",
        "latitude": -23.654722,
        "longitude": -46.530833,
        "type": "público",
        "priority": 2,
        "demand": 28.0
    },
    {
        "id": 116,
        "name": "Hospital da Mulher Mauá",
        "city": "Mauá",
        "latitude": -23.668611,
        "longitude": -46.461389,
        "type": "público",
        "priority": 3,
        "demand": 16.0
    },
    {
        "id": 117,
        "name": "Hospital Nardini",
        "city": "Mauá",
        "latitude": -23.667500,
        "longitude": -46.461944,
        "type": "público",
        "priority": 3,
        "demand": 16.0
    },
    {
        "id": 118,
        "name": "Hospital São Luiz Anália Franco",
        "city": "São Paulo",
        "latitude": -23.560000,
        "longitude": -46.560000,
        "type": "privado",
        "priority": 2,
        "demand": 28.0
    },
    {
        "id": 119,
        "name": "Hospital Santa Paula",
        "city": "São Paulo",
        "latitude": -23.583889,
        "longitude": -46.652778,
        "type": "privado",
        "priority": 2,
        "demand": 28.0
    }
]


def main():
    """Processa o arquivo de hospitais."""
    # Lê arquivo original
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    json_path = os.path.join(data_dir, 'hospitais_sp.json')

    print("=" * 80)
    print("FILTRO DE HOSPITAIS POR DISTÂNCIA AO DEPÓSITO")
    print("=" * 80)
    print(f"\nDepósito: Farmácia Central - Sé")
    print(f"Coordenadas: ({DEPOT_LAT}, {DEPOT_LON})")
    print(f"Distância máxima: {MAX_DISTANCE_KM} km")
    print("=" * 80)

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    depot = data['depot']
    capital = data['capital']
    metropolitana = data['metropolitana']
    interior = data['interior']

    # Filtra cada categoria
    print("\n📊 ANÁLISE DE HOSPITAIS:")
    print("\n1. CAPITAL:")
    capital_valid, capital_removed = filter_hospitals(capital, MAX_DISTANCE_KM)
    print(f"   ✅ Válidos: {len(capital_valid)}")
    print(f"   ❌ Removidos: {len(capital_removed)}")

    print("\n2. METROPOLITANA:")
    metro_valid, metro_removed = filter_hospitals(metropolitana, MAX_DISTANCE_KM)
    print(f"   ✅ Válidos: {len(metro_valid)}")
    print(f"   ❌ Removidos: {len(metro_removed)}")

    print("\n3. INTERIOR:")
    interior_valid, interior_removed = filter_hospitals(interior, MAX_DISTANCE_KM)
    print(f"   ✅ Válidos: {len(interior_valid)}")
    print(f"   ❌ Removidos: {len(interior_removed)}")

    # Mostra removidos
    all_removed = capital_removed + metro_removed + interior_removed
    if all_removed:
        print(f"\n\n❌ HOSPITAIS REMOVIDOS (distância > {MAX_DISTANCE_KM} km):")
        print("=" * 80)
        for hospital, distance in all_removed:
            print(f"  {hospital['name']:50s} | {hospital['city']:20s} | {distance:6.1f} km")

    # Adiciona novos hospitais
    print("\n\n✅ ADICIONANDO NOVOS HOSPITAIS PRÓXIMOS:")
    print("=" * 80)

    # Valida novos hospitais também
    novos_capital_valid, _ = filter_hospitals(NOVOS_HOSPITAIS_CAPITAL, MAX_DISTANCE_KM)
    novos_metro_valid, _ = filter_hospitals(NOVOS_HOSPITAIS_METROPOLITANA, MAX_DISTANCE_KM)

    for h in novos_capital_valid:
        dist = calculate_distance_to_depot(h)
        print(f"  + {h['name']:50s} | {h['city']:20s} | {dist:6.1f} km")

    for h in novos_metro_valid:
        dist = calculate_distance_to_depot(h)
        print(f"  + {h['name']:50s} | {h['city']:20s} | {dist:6.1f} km")

    # Atualiza listas
    new_capital = capital_valid + novos_capital_valid
    new_metropolitana = metro_valid + novos_metro_valid
    new_interior = interior_valid  # Mantém apenas os válidos

    # Reordena IDs
    next_id = 1
    for h in new_capital:
        h['id'] = next_id
        next_id += 1

    for h in new_metropolitana:
        h['id'] = next_id
        next_id += 1

    for h in new_interior:
        h['id'] = next_id
        next_id += 1

    # Cria novo arquivo
    new_data = {
        "depot": depot,
        "capital": new_capital,
        "metropolitana": new_metropolitana,
        "interior": new_interior
    }

    # Salva
    output_path = os.path.join(data_dir, 'hospitais_sp.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)

    # Resumo final
    print("\n\n" + "=" * 80)
    print("📈 RESUMO FINAL:")
    print("=" * 80)
    print(f"  Capital:       {len(capital):3d} → {len(new_capital):3d} hospitais")
    print(f"  Metropolitana: {len(metropolitana):3d} → {len(new_metropolitana):3d} hospitais")
    print(f"  Interior:      {len(interior):3d} → {len(new_interior):3d} hospitais")
    print(f"  TOTAL:         {len(capital) + len(metropolitana) + len(interior):3d} → "
          f"{len(new_capital) + len(new_metropolitana) + len(new_interior):3d} hospitais")
    print(f"\n  Removidos: {len(all_removed)} hospitais (distância > {MAX_DISTANCE_KM} km)")
    print(f"  Adicionados: {len(novos_capital_valid) + len(novos_metro_valid)} hospitais próximos")
    print("=" * 80)
    print(f"\n✅ Arquivo atualizado: {output_path}")
    print("\n🎯 Todos os hospitais agora estão a menos de {MAX_DISTANCE_KM} km do depósito!")
    print("=" * 80)


if __name__ == "__main__":
    main()

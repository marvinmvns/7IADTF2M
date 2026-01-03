"""
Script de validação: verifica que todos os hospitais estão dentro do raio permitido.
"""
import json
import math
import os


DEPOT_LAT = -23.5505
DEPOT_LON = -46.6333
MAX_DISTANCE_KM = 190.0
EARTH_RADIUS_KM = 6371.0


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calcula distância Haversine."""
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


def main():
    """Valida distâncias."""
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    json_path = os.path.join(data_dir, 'hospitais_sp.json')

    print("\n" + "=" * 80)
    print("VALIDAÇÃO DE DISTÂNCIAS DE HOSPITAIS")
    print("=" * 80)

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    all_hospitals = []
    all_hospitals.extend(data['capital'])
    all_hospitals.extend(data['metropolitana'])
    all_hospitals.extend(data['interior'])

    print(f"\n📍 Depósito: Farmácia Central - Sé ({DEPOT_LAT}, {DEPOT_LON})")
    print(f"📏 Distância máxima permitida: {MAX_DISTANCE_KM} km")
    print(f"🏥 Total de hospitais: {len(all_hospitals)}")
    print("\n" + "=" * 80)

    violations = []
    max_dist = 0
    max_dist_hospital = None

    for hospital in all_hospitals:
        dist = haversine_distance(
            DEPOT_LAT, DEPOT_LON,
            hospital['latitude'], hospital['longitude']
        )

        if dist > max_dist:
            max_dist = dist
            max_dist_hospital = hospital

        if dist > MAX_DISTANCE_KM:
            violations.append((hospital, dist))

    if violations:
        print(f"\n❌ FALHA: {len(violations)} hospitais excedem {MAX_DISTANCE_KM} km!")
        print("=" * 80)
        for hospital, dist in sorted(violations, key=lambda x: x[1]):
            print(f"  {hospital['name']:50s} | {hospital['city']:20s} | {dist:6.1f} km")
        print("=" * 80)
        return False
    else:
        print(f"\n✅ SUCESSO: Todos os {len(all_hospitals)} hospitais estão dentro do raio!")
        print("=" * 80)
        print(f"\n📊 Estatísticas:")
        print(f"  - Hospital mais distante: {max_dist_hospital['name']}")
        print(f"  - Cidade: {max_dist_hospital['city']}")
        print(f"  - Distância: {max_dist:.1f} km")
        print(f"  - Margem de segurança: {MAX_DISTANCE_KM - max_dist:.1f} km")
        print("\n" + "=" * 80)

        # Mostra distribuição por categoria
        categories = {
            'capital': data['capital'],
            'metropolitana': data['metropolitana'],
            'interior': data['interior']
        }

        print(f"\n📋 Distribuição por categoria:")
        for cat_name, hospitals in categories.items():
            if hospitals:
                distances = [haversine_distance(DEPOT_LAT, DEPOT_LON, h['latitude'], h['longitude'])
                           for h in hospitals]
                avg_dist = sum(distances) / len(distances)
                min_dist = min(distances)
                max_dist_cat = max(distances)

                print(f"\n  {cat_name.upper():15s}: {len(hospitals):2d} hospitais")
                print(f"    Distância mínima: {min_dist:6.1f} km")
                print(f"    Distância média:  {avg_dist:6.1f} km")
                print(f"    Distância máxima: {max_dist_cat:6.1f} km")

        print("\n" + "=" * 80)
        print("✅ VALIDAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 80 + "\n")
        return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

"""
Dados de Hospitais do Estado de Sao Paulo
========================================

Este modulo carrega dados reais de hospitais (capital, metropolitana e interior)
exclusivamente a partir do arquivo JSON em data/hospitais_sp.json.
"""

from dataclasses import dataclass
import json
import os
from typing import List, Tuple, Optional, Dict


@dataclass
class HospitalData:
    """
    Dados de um hospital.

    Attributes:
        id: Identificador unico
        name: Nome do hospital
        city: Cidade
        latitude: Latitude (coordenada Y)
        longitude: Longitude (coordenada X)
        type: Tipo (publico/privado/indefinido/deposito)
        priority: Prioridade padrao de entregas (1=critico, 2=urgente, 3=regular)
        demand: Demanda media de medicamentos/insumos
    """
    id: int
    name: str
    city: str
    latitude: float
    longitude: float
    type: str
    priority: int = 3
    demand: float = 10.0


DATA_JSON_PATH = os.path.join(os.path.dirname(__file__), "hospitais_sp.json")

CIDADES_PROXIMAS = {
    "Campinas",
    "Jundiaí",
    "Sorocaba",
    "São José dos Campos",
    "Taubaté",
    "Santos",
    "São Vicente",
    "Guarujá",
    "Praia Grande",
    "Cubatão",
    "Atibaia",
    "Bragança Paulista",
    "Jacareí",
    "Caraguatatuba",
    "Americana",
}


def _normalize_city(city: str) -> str:
    return city.strip()


def _hospital_from_dict(data: Dict) -> HospitalData:
    """Cria HospitalData a partir de um dicionario."""
    return HospitalData(
        id=int(data["id"]),
        name=str(data["name"]),
        city=_normalize_city(str(data["city"])),
        latitude=float(data["latitude"]),
        longitude=float(data["longitude"]),
        type=str(data.get("type", "indefinido")),
        priority=int(data.get("priority", 3)),
        demand=float(data.get("demand", 10.0)),
    )


def _hospital_to_dict(hospital: HospitalData) -> Dict:
    """Serializa HospitalData para dicionario."""
    return {
        "id": hospital.id,
        "name": hospital.name,
        "city": hospital.city,
        "latitude": hospital.latitude,
        "longitude": hospital.longitude,
        "type": hospital.type,
        "priority": hospital.priority,
        "demand": hospital.demand,
    }


def _load_hospitals_json(path: str = DATA_JSON_PATH) -> Dict[str, List[HospitalData]]:
    """Carrega dados de hospitais a partir de JSON."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Arquivo de dados nao encontrado: {path}. "
            "Certifique-se de que data/hospitais_sp.json existe."
        )
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    depot = _hospital_from_dict(data["depot"])
    capital = [_hospital_from_dict(item) for item in data.get("capital", [])]
    metro = [_hospital_from_dict(item) for item in data.get("metropolitana", [])]
    interior = [_hospital_from_dict(item) for item in data.get("interior", [])]
    return {
        "depot": depot,
        "capital": capital,
        "metropolitana": metro,
        "interior": interior,
    }


def _save_hospitals_json(path: str = DATA_JSON_PATH):
    """Salva os dados atuais de hospitais em JSON."""
    data = {
        "depot": _hospital_to_dict(DEPOSITO_CENTRAL),
        "capital": [_hospital_to_dict(h) for h in HOSPITAIS_CAPITAL],
        "metropolitana": [_hospital_to_dict(h) for h in HOSPITAIS_METROPOLITANA],
        "interior": [_hospital_to_dict(h) for h in HOSPITAIS_INTERIOR],
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)


def _load_globals_from_json():
    data = _load_hospitals_json()
    return (
        data["depot"],
        data["capital"],
        data["metropolitana"],
        data["interior"],
    )


DEPOSITO_CENTRAL, HOSPITAIS_CAPITAL, HOSPITAIS_METROPOLITANA, HOSPITAIS_INTERIOR = (
    _load_globals_from_json()
)


# ============================================================================
# FUNCOES AUXILIARES
# ============================================================================

def get_all_hospitals() -> List[HospitalData]:
    """Retorna lista de todos os hospitais."""
    return HOSPITAIS_CAPITAL + HOSPITAIS_METROPOLITANA + HOSPITAIS_INTERIOR


def get_hospitals_by_region(region: str) -> List[HospitalData]:
    """
    Retorna hospitais de uma regiao especifica.

    Args:
        region: 'capital', 'metropolitana' ou 'interior'

    Returns:
        Lista de hospitais da regiao
    """
    regions = {
        "capital": HOSPITAIS_CAPITAL,
        "metropolitana": HOSPITAIS_METROPOLITANA,
        "interior": HOSPITAIS_INTERIOR,
    }
    return regions.get(region.lower(), [])


def get_hospitals_by_priority(priority: int) -> List[HospitalData]:
    """
    Retorna hospitais com prioridade especifica.

    Args:
        priority: 1 (critico), 2 (urgente) ou 3 (regular)

    Returns:
        Lista de hospitais com a prioridade especificada
    """
    all_hospitals = get_all_hospitals()
    return [h for h in all_hospitals if h.priority == priority]


def get_depot() -> HospitalData:
    """Retorna o deposito central."""
    return DEPOSITO_CENTRAL


def get_hospital_by_id(hospital_id: int) -> Optional[HospitalData]:
    """Busca um hospital pelo ID."""
    if hospital_id == DEPOSITO_CENTRAL.id:
        return DEPOSITO_CENTRAL
    for hospital in get_all_hospitals():
        if hospital.id == hospital_id:
            return hospital
    return None


def update_hospital_by_id(hospital_id: int, **fields) -> Optional[HospitalData]:
    """Atualiza dados de um hospital e salva em JSON."""
    if hospital_id == DEPOSITO_CENTRAL.id:
        return None
    all_lists = [HOSPITAIS_CAPITAL, HOSPITAIS_METROPOLITANA, HOSPITAIS_INTERIOR]
    for hospital_list in all_lists:
        for idx, hospital in enumerate(hospital_list):
            if hospital.id == hospital_id:
                updated = HospitalData(
                    id=hospital.id,
                    name=fields.get("name", hospital.name),
                    city=fields.get("city", hospital.city),
                    latitude=fields.get("latitude", hospital.latitude),
                    longitude=fields.get("longitude", hospital.longitude),
                    type=fields.get("type", hospital.type),
                    priority=int(fields.get("priority", hospital.priority)),
                    demand=float(fields.get("demand", hospital.demand)),
                )
                hospital_list[idx] = updated
                _save_hospitals_json()
                return updated
    return None


def remove_hospital_by_id(hospital_id: int) -> bool:
    """Remove um hospital pelo ID e salva em JSON."""
    if hospital_id == DEPOSITO_CENTRAL.id:
        return False
    all_lists = [HOSPITAIS_CAPITAL, HOSPITAIS_METROPOLITANA, HOSPITAIS_INTERIOR]
    for hospital_list in all_lists:
        for idx, hospital in enumerate(hospital_list):
            if hospital.id == hospital_id:
                del hospital_list[idx]
                _save_hospitals_json()
                return True
    return False


def _next_hospital_id() -> int:
    """Gera o proximo ID disponivel para um novo hospital."""
    ids = [DEPOSITO_CENTRAL.id] + [h.id for h in get_all_hospitals()]
    return max(ids) + 1 if ids else 1


def _infer_region_for_city(city: str) -> str:
    """Infere a regiao a partir da cidade informada."""
    normalized = _normalize_city(city).casefold()
    capital_cities = {_normalize_city(h.city).casefold() for h in HOSPITAIS_CAPITAL}
    metro_cities = {_normalize_city(h.city).casefold() for h in HOSPITAIS_METROPOLITANA}
    interior_cities = {_normalize_city(h.city).casefold() for h in HOSPITAIS_INTERIOR}
    if normalized in capital_cities:
        return "capital"
    if normalized in metro_cities:
        return "metropolitana"
    if normalized in interior_cities:
        return "interior"
    return "interior"


def add_hospital(
    name: str,
    city: str,
    latitude: float,
    longitude: float,
    type: str = "indefinido",
    priority: int = 3,
    demand: float = 10.0,
    region: Optional[str] = None,
) -> Optional[HospitalData]:
    """Adiciona um novo hospital e salva em JSON."""
    name = (name or "").strip()
    city = _normalize_city(city or "")
    if not name or not city:
        return None
    region_key = region.lower() if region else _infer_region_for_city(city)
    if region_key not in {"capital", "metropolitana", "interior"}:
        region_key = _infer_region_for_city(city)
    new_hospital = HospitalData(
        id=_next_hospital_id(),
        name=name,
        city=city,
        latitude=float(latitude),
        longitude=float(longitude),
        type=str(type),
        priority=int(priority),
        demand=float(demand),
    )
    if region_key == "capital":
        HOSPITAIS_CAPITAL.append(new_hospital)
    elif region_key == "metropolitana":
        HOSPITAIS_METROPOLITANA.append(new_hospital)
    else:
        HOSPITAIS_INTERIOR.append(new_hospital)
    _save_hospitals_json()
    return new_hospital


def create_scenario(
    num_hospitals: int = 20,
    include_depot: bool = True,
    region: str = "all",
) -> List[HospitalData]:
    """
    Cria um cenario de teste com numero especifico de hospitais.

    Args:
        num_hospitals: Numero de hospitais a incluir
        include_depot: Se deve incluir o deposito
        region: Regiao ('capital', 'metropolitana', 'interior', 'all')

    Returns:
        Lista de hospitais para o cenario
    """
    import random

    if region == "all":
        hospitals = get_all_hospitals()
    else:
        hospitals = get_hospitals_by_region(region)

    critical = [h for h in hospitals if h.priority == 1]
    others = [h for h in hospitals if h.priority != 1]

    selected = critical[: min(len(critical), num_hospitals // 3)]
    remaining = num_hospitals - len(selected)

    if remaining > 0 and others:
        random.shuffle(others)
        selected.extend(others[:remaining])

    result = []
    if include_depot:
        result.append(DEPOSITO_CENTRAL)

    result.extend(selected[:num_hospitals])

    return result


# ============================================================================
# CENARIOS PRE-DEFINIDOS
# ============================================================================

def _select_cities(hospitals: List[HospitalData], cities: set) -> List[HospitalData]:
    """Filtra hospitais por cidade mantendo a ordem da lista."""
    return [h for h in hospitals if h.city in cities]


def scenario_small() -> List[HospitalData]:
    """Cenario pequeno: 20 hospitais da regiao metropolitana."""
    metro = HOSPITAIS_CAPITAL + HOSPITAIS_METROPOLITANA
    selected = metro[:20]
    return [DEPOSITO_CENTRAL] + selected


def scenario_medium() -> List[HospitalData]:
    """Cenario medio: 40 hospitais (metropole + cidades ao lado)."""
    metro = HOSPITAIS_CAPITAL + HOSPITAIS_METROPOLITANA
    nearby = _select_cities(HOSPITAIS_INTERIOR, CIDADES_PROXIMAS)
    selected = metro[:20]
    remaining = 40 - len(selected)
    if remaining > 0:
        selected.extend(nearby[:remaining])
        remaining = 40 - len(selected)
    if remaining > 0:
        fallback = [h for h in HOSPITAIS_INTERIOR if h.city not in CIDADES_PROXIMAS]
        selected.extend(fallback[:remaining])
    return [DEPOSITO_CENTRAL] + selected


def scenario_large() -> List[HospitalData]:
    """Cenario grande: 80 hospitais (metropole + interior)."""
    metro = HOSPITAIS_CAPITAL + HOSPITAIS_METROPOLITANA
    selected = metro[:20]
    remaining = 80 - len(selected)
    if remaining > 0:
        selected.extend(HOSPITAIS_INTERIOR[:remaining])
        remaining = 80 - len(selected)
    if remaining > 0:
        selected.extend(metro[20 : 20 + remaining])
    return [DEPOSITO_CENTRAL] + selected


def scenario_critical_only() -> List[HospitalData]:
    """Cenario apenas com hospitais criticos (prioridade 1)."""
    critical = get_hospitals_by_priority(1)
    return [DEPOSITO_CENTRAL] + critical


if __name__ == "__main__":
    print("=" * 60)
    print("HOSPITAIS DO ESTADO DE SAO PAULO")
    print("=" * 60)

    print(f"\nDeposito Central: {DEPOSITO_CENTRAL.name}")
    print(f"  Coordenadas: ({DEPOSITO_CENTRAL.latitude}, {DEPOSITO_CENTRAL.longitude})")

    print(f"\nHospitais da Capital: {len(HOSPITAIS_CAPITAL)}")
    print(f"Hospitais da Regiao Metropolitana: {len(HOSPITAIS_METROPOLITANA)}")
    print(f"Hospitais do Interior: {len(HOSPITAIS_INTERIOR)}")
    print(f"Total: {len(get_all_hospitals())}")

    print("\n" + "-" * 60)
    print("HOSPITAIS CRITICOS (Prioridade 1):")
    for h in get_hospitals_by_priority(1):
        print(f"  - {h.name} ({h.city})")

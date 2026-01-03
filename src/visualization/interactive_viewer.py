"""
Módulo de Visualização Interativa
=================================

Este módulo fornece uma interface interativa completa para
visualizar e controlar o algoritmo genético.

Funcionalidades:
---------------
- Controle de execução (iniciar, pausar, parar)
- Ajuste de parâmetros em tempo real
- Visualização de múltiplas métricas
- Exportação de resultados
"""

import os
import sys
import time
import requests
from typing import List, Optional, Callable, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    import pygame
    from pygame import gfxdraw
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
try:
    import pygame_gui
    PYGAME_GUI_AVAILABLE = True
except ImportError:
    PYGAME_GUI_AVAILABLE = False

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.genetic_algorithm.chromosome import Chromosome, DeliveryPoint, Vehicle
from src.genetic_algorithm.population import Population, PopulationStats
from src.genetic_algorithm.genetic_algorithm import (
    GeneticAlgorithm, GAConfig, GAResult, ReplacementStrategy
)
from src.genetic_algorithm.selection import SelectionMethod
from src.genetic_algorithm.crossover import CrossoverMethod
from src.genetic_algorithm.mutation import MutationMethod
from src.genetic_algorithm.mutation import MutationMethod
from src.genetic_algorithm.fitness import FitnessType
from src.controllers.experiment_manager import ExperimentManager


# Função para buscar configurações da API
def get_api_defaults():
    """Busca configurações padrão da API."""
    try:
        response = requests.get("http://localhost:8000/config/defaults", timeout=1)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    # Fallback
    return {
        "num_vehicles": 3,
        "vehicle_capacity": 100.0,
        "vehicle_max_distance": 200.0,
        "vehicle_speed": 40.0,
        "w_distance": 1.0,
        "w_priority": 10.0,
        "w_capacity": 100.0,
        "w_autonomy": 100.0,
        "w_window": 50.0
    }

def get_api_config_options():
    """Busca opções de configuração da API."""
    try:
        response = requests.get("http://localhost:8000/config/options", timeout=1)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    # Fallback
    return {
        "logo_path": "assets/logo.png"
    }


# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (236, 238, 242)
DARK_GRAY = (64, 64, 64)
SOFT_BLACK = (24, 24, 24)
SOFT_GRAY = (110, 114, 120)
PANEL_BG = (245, 247, 250)
PANEL_BORDER = (210, 214, 220)
INPUT_BG = (255, 255, 255)
INPUT_BORDER = (190, 195, 202)
INPUT_ACTIVE = (0, 123, 255)
RED = (220, 53, 69)
GREEN = (40, 167, 69)
BLUE = (0, 123, 255)
YELLOW = (255, 193, 7)
CYAN = (23, 162, 184)
ORANGE = (255, 128, 0)

# Cores para rotas
ROUTE_COLORS = [
    (31, 119, 180),
    (255, 127, 14),
    (44, 160, 44),
    (214, 39, 40),
    (148, 103, 189),
    (140, 86, 75),
    (227, 119, 194),
    (127, 127, 127),
]

SELECTION_LABELS = {
    SelectionMethod.ROULETTE_WHEEL: "Roleta",
    SelectionMethod.TOURNAMENT: "Torneio",
    SelectionMethod.RANK: "Ranking",
    SelectionMethod.TRUNCATION: "Truncamento",
    SelectionMethod.ELITIST: "Elitista",
    SelectionMethod.SUS: "Amostragem universal (SUS)",
    SelectionMethod.BOLTZMANN: "Boltzmann",
    SelectionMethod.STEADY_STATE: "Estado estacionario",
}

CROSSOVER_LABELS = {
    CrossoverMethod.PMX: "PMX (mapeamento parcial)",
    CrossoverMethod.OX: "OX (ordem)",
    CrossoverMethod.CX: "CX (ciclo)",
    CrossoverMethod.AEX: "AEX (arestas alternadas)",
    CrossoverMethod.ERX: "ERX (recombinacao de arestas)",
    CrossoverMethod.SCX: "SCX (construtivo sequencial)",
    CrossoverMethod.OX2: "OX2 (baseado em ordem)",
    CrossoverMethod.POS: "POS (posicao)",
    CrossoverMethod.ARITHMETIC: "Aritmetico (Velocidades)",
    CrossoverMethod.HYBRID: "Hibrido (Rota + Velocidade)",
}

MUTATION_LABELS = {
    MutationMethod.SWAP: "Troca",
    MutationMethod.INVERSION: "Inversao",
    MutationMethod.SCRAMBLE: "Embaralhar",
    MutationMethod.INSERT: "Insercao",
    MutationMethod.DISPLACEMENT: "Deslocamento",
    MutationMethod.GAUSSIAN: "Gaussiana (Velocidades)",
    MutationMethod.HYBRID: "Hibrida (Rota + Velocidade)",
}

REPLACEMENT_LABELS = {
    ReplacementStrategy.GENERATIONAL: "Geracional",
    ReplacementStrategy.STEADY_STATE: "Estado estacionario",
    ReplacementStrategy.ELITIST: "Elitista",
}

FITNESS_LABELS = {
    FitnessType.DISTANCE_ONLY: "Distancia",
    FitnessType.WEIGHTED_MULTI: "Multiobjetivo ponderado",
    FitnessType.PENALTY_BASED: "Baseado em penalidade",
    FitnessType.PRIORITY_AWARE: "Prioridade",
}


class ViewerState(Enum):
    """Estados do visualizador."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"


@dataclass
class Button:
    """Representa um botão na interface."""
    x: int
    y: int
    width: int
    height: int
    text: str
    color: tuple
    hover_color: tuple
    action: Callable
    enabled: bool = True


 


class InteractiveViewer:
    """
    Visualizador interativo completo para o algoritmo genético.
    
    Fornece uma interface gráfica com:
    - Mapa de rotas
    - Gráficos de evolução
    - Controles de execução
    - Estatísticas detalhadas
    """
    
    def __init__(self, width: int = 1600, height: int = 900):
        """
        Inicializa o visualizador.

        Args:
            width: Largura da janela
            height: Altura da janela
        """
        if not PYGAME_AVAILABLE:
            raise ImportError("Pygame não está instalado")
        if not PYGAME_GUI_AVAILABLE:
            raise ImportError("pygame_gui não está instalado")

        self.width = width
        self.height = height

        # Busca configurações da API
        api_defaults = get_api_defaults()
        api_options = get_api_config_options()

        # Estado
        self.state = ViewerState.IDLE
        self.running = False

        # Dados
        self.delivery_points: List[DeliveryPoint] = []
        self.depot_index = 0
        self.best_chromosome: Optional[Chromosome] = None
        self.generation = 0

        # Histórico
        self.fitness_history: List[float] = []
        self.avg_fitness_history: List[float] = []
        self.diversity_history: List[float] = []

        # Configuração do AG
        self.ga_config: Optional[GAConfig] = None

        # Gerenciador de Experimentos
        try:
            self.experiment_manager = ExperimentManager()
        except Exception as e:
            print(f"CRITICAL ERROR initializing ExperimentManager: {e}")
            import traceback
            traceback.print_exc()
            self.experiment_manager = None

        self.current_exp_id = None
        self.ga: Optional[GeneticAlgorithm] = None

        # Valores padrão vindos da API
        self.vehicle_count = api_defaults.get("num_vehicles", 3)
        self.vehicle_capacity = api_defaults.get("vehicle_capacity", 100.0)
        self.vehicle_max_distance = api_defaults.get("vehicle_max_distance", 200.0)
        self.vehicle_speed = api_defaults.get("vehicle_speed", 40.0)

        # Interface
        self.screen = None
        self.clock = None
        self.fonts = {}
        self.buttons: List[Button] = []
        self.config_panel_rect = None
        self.ui_manager = None
        self.ui_panel = None
        self.ui_elements: Dict[str, Any] = {}
        self.ui_needs_sync = True
        self.active_tab = "Mapa"
        self.results_label_keys: List[str] = []
        self.km_initial = None
        self.km_final = None
        self.results_rect = None
        self.background_map_path: Optional[str] = None
        self.background_map_surface = None
        self.selected_hospital_id: Optional[int] = None

        # Logo path da API
        self.logo_path = api_options.get("logo_path", "assets/logo.png")
        
        # Cenários
        self.scenario_names: List[str] = []
        self.scenario_points: List[List[DeliveryPoint]] = []
        self.active_scenario_index = 0
        
        # Limites do mapa
        self.max_y = 1
        
        # Logo
        self.logo_surface = None

        # Gerenciador de Experimentos
        self.manager = self.experiment_manager
        self.current_experiment_id = None
        self.start_time = None
    
    def setup(self, delivery_points: Optional[List[DeliveryPoint]] = None,
              depot_index: int = 0,
              ga_config: Optional[GAConfig] = None,
              scenarios: Optional[List[tuple]] = None,
              initial_scenario: int = 0,
              vehicle_count: int = 3,
              background_map_path: Optional[str] = None):
        """
        Configura o visualizador com dados.
        
        Args:
            delivery_points: Pontos de entrega
            depot_index: Índice do depósito
            ga_config: Configuração do AG
            scenarios: Lista de cenários (nome, pontos de entrega)
            initial_scenario: Índice do cenário inicial
            vehicle_count: Número de veículos
            background_map_path: Caminho para PNG de mapa de fundo
        """
        self.vehicle_count = vehicle_count
        self.scenario_names = []
        self.scenario_points = []
        self.background_map_path = background_map_path
        
        if scenarios:
            self.scenario_names = [name for name, _ in scenarios]
            self.scenario_points = [points for _, points in scenarios]
            if self.scenario_points:
                self.active_scenario_index = max(
                    0, min(initial_scenario, len(self.scenario_points) - 1)
                )
                self.delivery_points = self.scenario_points[self.active_scenario_index]
            else:
                self.delivery_points = delivery_points or []
        else:
            self.delivery_points = delivery_points or []
        self.depot_index = depot_index
        self.ga_config = ga_config or GAConfig()
        self.selected_hospital_id = None
        
        # Calcula limites
        self._calculate_bounds()
    
    def _calculate_bounds(self):
        """Calcula limites das coordenadas."""
        if not self.delivery_points:
            return
        
        xs = [p.x for p in self.delivery_points]
        ys = [p.y for p in self.delivery_points]
        
        margin = 0.1
        x_range = max(xs) - min(xs)
        y_range = max(ys) - min(ys)
        
        self.min_x = min(xs) - x_range * margin
        self.max_x = max(xs) + x_range * margin
        self.min_y = min(ys) - y_range * margin
        self.max_y = max(ys) + y_range * margin
    
    def initialize(self):
        """Inicializa Pygame."""
        pygame.init()
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(
            "Saudelog - Inteligência em Distribuição de Medicamentos"
        )
        
        self.clock = pygame.time.Clock()
        self.ui_manager = pygame_gui.UIManager((self.width, self.height))
        
        # Fontes
        self.fonts = {
            'tiny': pygame.font.SysFont('DejaVu Sans', 11),
            'small': pygame.font.SysFont('DejaVu Sans', 13),
            'normal': pygame.font.SysFont('DejaVu Sans', 15),
            'medium': pygame.font.SysFont('DejaVu Sans', 17),
            'title': pygame.font.SysFont('DejaVu Sans', 24, bold=True),
            'subtitle': pygame.font.SysFont('DejaVu Sans', 18, bold=True),
            'section': pygame.font.SysFont('DejaVu Sans', 16, bold=True),
        }
        
        # Cria UI
        self._create_ui()
        self._reset_hospital_editor_ui()
        
        # Mapa de fundo (se houver)
        self.background_map_surface = None
        if self.background_map_path and os.path.exists(self.background_map_path):
            try:
                self.background_map_surface = pygame.image.load(
                    self.background_map_path
                ).convert()
            except pygame.error:
                self.background_map_surface = None
        
        # Carrega Logo Saudelog
        if os.path.exists(self.logo_path):
            try:
                logo_img = pygame.image.load(self.logo_path).convert_alpha()
                # Redimensiona mantendo proporção (ex: altura 80)
                aspect_ratio = logo_img.get_width() / logo_img.get_height()
                self.logo_surface = pygame.transform.smoothscale(logo_img, (int(80 * aspect_ratio), 80))
            except pygame.error:
                self.logo_surface = None
                
        self.running = True
    
    def _create_ui(self):
        """Cria UI com pygame_gui."""
        if self.ui_manager is None:
            return
        
        self.ui_elements = {}
        panel_rect = pygame.Rect(20, 90, 560, 770)
        self.ui_panel = pygame_gui.elements.UIPanel(
            relative_rect=panel_rect,
            starting_height=1,
            manager=self.ui_manager
        )
        self.config_panel_rect = panel_rect
        self.ui_needs_sync = True
        
        tab_y = 10
        tab_width = 130
        tab_height = 30
        tab_gap = 8
        tab_row_gap = 6
        tab_row2_y = tab_y + tab_height + tab_row_gap
        self.ui_elements["tab_config"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, tab_y, tab_width, tab_height),
            text="Mapa",
            manager=self.ui_manager,
            container=self.ui_panel
        )
        self.ui_elements["tab_ga"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10 + tab_width + tab_gap, tab_y, tab_width, tab_height),
            text="Algoritmo",
            manager=self.ui_manager,
            container=self.ui_panel
        )
        self.ui_elements["tab_vehicles"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10 + 2 * (tab_width + tab_gap), tab_y, tab_width, tab_height),
            text="Veículos",
            manager=self.ui_manager,
            container=self.ui_panel
        )
        self.ui_elements["tab_results"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10 + 3 * (tab_width + tab_gap), tab_y, tab_width, tab_height),
            text="Resultados",
            manager=self.ui_manager,
            container=self.ui_panel
        )
        self.ui_elements["tab_weights"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, tab_row2_y, tab_width, tab_height),
            text="Pesos",
            manager=self.ui_manager,
            container=self.ui_panel
        )
        self.ui_elements["tab_llm"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10 + tab_width + tab_gap, tab_row2_y, tab_width, tab_height),
            text="LLM",
            manager=self.ui_manager,
            container=self.ui_panel
        )
        
        content_y = tab_row2_y + tab_height + 8
        content_height = panel_rect.height - content_y - 10
        config_container = pygame_gui.core.UIContainer(
            relative_rect=pygame.Rect(10, content_y, panel_rect.width - 20, content_height),
            manager=self.ui_manager,
            container=self.ui_panel
        )
        vehicles_container = pygame_gui.core.UIContainer(
            relative_rect=pygame.Rect(10, content_y, panel_rect.width - 20, content_height),
            manager=self.ui_manager,
            container=self.ui_panel
        )
        results_container = pygame_gui.core.UIContainer(
            relative_rect=pygame.Rect(10, content_y, panel_rect.width - 20, content_height),
            manager=self.ui_manager,
            container=self.ui_panel
        )
        ga_container = pygame_gui.core.UIContainer(
            relative_rect=pygame.Rect(10, content_y, panel_rect.width - 20, content_height),
            manager=self.ui_manager,
            container=self.ui_panel
        )
        llm_container = pygame_gui.core.UIContainer(
            relative_rect=pygame.Rect(10, content_y, panel_rect.width - 20, content_height),
            manager=self.ui_manager,
            container=self.ui_panel
        )
        weights_container = pygame_gui.core.UIContainer(
            relative_rect=pygame.Rect(10, content_y, panel_rect.width - 20, content_height),
            manager=self.ui_manager,
            container=self.ui_panel
        )
        vehicles_container.hide()
        results_container.hide()
        ga_container.hide()
        llm_container.hide()
        weights_container.hide()
        self.ui_elements["container_config"] = config_container
        self.ui_elements["container_vehicles"] = vehicles_container
        self.ui_elements["container_results"] = results_container
        self.ui_elements["container_ga"] = ga_container
        self.ui_elements["container_llm"] = llm_container
        self.ui_elements["container_weights"] = weights_container
        
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(16, 6, 260, 20),
            text="Cenário e hospitais",
            manager=self.ui_manager,
            container=config_container
        )
        
        left_x = 16
        right_x = 288
        row_height = 58
        input_width = 240
        input_height = 32
        start_y = 32
        map_center_x = (panel_rect.width - 20 - input_width) // 2
        map_list_x = 16
        map_list_width = panel_rect.width - 20 - 32
        
        def add_label(text: str, x: int, y: int, container):
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(x, y, input_width, 20),
                text=text,
                manager=self.ui_manager,
                container=container
            )
        
        def add_text_entry(name: str, x: int, row: int, container):
            y = start_y + row * row_height
            entry = pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect(x, y + 20, input_width, input_height),
                manager=self.ui_manager,
                container=container
            )
            self.ui_elements[name] = entry
        
        def add_dropdown(name: str, options: List[str], x: int, row: int, container):
            y = start_y + row * row_height
            dropdown = pygame_gui.elements.UIDropDownMenu(
                options_list=options,
                starting_option=options[0],
                relative_rect=pygame.Rect(x, y + 20, input_width, input_height),
                manager=self.ui_manager,
                container=container
            )
            self.ui_elements[name] = dropdown
        
        left_row = 0
        if self.scenario_names:
            add_label("Cenário", map_center_x, start_y + left_row * row_height, config_container)
            add_dropdown("scenario", self.scenario_names, map_center_x, left_row, config_container)
            left_row += 1
        
        hospitals_y = start_y + left_row * row_height + 6
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(map_list_x, hospitals_y, map_list_width, 20),
            text="Hospitais",
            manager=self.ui_manager,
            container=config_container
        )
        hospitals_y += 24
        list_height = 120
        self.ui_elements["hospital_list"] = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect(
                map_list_x,
                hospitals_y,
                map_list_width,
                list_height
            ),
            item_list=[],
            manager=self.ui_manager,
            container=config_container
        )

        edit_y = hospitals_y + list_height + 12
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(map_list_x, edit_y, map_list_width, 20),
            text="Editar/adicionar hospital",
            manager=self.ui_manager,
            container=config_container
        )
        edit_y += 24
        self.ui_elements["hospital_id_label"] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(map_list_x, edit_y, map_list_width, 20),
            text="ID: -",
            manager=self.ui_manager,
            container=config_container
        )
        edit_y += 26

        edit_row_height = 48
        field_width = (map_list_width - 12) // 2
        col1_x = map_list_x
        col2_x = map_list_x + field_width + 12

        def add_edit_label(text: str, x: int, y: int):
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(x, y, field_width, 20),
                text=text,
                manager=self.ui_manager,
                container=config_container
            )

        def add_edit_entry(name: str, x: int, y: int, width: int = field_width):
            entry = pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect(x, y + 20, width, input_height),
                manager=self.ui_manager,
                container=config_container
            )
            self.ui_elements[name] = entry

        def add_edit_dropdown(name: str, options: List[str], x: int, y: int):
            dropdown = pygame_gui.elements.UIDropDownMenu(
                options_list=options,
                starting_option=options[0],
                relative_rect=pygame.Rect(x, y + 20, field_width, input_height),
                manager=self.ui_manager,
                container=config_container
            )
            self.ui_elements[name] = dropdown

        add_edit_label("Nome", col1_x, edit_y)
        add_edit_entry("hospital_name", col1_x, edit_y, map_list_width)
        edit_y += edit_row_height

        add_edit_label("Cidade", col1_x, edit_y)
        add_edit_entry("hospital_city", col1_x, edit_y, map_list_width)
        edit_y += edit_row_height

        add_edit_label("Tipo", col1_x, edit_y)
        add_edit_dropdown("hospital_type", ["público", "privado", "indefinido"], col1_x, edit_y)
        add_edit_label("Prioridade", col2_x, edit_y)
        add_edit_dropdown("hospital_priority", ["1", "2", "3"], col2_x, edit_y)
        edit_y += edit_row_height

        add_edit_label("Demanda", col1_x, edit_y)
        add_edit_entry("hospital_demand", col1_x, edit_y)
        add_edit_label("Latitude", col2_x, edit_y)
        add_edit_entry("hospital_latitude", col2_x, edit_y)
        edit_y += edit_row_height

        add_edit_label("Longitude", col1_x, edit_y)
        add_edit_entry("hospital_longitude", col1_x, edit_y)
        self.ui_elements["btn_hospital_save"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(col2_x, edit_y + 20, field_width, input_height),
            text="Salvar hospital",
            manager=self.ui_manager,
            container=config_container
        )
        edit_y += edit_row_height
        self.ui_elements["btn_hospital_add"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(col1_x, edit_y, field_width, input_height),
            text="Adicionar hospital",
            manager=self.ui_manager,
            container=config_container
        )
        self.ui_elements["btn_hospital_delete"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(col2_x, edit_y, field_width, input_height),
            text="Excluir hospital",
            manager=self.ui_manager,
            container=config_container
        )
        edit_y += edit_row_height
        
        self.results_rect = pygame.Rect(
            panel_rect.x + 10,
            panel_rect.y + content_y,
            panel_rect.width - 20,
            content_height
        )
        self.results_label_keys = []
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(16, 10, 200, 20),
            text="Resultados",
            manager=self.ui_manager,
            container=results_container
        )
        results_y = 34
        results_x = 16
        results_width = panel_rect.width - 52
        for key, text in [
            ("result_fitness", "Melhor Fitness: -"),
            ("result_distance", "Distância Total: -"),
            ("result_routes", "Rotas: -"),
            ("result_generation", "Geração: -"),
            ("result_km_initial", "KM Inicial: -"),
            ("result_km_final", "KM Final: -"),
            ("result_km_diff", "Diferença: -"),
        ]:
            self.ui_elements[key] = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(results_x, results_y, results_width, 20),
                text=text,
                manager=self.ui_manager,
                container=results_container
            )
            self.results_label_keys.append(key)
            results_y += 20

        ga_fields = [
            ("Fitness", "fitness", "dropdown", [FITNESS_LABELS.get(m, m.value) for m in FitnessType]),
            ("Seleção", "selection", "dropdown", [SELECTION_LABELS.get(m, m.value) for m in SelectionMethod]),
            ("Torneio", "tournament", "text", None),
            ("Crossover Op", "crossover_method", "dropdown", [CROSSOVER_LABELS.get(m, m.value) for m in CrossoverMethod]),
            ("Crossover", "crossover_rate", "text", None),
            ("Mutação Op", "mutation_method", "dropdown", [MUTATION_LABELS.get(m, m.value) for m in MutationMethod]),
            ("Mutação", "mutation_rate", "text", None),
            ("População", "population", "text", None),
            ("Gerações", "generations", "text", None),
            ("Reposição", "replacement", "dropdown", [REPLACEMENT_LABELS.get(m, m.value) for m in ReplacementStrategy]),
            ("Elites", "elites", "text", None),
            ("Estagnação", "stagnation", "text", None),
            ("Heurística", "heuristic", "text", None),
        ]
        for index, (label, key, kind, options) in enumerate(ga_fields):
            col_x = left_x if index % 2 == 0 else right_x
            row = index // 2
            add_label(label, col_x, start_y + row * row_height, ga_container)
            if kind == "dropdown":
                add_dropdown(key, options, col_x, row, ga_container)
            else:
                add_text_entry(key, col_x, row, ga_container)
        
        vehicles_container_width = vehicles_container.relative_rect.width
        vehicle_field_width = 230
        vehicle_gap = 24
        vehicle_row_height = 72
        vehicle_label_height = 18
        vehicle_input_height = 34
        vehicle_start_y = 24
        vehicle_total_width = vehicle_field_width * 2 + vehicle_gap
        vehicle_left = int((vehicles_container_width - vehicle_total_width) / 2)
        vehicle_right = vehicle_left + vehicle_field_width + vehicle_gap
        
        def add_vehicle_field(name: str, label: str, x: int, row: int):
            y = vehicle_start_y + row * vehicle_row_height
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(x, y, vehicle_field_width, vehicle_label_height),
                text=label,
                manager=self.ui_manager,
                container=vehicles_container
            )
            entry = pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect(
                    x,
                    y + vehicle_label_height + 6,
                    vehicle_field_width,
                    vehicle_input_height
                ),
                manager=self.ui_manager,
                container=vehicles_container
            )
            self.ui_elements[name] = entry
        
        add_vehicle_field("vehicles", "Qtd. Veículos", vehicle_left, 0)
        add_vehicle_field("vehicle_capacity", "Capacidade", vehicle_right, 0)
        add_vehicle_field("vehicle_max_distance", "Autonomia (km)", vehicle_left, 1)
        add_vehicle_field("vehicle_speed", "Velocidade (km/h)", vehicle_right, 1)

        # Aba de Pesos de Fitness
        weights_start_y = 24
        weights_row_height = 72
        weights_field_width = 230
        weights_gap = 24
        weights_left = int((panel_rect.width - 20 - (weights_field_width * 2 + weights_gap)) / 2)
        weights_right = weights_left + weights_field_width + weights_gap

        def add_weight_field(name: str, label: str, x: int, row: int, default_val: float):
            y = weights_start_y + row * weights_row_height
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(x, y, weights_field_width, 18),
                text=label,
                manager=self.ui_manager,
                container=weights_container
            )
            entry = pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect(x, y + 24, weights_field_width, 34),
                manager=self.ui_manager,
                container=weights_container
            )
            entry.set_text(str(default_val))
            self.ui_elements[name] = entry

        # Busca valores padrão da API
        api_defaults_weights = get_api_defaults()

        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(16, 6, 400, 20),
            text="Pesos da Função de Fitness Multi-Objetivo",
            manager=self.ui_manager,
            container=weights_container
        )

        add_weight_field("w_distance", "Peso Distância", weights_left, 0, api_defaults_weights.get("w_distance", 1.0))
        add_weight_field("w_priority", "Peso Prioridade", weights_right, 0, api_defaults_weights.get("w_priority", 10.0))
        add_weight_field("w_capacity", "Penalidade Capacidade", weights_left, 1, api_defaults_weights.get("w_capacity", 100.0))
        add_weight_field("w_autonomy", "Penalidade Autonomia", weights_right, 1, api_defaults_weights.get("w_autonomy", 100.0))
        add_weight_field("w_window", "Penalidade Janela Tempo", weights_left, 2, api_defaults_weights.get("w_window", 50.0))

        # Parâmetros Condicionais de Seleção
        add_weight_field("truncation_threshold", "Limiar Truncamento", weights_right, 2, 0.5)
        add_weight_field("boltzmann_temp", "Temp. Boltzmann", weights_left, 3, 100.0)
        add_weight_field("steady_state_ratio", "Taxa Steady State", weights_right, 3, 0.2)

        llm_title_y = 6
        llm_list_y = 34
        llm_list_width = panel_rect.width - 20 - 32
        llm_list_height = content_height - llm_list_y - 10
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(16, llm_title_y, llm_list_width, 20),
            text="LLM - Combinador LLM",
            manager=self.ui_manager,
            container=llm_container
        )
        self.ui_elements["llm_list"] = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect(16, llm_list_y, llm_list_width, llm_list_height),
            item_list=[],
            manager=self.ui_manager,
            container=llm_container
        )
        
        buttons_x = 600
        buttons_y = self.height - 50
        self.ui_elements["btn_start"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(buttons_x, buttons_y, 140, 40),
            text="Iniciar",
            manager=self.ui_manager
        )
        self.ui_elements["btn_pause"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(buttons_x + 156, buttons_y, 140, 40),
            text="Pausar",
            manager=self.ui_manager
        )
        self.ui_elements["btn_stop"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(buttons_x + 312, buttons_y, 140, 40),
            text="Parar",
            manager=self.ui_manager
        )
        self.ui_elements["btn_reset"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(buttons_x + 468, buttons_y, 140, 40),
            text="Resetar",
            manager=self.ui_manager
        )
        self.ui_elements["btn_export"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(buttons_x + 624, buttons_y, 160, 40),
            text="Exportar Mapa",
            manager=self.ui_manager
        )
        
        self._sync_ui_values()

    def _get_container(self, name: str):
        """Retorna container pelo nome."""
        if name == "config":
            return self.ui_elements.get("container_config")
        if name == "vehicles":
            return self.ui_elements.get("container_vehicles")
        if name == "results":
            return self.ui_elements.get("container_results")
        if name == "ga":
            return self.ui_elements.get("container_ga")
        if name == "weights":
            return self.ui_elements.get("container_weights")
        if name == "llm":
            return self.ui_elements.get("container_llm")
        return None

    def _show_tab(self, name: str):
        """Mostra a aba selecionada."""
        self.active_tab = name
        config_container = self._get_container("config")
        vehicles_container = self._get_container("vehicles")
        results_container = self._get_container("results")
        ga_container = self._get_container("ga")
        weights_container = self._get_container("weights")
        llm_container = self._get_container("llm")
        if config_container is not None:
            config_container.show() if name == "Mapa" else config_container.hide()
        if vehicles_container is not None:
            vehicles_container.show() if name == "Veículos" else vehicles_container.hide()
        if results_container is not None:
            results_container.show() if name == "Resultados" else results_container.hide()
        if ga_container is not None:
            ga_container.show() if name == "Algoritmo" else ga_container.hide()
        if weights_container is not None:
            weights_container.show() if name == "Pesos" else weights_container.hide()
        if llm_container is not None:
            llm_container.show() if name == "LLM" else llm_container.hide()
    
    def run(self):
        """Loop principal do visualizador."""
        if not self.running:
            self.initialize()
        
        while self.running:
            self._handle_events()
            time_delta = self.clock.tick(30) / 1000.0
            if self.ui_manager is not None:
                self.ui_manager.update(time_delta)
            self._update()
            self._render()
        
        pygame.quit()
    
    def _handle_events(self):
        """Processa eventos do Pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self._toggle_pause()
                elif event.key == pygame.K_r:
                    self._reset()
            
            if self.ui_manager is not None:
                self.ui_manager.process_events(event)
            
            if event.type == pygame.USEREVENT and self.ui_manager is not None:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.ui_elements.get("btn_start"):
                        self._start_evolution()
                    elif event.ui_element == self.ui_elements.get("btn_pause"):
                        self._toggle_pause()
                    elif event.ui_element == self.ui_elements.get("btn_stop"):
                        self._stop_evolution()
                    elif event.ui_element == self.ui_elements.get("btn_reset"):
                        self._reset()
                    elif event.ui_element == self.ui_elements.get("btn_export"):
                        self._export_map()
                    elif event.ui_element == self.ui_elements.get("tab_config"):
                        self._show_tab("Mapa")
                    elif event.ui_element == self.ui_elements.get("tab_vehicles"):
                        self._show_tab("Veículos")
                    elif event.ui_element == self.ui_elements.get("tab_results"):
                        self._show_tab("Resultados")
                    elif event.ui_element == self.ui_elements.get("tab_ga"):
                        self._show_tab("Algoritmo")
                    elif event.ui_element == self.ui_elements.get("tab_weights"):
                        self._show_tab("Pesos")
                    elif event.ui_element == self.ui_elements.get("tab_llm"):
                        self._show_tab("LLM")
                    elif event.ui_element == self.ui_elements.get("btn_hospital_save"):
                        self._save_hospital_from_ui()
                    elif event.ui_element == self.ui_elements.get("btn_hospital_add"):
                        self._add_hospital_from_ui()
                    elif event.ui_element == self.ui_elements.get("btn_hospital_delete"):
                        self._delete_selected_hospital()
                
                if event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    self._apply_text_entry(event.ui_element, event.text)
                
                if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    self._apply_dropdown(event.ui_element, event.text)
                
                if event.user_type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                    if event.ui_element == self.ui_elements.get("hospital_list"):
                        self._on_hospital_selected(event.text)
                
    
    def _is_point_in_rect(self, point: tuple, button: Button) -> bool:
        """Verifica se ponto está dentro do botão."""
        return (button.x <= point[0] <= button.x + button.width and
                button.y <= point[1] <= button.y + button.height)
    
    def _update(self):
        """Atualiza estado do visualizador."""
        if self.state == ViewerState.RUNNING and self.ga is not None:
            # Executa uma geração
            self._evolve_one_generation()
    
    def _evolve_one_generation(self):
        """Executa uma geração do AG."""
        if self.ga is None:
            return
        
        # Evolui
        self.ga._evolve_generation()
        self.ga.population.evaluate(self.ga.fitness_func.evaluate)
        
        # Atualiza melhor
        current_best = self.ga.population.get_best()
        if self.ga._best_ever is None or current_best.fitness < self.ga._best_ever.fitness:
            self.ga._best_ever = current_best.copy()
            self.ga._stagnation_counter = 0
        else:
            self.ga._stagnation_counter += 1
        
        self.best_chromosome = self.ga._best_ever
        self.generation = self.ga.population.generation
        self.ga.population.generation += 1
        
        if self.km_initial is None and self.best_chromosome is not None:
            self.km_initial = self._calculate_total_distance(self.best_chromosome)
        if self.best_chromosome is not None:
            self.km_final = self._calculate_total_distance(self.best_chromosome)
        
        # Atualiza histórico
        stats = self.ga.population.calculate_stats()
        self.fitness_history.append(stats.best_fitness)
        self.avg_fitness_history.append(stats.avg_fitness)
        self.diversity_history.append(stats.diversity)
        
        # Verifica parada (respeita apenas o número de gerações configurado)
        if self.generation >= self.ga_config.max_generations:
            self._stop_evolution()
    
    def _render(self):
        """Renderiza a interface."""
        self.screen.fill(WHITE)
        self._update_ui_state()
        
        # Componentes
        self._draw_header()
        self._draw_map()
        self._draw_fitness_graph()
        self._draw_statistics()
        
        self._draw_results_panel()
        
        if self.ui_manager is not None:
            self.ui_manager.draw_ui(self.screen)
        
        pygame.display.flip()
    
    def _draw_header(self):
        """Desenha cabeçalho."""
        x_offset = 20
        # Logo se disponível
        if self.logo_surface:
            self.screen.blit(self.logo_surface, (30, 10))
            x_offset = 30 + self.logo_surface.get_width() + 20
            text_y_start = 10 + (self.logo_surface.get_height() // 2) - 30
        else:
            text_y_start = 15

        # Título
        title = self.fonts['title'].render(
            "Saudelog - Inteligência em Distribuição",
            True, SOFT_BLACK
        )
        self.screen.blit(title, (x_offset, text_y_start))
        
        # Subtítulo
        subtitle = self.fonts['medium'].render(
            "Otimização de Rotas Hospitalares - São Paulo",
            True, SOFT_GRAY
        )
        self.screen.blit(subtitle, (x_offset, text_y_start + 35))
        
        if self.scenario_names:
            scenario_text = self.fonts['normal'].render(
                f"Cenário: {self.scenario_names[self.active_scenario_index]}",
                True, SOFT_GRAY
            )
            # Move para baixo para não sobrepor com o logo
            self.screen.blit(scenario_text, (20, 100))
        
        # Status
        status_colors = {
            ViewerState.IDLE: GRAY,
            ViewerState.RUNNING: GREEN,
            ViewerState.PAUSED: YELLOW,
            ViewerState.FINISHED: BLUE,
        }
        status_texts = {
            ViewerState.IDLE: "Aguardando",
            ViewerState.RUNNING: "Executando",
            ViewerState.PAUSED: "Pausado",
            ViewerState.FINISHED: "Concluído",
        }
        
        status = self.fonts['subtitle'].render(
            f"Status: {status_texts[self.state]} | Geração: {self.generation}",
            True, status_colors[self.state]
        )
        self.screen.blit(status, (self.width - 420, 20))

    def _draw_map(self):
        """Desenha mapa de rotas."""
        map_x, map_y = 600, 90
        map_width, map_height = 980, 540
        
        # Fundo
        pygame.draw.rect(self.screen, WHITE,
                        (map_x, map_y, map_width, map_height),
                        border_radius=12)
        pygame.draw.rect(self.screen, PANEL_BORDER,
                        (map_x, map_y, map_width, map_height), 2,
                        border_radius=12)
        
        # Título
        title = self.fonts['section'].render("Mapa de Rotas", True, SOFT_BLACK)
        self.screen.blit(title, (map_x + 12, map_y + 10))
        
        # Desenha rotas
        if self.best_chromosome is not None:
            routes = self.best_chromosome.get_routes()
            self._draw_routes_on_map(routes, map_x, map_y, map_width, map_height)
        
        # Desenha hospitais
        self._draw_hospitals_on_map(map_x, map_y, map_width, map_height)
        self._draw_legend(map_x, map_y, map_width, map_height)
    
    def _normalize_to_map(self, x: float, y: float,
                          map_x: int, map_y: int,
                          map_width: int, map_height: int) -> tuple:
        """Normaliza coordenadas para o mapa."""
        margin = 40
        
        norm_x = (x - self.min_x) / (self.max_x - self.min_x)
        norm_y = (y - self.min_y) / (self.max_y - self.min_y)
        
        screen_x = int(map_x + margin + norm_x * (map_width - 2 * margin))
        screen_y = int(map_y + margin + (1 - norm_y) * (map_height - 2 * margin))
        
        return screen_x, screen_y
    
    def _draw_hospitals_on_map(self, map_x: int, map_y: int,
                                map_width: int, map_height: int):
        """Desenha hospitais no mapa."""
        for i, point in enumerate(self.delivery_points):
            x, y = self._normalize_to_map(
                point.x, point.y, map_x, map_y, map_width, map_height
            )
            
            # Cor e tamanho baseados na prioridade
            if i == self.depot_index:
                color = BLUE
                radius = 12
                # Desenha quadrado para depósito
                pygame.draw.rect(self.screen, color,
                               (x - radius, y - radius, radius * 2, radius * 2))
                pygame.draw.rect(self.screen, BLACK,
                               (x - radius, y - radius, radius * 2, radius * 2), 2)
            else:
                priority = getattr(point, 'priority', 3)
                if priority == 1:
                    color = RED
                    radius = 10
                elif priority == 2:
                    color = ORANGE
                    radius = 8
                else:
                    color = GREEN
                    radius = 6
                
                pygame.draw.circle(self.screen, color, (x, y), radius)
                pygame.draw.circle(self.screen, BLACK, (x, y), radius, 2)
    
    def _draw_routes_on_map(self, routes: list, map_x: int, map_y: int,
                            map_width: int, map_height: int):
        """Desenha rotas no mapa."""
        for i, route in enumerate(routes):
            color = ROUTE_COLORS[i % len(ROUTE_COLORS)]
            
            points = []
            
            # Depósito
            depot_pos = self._normalize_to_map(
                route.depot.x, route.depot.y,
                map_x, map_y, map_width, map_height
            )
            points.append(depot_pos)
            
            # Pontos
            for point in route.points:
                pos = self._normalize_to_map(
                    point.x, point.y,
                    map_x, map_y, map_width, map_height
                )
                points.append(pos)
            
            # Volta
            points.append(depot_pos)
            
            # Desenha
            if len(points) > 1:
                pygame.draw.lines(self.screen, color, False, points, 3)
    
    def _draw_fitness_graph(self):
        """Desenha gráfico de fitness."""
        graph_x = 600
        graph_y = 640
        graph_width = 980
        graph_height = 200
        
        # Fundo
        pygame.draw.rect(self.screen, PANEL_BG,
                        (graph_x, graph_y, graph_width, graph_height),
                        border_radius=12)
        pygame.draw.rect(self.screen, PANEL_BORDER,
                        (graph_x, graph_y, graph_width, graph_height), 2,
                        border_radius=12)
        
        # Título
        title = self.fonts['section'].render("Evolução do Fitness", True, SOFT_BLACK)
        self.screen.blit(title, (graph_x + 12, graph_y + 10))

        # Legenda
        legend_y = graph_y + graph_height - 22
        legend_x = graph_x + 20
        pygame.draw.line(self.screen, GREEN, (legend_x, legend_y), (legend_x + 24, legend_y), 3)
        legend_text = self.fonts['tiny'].render("Melhor fitness", True, SOFT_GRAY)
        self.screen.blit(legend_text, (legend_x + 30, legend_y - 6))
        legend_x += 150
        pygame.draw.line(self.screen, BLUE, (legend_x, legend_y), (legend_x + 24, legend_y), 3)
        legend_text = self.fonts['tiny'].render("Fitness médio", True, SOFT_GRAY)
        self.screen.blit(legend_text, (legend_x + 30, legend_y - 6))
        
        if len(self.fitness_history) < 2:
            return
        
        # Área de plotagem
        plot_x = graph_x + 60
        plot_y = graph_y + 50
        plot_width = graph_width - 90
        plot_height = graph_height - 80
        
        # Eixos
        pygame.draw.line(self.screen, SOFT_BLACK,
                        (plot_x, plot_y), (plot_x, plot_y + plot_height), 2)
        pygame.draw.line(self.screen, SOFT_BLACK,
                        (plot_x, plot_y + plot_height),
                        (plot_x + plot_width, plot_y + plot_height), 2)
        
        # Escala
        min_f = min(self.fitness_history)
        max_f = max(max(self.fitness_history), max(self.avg_fitness_history))
        f_range = max_f - min_f if max_f != min_f else 1
        
        # Zoom automático quando as curvas convergem
        window_size = min(30, len(self.fitness_history))
        if window_size >= 5 and self.avg_fitness_history:
            recent_best = self.fitness_history[-window_size:]
            recent_avg = self.avg_fitness_history[-window_size:]
            recent_min = min(min(recent_best), min(recent_avg))
            recent_max = max(max(recent_best), max(recent_avg))
            recent_range = recent_max - recent_min
            last_gap = abs(recent_best[-1] - recent_avg[-1])
            if recent_range > 0 and last_gap <= recent_range * 0.2:
                zoom_padding = recent_range * 0.15
                min_f = recent_min - zoom_padding
                max_f = recent_max + zoom_padding
                f_range = max_f - min_f if max_f != min_f else 1
        
        # Plota melhor fitness
        points = []
        for i, f in enumerate(self.fitness_history):
            x = plot_x + int(i / len(self.fitness_history) * plot_width)
            y = plot_y + plot_height - int((f - min_f) / f_range * plot_height)
            points.append((x, y))
        
        if len(points) > 1:
            pygame.draw.lines(self.screen, GREEN, False, points, 2)
        
        # Plota média
        avg_points = []
        for i, f in enumerate(self.avg_fitness_history):
            x = plot_x + int(i / len(self.avg_fitness_history) * plot_width)
            y = plot_y + plot_height - int((f - min_f) / f_range * plot_height)
            avg_points.append((x, y))
        
        if len(avg_points) > 1:
            pygame.draw.lines(self.screen, BLUE, False, avg_points, 2)
        
        # Labels
        max_label = self.fonts['tiny'].render(f"{max_f:.0f}", True, SOFT_GRAY)
        self.screen.blit(max_label, (plot_x - 50, plot_y - 5))
        
        min_label = self.fonts['tiny'].render(f"{min_f:.0f}", True, SOFT_GRAY)
        self.screen.blit(min_label, (plot_x - 50, plot_y + plot_height - 10))
    
    def _draw_statistics(self):
        """Desenha estatísticas."""
        stats_x = 20
        stats_y = 90
        stats_width = 560
        stats_height = 770
        self.config_panel_rect = pygame.Rect(stats_x, stats_y, stats_width, stats_height)
        
        # Fundo
        pygame.draw.rect(self.screen, PANEL_BG,
                        (stats_x, stats_y, stats_width, stats_height),
                        border_radius=12)
        pygame.draw.rect(self.screen, PANEL_BORDER,
                        (stats_x, stats_y, stats_width, stats_height), 2,
                        border_radius=12)
        
        if self.state in [ViewerState.IDLE, ViewerState.FINISHED] and self.best_chromosome is None:
            return
        
        # Título
        title = self.fonts['section'].render("Estatísticas", True, SOFT_BLACK)
        self.screen.blit(title, (stats_x + 12, stats_y + 10))
        
        y = stats_y + 44
        line_height = 24
        
        # Informações gerais
        info = [
            f"Geração Atual: {self.generation}",
            f"Total de Hospitais: {len(self.delivery_points) - 1}",
            f"Veículos: {self.vehicle_count}",
        ]
        
        if self.best_chromosome is not None:
            routes = self.best_chromosome.get_routes()
            total_dist = sum(r.total_distance for r in routes)
            
            info.extend([
                f"Melhor Fitness: {self.best_chromosome.fitness:.2f}",
                f"Distância Total: {total_dist:.2f} km",
                f"Número de Rotas: {len(routes)}",
                "",
                "Detalhes das Rotas:",
            ])
            
            for i, route in enumerate(routes):
                info.append(f"  Rota {i+1}: {len(route.points)} hospitais, "
                           f"{route.total_distance:.1f} km")
        
        if self.fitness_history:
            info.extend([
                "",
                f"Melhor Fitness Histórico: {min(self.fitness_history):.2f}",
            ])
        
        for line in info:
            text = self.fonts['normal'].render(line, True, SOFT_BLACK)
            self.screen.blit(text, (stats_x + 18, y))
            y += line_height

    
    
    def _draw_legend(self, map_x: int, map_y: int, map_width: int, map_height: int):
        """Desenha legenda dentro do mapa."""
        legend_width = 260
        legend_height = 110
        legend_x = map_x + 16
        legend_y = map_y + map_height - legend_height - 16
        
        pygame.draw.rect(self.screen, WHITE,
                        (legend_x, legend_y, legend_width, legend_height),
                        border_radius=10)
        pygame.draw.rect(self.screen, PANEL_BORDER,
                        (legend_x, legend_y, legend_width, legend_height),
                        1, border_radius=10)
        
        title = self.fonts['small'].render("Legenda", True, SOFT_BLACK)
        self.screen.blit(title, (legend_x + 10, legend_y + 8))
        
        y = legend_y + 30
        items = [
            (BLUE, "■", "Depósito Central"),
            (RED, "●", "Hospital Crítico"),
            (ORANGE, "●", "Hospital Urgente"),
            (GREEN, "●", "Hospital Regular"),
        ]
        
        for color, symbol, text in items:
            symbol_text = self.fonts['small'].render(symbol, True, color)
            self.screen.blit(symbol_text, (legend_x + 12, y))
            label = self.fonts['small'].render(text, True, SOFT_BLACK)
            self.screen.blit(label, (legend_x + 30, y))
            y += 18

    def _draw_results_panel(self):
        """Desenha painel de resultados com fundo branco."""
        if self.results_rect is None or self.active_tab != "Resultados":
            return
        pygame.draw.rect(self.screen, WHITE, self.results_rect, border_radius=10)
        pygame.draw.rect(self.screen, PANEL_BORDER, self.results_rect, 1, border_radius=10)

    
    # ========================================================================
    # Ações dos botões
    # ========================================================================
    
    def _start_evolution(self):
        """Inicia a evolução."""
        if self.state == ViewerState.IDLE or self.state == ViewerState.FINISHED:
            self._apply_all_ui_values()
            self._show_tab("Resultados")
            # Cria novo AG
            from src.genetic_algorithm.genetic_algorithm import GeneticAlgorithm
            vehicles = self._create_vehicles()
            self.ga = GeneticAlgorithm(
                config=self.ga_config,
                delivery_points=self.delivery_points,
                vehicles=vehicles,
                depot_index=self.depot_index
            )
            
            # Inicializa população
            self.ga.population.initialize_heuristic(
                self.ga_config.heuristic_init_ratio
            )
            self.ga.population.evaluate(self.ga.fitness_func.evaluate)
            self.ga._best_ever = self.ga.population.get_best().copy()
            
            self.best_chromosome = self.ga._best_ever
            self.generation = 0
            
            # Inicializa histórico com o fitness inicial real
            initial_stats = self.ga.population.calculate_stats()
            print(f"DEBUG: Initial Stats Captured: {initial_stats.best_fitness}")
            self.fitness_history = [initial_stats.best_fitness]
            self.avg_fitness_history = [initial_stats.avg_fitness]
            self.diversity_history = [initial_stats.diversity]
            
            self.km_initial = self._calculate_total_distance(self.best_chromosome)
            self.km_final = None
            
            self.state = ViewerState.RUNNING
            self.start_time = time.time()
            
            # Cria registro do experimento
            if self.manager:
                try:
                    # Busca valores dos campos de pesos (se existirem na UI)
                    try:
                        w_dist = float(self.ui_elements.get("w_distance", None).get_text() or 1.0) if self.ui_elements.get("w_distance") else 1.0
                        w_prio = float(self.ui_elements.get("w_priority", None).get_text() or 10.0) if self.ui_elements.get("w_priority") else 10.0
                        w_cap = float(self.ui_elements.get("w_capacity", None).get_text() or 100.0) if self.ui_elements.get("w_capacity") else 100.0
                        w_auto = float(self.ui_elements.get("w_autonomy", None).get_text() or 100.0) if self.ui_elements.get("w_autonomy") else 100.0
                        w_wind = float(self.ui_elements.get("w_window", None).get_text() or 50.0) if self.ui_elements.get("w_window") else 50.0
                        trunc_thresh = float(self.ui_elements.get("truncation_threshold", None).get_text() or 0.5) if self.ui_elements.get("truncation_threshold") else 0.5
                        boltz_temp = float(self.ui_elements.get("boltzmann_temp", None).get_text() or 100.0) if self.ui_elements.get("boltzmann_temp") else 100.0
                        steady_ratio = float(self.ui_elements.get("steady_state_ratio", None).get_text() or 0.2) if self.ui_elements.get("steady_state_ratio") else 0.2
                    except:
                        # Fallback para valores da API
                        api_defaults = get_api_defaults()
                        w_dist = api_defaults.get("w_distance", 1.0)
                        w_prio = api_defaults.get("w_priority", 10.0)
                        w_cap = api_defaults.get("w_capacity", 100.0)
                        w_auto = api_defaults.get("w_autonomy", 100.0)
                        w_wind = api_defaults.get("w_window", 50.0)
                        trunc_thresh = 0.5
                        boltz_temp = 100.0
                        steady_ratio = 0.2

                    # Monta config em dict (similar ao que a API recebe)
                    # Precisamos serializar Enums
                    config_dict = {
                        "population_size": self.ga_config.population_size,
                        "max_generations": self.ga_config.max_generations,
                        "crossover_rate": self.ga_config.crossover_rate,
                        "mutation_rate": self.ga_config.mutation_rate,
                        "selection_method": self.ga_config.selection_method.value,
                        "crossover_method": self.ga_config.crossover_method.value,
                        "mutation_method": self.ga_config.mutation_method.value,
                        "replacement_strategy": self.ga_config.replacement_strategy.value,
                        "fitness_type": self.ga_config.fitness_type.value,
                        "elite_size": self.ga_config.elite_size,
                        "tournament_size": self.ga_config.tournament_size,
                        "stagnation_limit": self.ga_config.stagnation_limit,
                        "heuristic_init_ratio": self.ga_config.heuristic_init_ratio,
                        "num_vehicles": self.vehicle_count,
                        "vehicle_capacity": self.vehicle_capacity,
                        "vehicle_max_distance": self.vehicle_max_distance,
                        "vehicle_speed": self.vehicle_speed,
                        "scenario": self.scenario_names[self.active_scenario_index] if self.scenario_names else "custom",
                        # Pesos vindos da UI
                        "w_distance": w_dist,
                        "w_priority": w_prio,
                        "w_capacity": w_cap,
                        "w_autonomy": w_auto,
                        "w_window": w_wind,
                        "truncation_threshold": trunc_thresh,
                        "boltzmann_temperature": boltz_temp,
                        "steady_state_ratio": steady_ratio
                    }
                    exp = self.manager.create_experiment(config_dict)
                    self.current_experiment_id = exp.id
                    # Atualiza status para running imediatamente
                    self.manager.update_experiment_result(exp.id, {}, 0, 0, 0, status="running")
                    print(f"Experimento visual iniciado: ID {exp.id}")
                except Exception as e:
                    print(f"Erro ao criar experimento: {e}")
        
        elif self.state == ViewerState.PAUSED:
            self.state = ViewerState.RUNNING
    
    def _toggle_pause(self):
        """Alterna pausa."""
        if self.state == ViewerState.RUNNING:
            self.state = ViewerState.PAUSED
        elif self.state == ViewerState.PAUSED:
            self.state = ViewerState.RUNNING
    
    def _stop_evolution(self):
        """Para a evolução."""
        if self.state in [ViewerState.RUNNING, ViewerState.PAUSED]:
            self.state = ViewerState.FINISHED
        
        # Salva resultados finais
        if self.manager and self.current_experiment_id and self.ga:
            try:
                duration = time.time() - (self.start_time or time.time())
                
                # Prepara detalhes das rotas (igual ao que a API faz)
                routes_info = []
                if self.ga.get_best_solution():
                    for r in self.ga.get_best_solution().get_routes():
                        if hasattr(r, 'points'):
                            points_ids = [p.id for p in r.points]
                            routes_info.append({
                                "vehicle_id": r.vehicle.id,
                                "distance": r.total_distance,
                                "demand": r.total_demand,
                                "points": points_ids
                            })

                result_data = {
                    "best_fitness": float(self.ga.get_best_solution().fitness),
                    "generations_run": self.generation,
                    "execution_time": duration,
                    "routes": routes_info,
                    "initial_fitness": self.fitness_history[0] if self.fitness_history else 0,
                    "convergence_generation": self.ga._stagnation_counter
                }

                self.manager.complete_experiment(
                    experiment_id=self.current_experiment_id,
                    result=result_data
                )
                print(f"Experimento visual salvo: ID {self.current_experiment_id}")
                self.current_experiment_id = None
            except Exception as e:
                print(f"Erro ao salvar resultados: {e}")
                import traceback
                traceback.print_exc()
    
    def _reset(self):
        """Reseta o visualizador."""
        self.state = ViewerState.IDLE
        self.ga = None
        self.best_chromosome = None
        self.generation = 0
        self.fitness_history = []
        self.avg_fitness_history = []
        self.diversity_history = []
        self.ui_needs_sync = True
        self.km_initial = None
        self.km_final = None

    def _create_vehicles(self) -> List[Vehicle]:
        """Cria lista de veículos."""
        return [
            Vehicle(
                id=i,
                capacity=self.vehicle_capacity,
                max_distance=self.vehicle_max_distance,
                speed=self.vehicle_speed
            )
            for i in range(1, self.vehicle_count + 1)
        ]

    def _calculate_total_distance(self, chromosome: Chromosome) -> float:
        """Calcula distância total da solução."""
        routes = chromosome.get_routes()
        return sum(route.total_distance for route in routes)

    def _can_edit_config(self) -> bool:
        """Verifica se a configuração pode ser editada."""
        return self.state in [ViewerState.IDLE, ViewerState.FINISHED]

    def _sync_ui_values(self):
        """Sincroniza valores da UI com o estado atual."""
        if not self.ui_elements:
            return
        def set_text(name: str, value: str):
            entry = self.ui_elements.get(name)
            if entry is not None:
                entry.set_text(value)
        
        def set_dropdown(name: str, value: str):
            dropdown = self.ui_elements.get(name)
            if dropdown is not None:
                if hasattr(dropdown, "set_selected_option"):
                    dropdown.set_selected_option(value)
                else:
                    dropdown.selected_option = value
        
        if self.scenario_names:
            set_dropdown("scenario", self.scenario_names[self.active_scenario_index])
            self._update_hospital_list()
        
        set_text("vehicles", f"{self.vehicle_count}")
        set_text("vehicle_capacity", f"{self.vehicle_capacity:.2f}")
        set_text("vehicle_max_distance", f"{self.vehicle_max_distance:.2f}")
        set_text("vehicle_speed", f"{self.vehicle_speed:.2f}")
        set_text("population", f"{self.ga_config.population_size}")
        set_text("generations", f"{self.ga_config.max_generations}")
        set_text("tournament", f"{self.ga_config.tournament_size}")
        set_text("heuristic", f"{self.ga_config.heuristic_init_ratio:.2f}")
        
        set_text("crossover_rate", f"{self.ga_config.crossover_rate:.2f}")
        set_text("mutation_rate", f"{self.ga_config.mutation_rate:.2f}")
        set_text("elites", f"{self.ga_config.elite_size}")
        set_text("stagnation", f"{self.ga_config.stagnation_limit}")
        
        set_dropdown(
            "selection",
            self._label_for_enum(self.ga_config.selection_method, SELECTION_LABELS)
        )
        set_dropdown(
            "crossover_method",
            self._label_for_enum(self.ga_config.crossover_method, CROSSOVER_LABELS)
        )
        set_dropdown(
            "mutation_method",
            self._label_for_enum(self.ga_config.mutation_method, MUTATION_LABELS)
        )
        set_dropdown(
            "replacement",
            self._label_for_enum(self.ga_config.replacement_strategy, REPLACEMENT_LABELS)
        )
        set_dropdown(
            "fitness",
            self._label_for_enum(self.ga_config.fitness_type, FITNESS_LABELS)
        )

    def _update_ui_state(self):
        """Atualiza estado (habilitado/desabilitado) da UI."""
        if not self.ui_elements:
            return
        editable = self._can_edit_config()
        for key, element in self.ui_elements.items():
            if key.startswith("btn_"):
                continue
            if key.startswith("result_"):
                continue
            if editable:
                element.enable()
            else:
                element.disable()
        if editable and self.ui_needs_sync:
            focused = self.ui_manager.get_focus_set() if self.ui_manager else None
            focused = focused or []
            typing = any(
                isinstance(el, pygame_gui.elements.UITextEntryLine)
                for el in focused
            )
            if not typing:
                self._sync_ui_values()
                self.ui_needs_sync = False
        self._set_hospital_editor_state(editable)
        self._update_results_ui()

    def _update_results_ui(self):
        """Atualiza rótulos de resultados."""
        if not self.results_label_keys:
            return
        if self.best_chromosome is None:
            return
        routes = self.best_chromosome.get_routes()
        total_dist = sum(r.total_distance for r in routes)
        km_initial = self.km_initial if self.km_initial is not None else total_dist
        km_final = self.km_final if self.km_final is not None else total_dist
        labels = {
            "result_fitness": f"Melhor Fitness: {self.best_chromosome.fitness:.2f}",
            "result_distance": f"Distância Total: {total_dist:.2f} km",
            "result_routes": f"Rotas: {len(routes)}",
            "result_generation": f"Geração: {self.generation}",
            "result_km_initial": f"KM Inicial: {km_initial:.2f}",
            "result_km_final": f"KM Final: {km_final:.2f}",
            "result_km_diff": f"Diferença: {km_final - km_initial:.2f} km",
        }
        for key in self.results_label_keys:
            label = self.ui_elements.get(key)
            if label is not None:
                label.set_text(labels.get(key, "-"))

    def _get_hospital_names(self) -> List[str]:
        """Retorna lista de hospitais do cenário atual."""
        names = []
        for i, point in enumerate(self.delivery_points):
            if i == self.depot_index:
                continue
            names.append(f"{i}. {point.name}")
        return names

    def _update_hospital_list(self):
        """Atualiza lista de hospitais na aba Mapa."""
        list_widget = self.ui_elements.get("hospital_list")
        if list_widget is None:
            return
        names = self._get_hospital_names()
        if hasattr(list_widget, "set_item_list"):
            list_widget.set_item_list(names)
        else:
            list_widget.item_list = names

    def _set_dropdown_value(self, name: str, value: str):
        """Define valor de um dropdown com compatibilidade entre versões."""
        dropdown = self.ui_elements.get(name)
        if dropdown is None:
            return
        if hasattr(dropdown, "set_selected_option"):
            dropdown.set_selected_option(value)
        else:
            dropdown.selected_option = value

    def _label_for_enum(self, enum_value, label_map):
        """Retorna o rótulo para um valor de enum (objeto ou string)."""
        # Se for Enum e estiver no mapa
        if enum_value in label_map:
            return label_map[enum_value]
        
        # Se for string, tenta encontrar correspondência no mapa
        if isinstance(enum_value, str):
            for key, label in label_map.items():
                if hasattr(key, 'value') and key.value == enum_value:
                    return label
            return enum_value
            
        # Fallback
        return getattr(enum_value, 'value', str(enum_value))

    def _enum_from_label(self, label: str, label_map: Dict, enum_cls: Enum):
        """Retorna enum a partir do rótulo em PT-BR."""
        for enum_value, label_text in label_map.items():
            if label_text == label:
                return enum_value
        try:
            return enum_cls(label)
        except ValueError:
            return None

    def _set_hospital_editor_state(self, editable: bool):
        """Habilita ou desabilita o editor de hospital."""
        fields_enabled = editable
        selection_enabled = editable and self.selected_hospital_id is not None
        for key in [
            "hospital_name",
            "hospital_city",
            "hospital_type",
            "hospital_priority",
            "hospital_demand",
            "hospital_latitude",
            "hospital_longitude",
        ]:
            element = self.ui_elements.get(key)
            if element is None:
                continue
            if fields_enabled:
                element.enable()
            else:
                element.disable()
        for key in ["btn_hospital_save", "btn_hospital_delete"]:
            element = self.ui_elements.get(key)
            if element is None:
                continue
            if selection_enabled:
                element.enable()
            else:
                element.disable()
        add_button = self.ui_elements.get("btn_hospital_add")
        if add_button is not None:
            add_button.enable() if editable else add_button.disable()

    def _reset_hospital_editor_ui(self):
        """Limpa o editor de hospital."""
        self.selected_hospital_id = None
        id_label = self.ui_elements.get("hospital_id_label")
        if id_label is not None:
            id_label.set_text("ID: -")
        for key in [
            "hospital_name",
            "hospital_city",
            "hospital_demand",
            "hospital_latitude",
            "hospital_longitude",
        ]:
            entry = self.ui_elements.get(key)
            if entry is not None:
                entry.set_text("")
        self._set_dropdown_value("hospital_type", "indefinido")
        self._set_dropdown_value("hospital_priority", "3")
        self._set_hospital_editor_state(self._can_edit_config())

    def _on_hospital_selected(self, item_text: str):
        """Carrega dados do hospital selecionado."""
        try:
            index = int(item_text.split(".", 1)[0].strip())
        except (ValueError, IndexError):
            return
        if index == self.depot_index or index >= len(self.delivery_points):
            return
        point = self.delivery_points[index]
        self.selected_hospital_id = point.id
        self._populate_hospital_editor(point)
        self._set_hospital_editor_state(self._can_edit_config())

    def _populate_hospital_editor(self, point: DeliveryPoint):
        """Preenche editor com dados do hospital."""
        try:
            from data.hospitais_sp import get_hospital_by_id
        except Exception:
            get_hospital_by_id = None
        hospital = get_hospital_by_id(point.id) if get_hospital_by_id else None
        name = hospital.name if hospital else point.name
        city = hospital.city if hospital else ""
        hosp_type = hospital.type if hospital else "indefinido"
        priority = hospital.priority if hospital else point.priority
        demand = hospital.demand if hospital else point.demand
        latitude = hospital.latitude if hospital else point.y
        longitude = hospital.longitude if hospital else point.x

        id_label = self.ui_elements.get("hospital_id_label")
        if id_label is not None:
            id_label.set_text(f"ID: {point.id}")
        entry = self.ui_elements.get("hospital_name")
        if entry is not None:
            entry.set_text(name)
        entry = self.ui_elements.get("hospital_city")
        if entry is not None:
            entry.set_text(city)
        entry = self.ui_elements.get("hospital_demand")
        if entry is not None:
            entry.set_text(f"{demand:.2f}")
        entry = self.ui_elements.get("hospital_latitude")
        if entry is not None:
            entry.set_text(f"{latitude:.6f}")
        entry = self.ui_elements.get("hospital_longitude")
        if entry is not None:
            entry.set_text(f"{longitude:.6f}")
        self._set_dropdown_value("hospital_type", hosp_type)
        self._set_dropdown_value("hospital_priority", str(priority))

    def _save_hospital_from_ui(self):
        """Salva alterações do hospital selecionado."""
        if not self._can_edit_config() or self.selected_hospital_id is None:
            return
        try:
            name = self.ui_elements["hospital_name"].get_text().strip()
            city = self.ui_elements["hospital_city"].get_text().strip()
            hosp_type = self.ui_elements["hospital_type"].selected_option
            priority = int(self.ui_elements["hospital_priority"].selected_option)
            demand = float(self.ui_elements["hospital_demand"].get_text())
            latitude = float(self.ui_elements["hospital_latitude"].get_text())
            longitude = float(self.ui_elements["hospital_longitude"].get_text())
        except (KeyError, ValueError):
            return
        try:
            from data.hospitais_sp import update_hospital_by_id
        except Exception:
            update_hospital_by_id = None
        updated = None
        if update_hospital_by_id:
            updated = update_hospital_by_id(
                self.selected_hospital_id,
                name=name,
                city=city,
                type=hosp_type,
                priority=priority,
                demand=demand,
                latitude=latitude,
                longitude=longitude,
            )
        for points in [self.delivery_points] + self.scenario_points:
            for point in points:
                if point.id == self.selected_hospital_id:
                    point.name = name
                    point.priority = priority
                    point.demand = demand
                    point.y = latitude
                    point.x = longitude
        if updated:
            self._calculate_bounds()
        self._update_hospital_list()

    def _add_hospital_from_ui(self):
        """Adiciona um novo hospital com os dados do formulário."""
        if not self._can_edit_config():
            return
        try:
            name = self.ui_elements["hospital_name"].get_text().strip()
            city = self.ui_elements["hospital_city"].get_text().strip()
            hosp_type = self.ui_elements["hospital_type"].selected_option
            priority = int(self.ui_elements["hospital_priority"].selected_option)
            demand = float(self.ui_elements["hospital_demand"].get_text())
            latitude = float(self.ui_elements["hospital_latitude"].get_text())
            longitude = float(self.ui_elements["hospital_longitude"].get_text())
        except (KeyError, ValueError):
            return
        if not name or not city:
            return
        try:
            from data.hospitais_sp import add_hospital
        except Exception:
            add_hospital = None
        created = None
        if add_hospital:
            created = add_hospital(
                name=name,
                city=city,
                type=hosp_type,
                priority=priority,
                demand=demand,
                latitude=latitude,
                longitude=longitude,
            )
            if created is None:
                return
            new_id = created.id
            name = created.name
            priority = created.priority
            demand = created.demand
            latitude = created.latitude
            longitude = created.longitude
        else:
            ids = [p.id for p in self.delivery_points]
            for points in self.scenario_points:
                ids.extend(p.id for p in points)
            new_id = max(ids) + 1 if ids else 1
        targets = []
        seen = set()
        for points in [self.delivery_points] + self.scenario_points:
            if id(points) in seen:
                continue
            seen.add(id(points))
            targets.append(points)
        for points in targets:
            if any(p.id == new_id for p in points):
                continue
            points.append(
                DeliveryPoint(
                    id=new_id,
                    name=name,
                    x=longitude,
                    y=latitude,
                    demand=demand,
                    priority=priority,
                    time_window=(0, 480)
                )
            )
        self._calculate_bounds()
        self._update_hospital_list()
        self._reset_hospital_editor_ui()

    def _delete_selected_hospital(self):
        """Remove hospital selecionado e atualiza listas/mapa."""
        if not self._can_edit_config() or self.selected_hospital_id is None:
            return
        try:
            from data.hospitais_sp import remove_hospital_by_id
        except Exception:
            remove_hospital_by_id = None
        if remove_hospital_by_id and not remove_hospital_by_id(self.selected_hospital_id):
            return
        for points in [self.delivery_points] + self.scenario_points:
            points[:] = [p for p in points if p.id != self.selected_hospital_id]
        self.selected_hospital_id = None
        self._calculate_bounds()
        self._update_hospital_list()
        self._reset_hospital_editor_ui()

    def _apply_text_entry(self, ui_element, text: str):
        """Aplica valores digitados."""
        if not self._can_edit_config():
            return
        try:
            if ui_element == self.ui_elements.get("vehicles"):
                self._set_vehicle_count(int(text))
            elif ui_element == self.ui_elements.get("vehicle_capacity"):
                self._set_vehicle_capacity(float(text))
            elif ui_element == self.ui_elements.get("vehicle_max_distance"):
                self._set_vehicle_max_distance(float(text))
            elif ui_element == self.ui_elements.get("vehicle_speed"):
                self._set_vehicle_speed(float(text))
            elif ui_element == self.ui_elements.get("population"):
                self._set_int("population_size", int(text))
            elif ui_element == self.ui_elements.get("generations"):
                self._set_int("max_generations", int(text))
            elif ui_element == self.ui_elements.get("tournament"):
                self._set_int("tournament_size", int(text))
            elif ui_element == self.ui_elements.get("heuristic"):
                self._set_float("heuristic_init_ratio", float(text), 2)
            elif ui_element == self.ui_elements.get("crossover_rate"):
                self._set_float("crossover_rate", float(text), 2)
            elif ui_element == self.ui_elements.get("mutation_rate"):
                self._set_float("mutation_rate", float(text), 2)
            elif ui_element == self.ui_elements.get("elites"):
                self._set_int("elite_size", int(text))
            elif ui_element == self.ui_elements.get("stagnation"):
                self._set_int("stagnation_limit", int(text))
        except ValueError:
            pass
        self.ui_needs_sync = True

    def _apply_dropdown(self, ui_element, text: str):
        """Aplica seleção do dropdown."""
        if not self._can_edit_config():
            return
        if ui_element == self.ui_elements.get("scenario"):
            if text in self.scenario_names:
                self._set_scenario(self.scenario_names.index(text))
        elif ui_element == self.ui_elements.get("selection"):
            method = self._enum_from_label(text, SELECTION_LABELS, SelectionMethod)
            if method is not None:
                self._set_enum("selection_method", method)
        elif ui_element == self.ui_elements.get("crossover_method"):
            method = self._enum_from_label(text, CROSSOVER_LABELS, CrossoverMethod)
            if method is not None:
                self._set_enum("crossover_method", method)
        elif ui_element == self.ui_elements.get("mutation_method"):
            method = self._enum_from_label(text, MUTATION_LABELS, MutationMethod)
            if method is not None:
                self._set_enum("mutation_method", method)
        elif ui_element == self.ui_elements.get("replacement"):
            method = self._enum_from_label(text, REPLACEMENT_LABELS, ReplacementStrategy)
            if method is not None:
                self._set_enum("replacement_strategy", method)
        elif ui_element == self.ui_elements.get("fitness"):
            method = self._enum_from_label(text, FITNESS_LABELS, FitnessType)
            if method is not None:
                self._set_enum("fitness_type", method)
        self.ui_needs_sync = True

    def _apply_all_ui_values(self):
        """Aplica todos os valores da UI antes de iniciar."""
        if not self.ui_elements or not self._can_edit_config():
            return
        entries = [
            ("vehicles", self._set_vehicle_count, int),
            ("vehicle_capacity", self._set_vehicle_capacity, float),
            ("vehicle_max_distance", self._set_vehicle_max_distance, float),
            ("vehicle_speed", self._set_vehicle_speed, float),
            ("population", lambda v: self._set_int("population_size", v), int),
            ("generations", lambda v: self._set_int("max_generations", v), int),
            ("tournament", lambda v: self._set_int("tournament_size", v), int),
            ("heuristic", lambda v: self._set_float("heuristic_init_ratio", v, 2), float),
            ("crossover_rate", lambda v: self._set_float("crossover_rate", v, 2), float),
            ("mutation_rate", lambda v: self._set_float("mutation_rate", v, 2), float),
            ("elites", lambda v: self._set_int("elite_size", v), int),
            ("stagnation", lambda v: self._set_int("stagnation_limit", v), int),
        ]
        for name, setter, caster in entries:
            entry = self.ui_elements.get(name)
            if entry is None:
                continue
            try:
                value = caster(entry.get_text())
            except ValueError:
                continue
            setter(value)

    def _set_int(self, attr: str, value: int):
        """Atualiza parâmetro inteiro do AG."""
        if not self._can_edit_config():
            return
        setattr(self.ga_config, attr, int(value))
        self.ui_needs_sync = True

    def _set_float(self, attr: str, value: float, precision: int):
        """Atualiza parâmetro float do AG."""
        if not self._can_edit_config():
            return
        setattr(self.ga_config, attr, round(float(value), precision))
        self.ui_needs_sync = True

    def _set_enum(self, attr: str, value: Enum):
        """Atualiza parâmetro enum do AG."""
        if not self._can_edit_config():
            return
        setattr(self.ga_config, attr, value)
        self.ui_needs_sync = True

    def _set_vehicle_count(self, value: int):
        """Atualiza quantidade de veículos."""
        if not self._can_edit_config():
            return
        self.vehicle_count = max(1, min(10, int(value)))
        self.ui_needs_sync = True

    def _set_vehicle_capacity(self, value: float):
        """Atualiza capacidade do veículo."""
        if not self._can_edit_config():
            return
        self.vehicle_capacity = max(1.0, float(value))
        self.ui_needs_sync = True

    def _set_vehicle_max_distance(self, value: float):
        """Atualiza autonomia do veículo."""
        if not self._can_edit_config():
            return
        self.vehicle_max_distance = max(1.0, float(value))
        self.ui_needs_sync = True

    def _set_vehicle_speed(self, value: float):
        """Atualiza velocidade do veículo."""
        if not self._can_edit_config():
            return
        self.vehicle_speed = max(1.0, float(value))
        self.ui_needs_sync = True


    def _set_scenario(self, index: int):
        """Seleciona cenário."""
        if not self._can_edit_config() or not self.scenario_points:
            return
        self.active_scenario_index = index
        self.delivery_points = self.scenario_points[index]
        self._calculate_bounds()
        self._reset()
        self._update_hospital_list()
        self._reset_hospital_editor_ui()
    
    def _export_map(self):
        """Exporta mapa HTML."""
        if self.best_chromosome is None:
            return
        
        try:
            from src.visualization.route_visualizer import RouteVisualizer
            
            visualizer = RouteVisualizer(
                self.delivery_points,
                self.depot_index
            )
            
            algorithm_info = (
                f"Seleção: {self.ga_config.selection_method.value} | "
                f"Crossover: {self.ga_config.crossover_method.value} | "
                f"Mutação: {self.ga_config.mutation_method.value}<br>"
                f"Reposição: {self.ga_config.replacement_strategy.value} | "
                f"Fitness: {self.ga_config.fitness_type.value} | "
                f"População: {self.ga_config.population_size} | "
                f"Gerações: {self.ga_config.max_generations}"
            )
            
            output_path = visualizer.visualize_solution(
                self.best_chromosome,
                output_path="mapa_rotas_hospitais_sp.html",
                title="Rotas Otimizadas - Hospitais de São Paulo",
                algorithm_info=algorithm_info,
                animate_car=True
            )
            
            print(f"Mapa exportado para: {output_path}")
            
        except Exception as e:
            print(f"Erro ao exportar mapa: {e}")

"""
Módulo de Visualização da Evolução do Algoritmo Genético
========================================================

Este módulo implementa visualização em tempo real da evolução
do algoritmo genético usando Pygame.

Funcionalidades:
---------------
- Gráfico de fitness ao longo das gerações
- Visualização das rotas em tempo real
- Estatísticas da população
- Controles interativos
"""

import os
import sys
import math
from typing import List, Optional, Tuple, Callable
from dataclasses import dataclass

try:
    import pygame
    from pygame import gfxdraw
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import matplotlib.backends.backend_agg as agg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.genetic_algorithm.chromosome import Chromosome, DeliveryPoint, Route
from src.genetic_algorithm.population import Population, PopulationStats


# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (128, 0, 128)

# Cores para rotas
ROUTE_COLORS = [
    (31, 119, 180),   # Azul
    (255, 127, 14),   # Laranja
    (44, 160, 44),    # Verde
    (214, 39, 40),    # Vermelho
    (148, 103, 189),  # Roxo
    (140, 86, 75),    # Marrom
    (227, 119, 194),  # Rosa
    (127, 127, 127),  # Cinza
    (188, 189, 34),   # Amarelo-verde
    (23, 190, 207),   # Ciano
]


@dataclass
class VisualizationConfig:
    """Configuração da visualização."""
    width: int = 1400
    height: int = 800
    fps: int = 30
    map_width: int = 800
    map_height: int = 600
    graph_width: int = 500
    graph_height: int = 300
    font_size: int = 14
    title_font_size: int = 20
    show_labels: bool = True
    animate_routes: bool = True


class EvolutionVisualizer:
    """
    Visualizador da evolução do algoritmo genético com Pygame.
    
    Mostra em tempo real:
    - Mapa com rotas atuais
    - Gráfico de evolução do fitness
    - Estatísticas da população
    """
    
    def __init__(self, delivery_points: List[DeliveryPoint],
                 depot_index: int = 0,
                 config: Optional[VisualizationConfig] = None):
        """
        Inicializa o visualizador.
        
        Args:
            delivery_points: Lista de pontos de entrega
            depot_index: Índice do depósito
            config: Configuração da visualização
        """
        if not PYGAME_AVAILABLE:
            raise ImportError("Pygame não está instalado. Use: pip install pygame")
        
        self.delivery_points = delivery_points
        self.depot_index = depot_index
        self.depot = delivery_points[depot_index]
        self.config = config or VisualizationConfig()
        
        # Histórico de fitness
        self.fitness_history: List[float] = []
        self.avg_fitness_history: List[float] = []
        self.generation = 0
        
        # Melhor solução atual
        self.best_chromosome: Optional[Chromosome] = None
        
        # Calcula limites do mapa
        self._calculate_bounds()
        
        # Estado da visualização
        self.running = False
        self.paused = False
        self.screen = None
        self.clock = None
        self.fonts = {}
    
    def _calculate_bounds(self):
        """Calcula limites das coordenadas para normalização."""
        xs = [p.x for p in self.delivery_points]
        ys = [p.y for p in self.delivery_points]
        
        self.min_x = min(xs)
        self.max_x = max(xs)
        self.min_y = min(ys)
        self.max_y = max(ys)
        
        # Adiciona margem
        margin_x = (self.max_x - self.min_x) * 0.1
        margin_y = (self.max_y - self.min_y) * 0.1
        
        self.min_x -= margin_x
        self.max_x += margin_x
        self.min_y -= margin_y
        self.max_y += margin_y
    
    def _normalize_coords(self, x: float, y: float,
                          offset_x: int = 50,
                          offset_y: int = 100) -> Tuple[int, int]:
        """
        Normaliza coordenadas para a tela.
        
        Args:
            x: Coordenada X (longitude)
            y: Coordenada Y (latitude)
            offset_x: Offset horizontal
            offset_y: Offset vertical
        
        Returns:
            Tupla (screen_x, screen_y)
        """
        # Normaliza para [0, 1]
        norm_x = (x - self.min_x) / (self.max_x - self.min_x)
        norm_y = (y - self.min_y) / (self.max_y - self.min_y)
        
        # Converte para coordenadas da tela
        screen_x = int(offset_x + norm_x * (self.config.map_width - 100))
        screen_y = int(offset_y + (1 - norm_y) * (self.config.map_height - 100))
        
        return screen_x, screen_y
    
    def initialize(self):
        """Inicializa Pygame e cria a janela."""
        pygame.init()
        
        self.screen = pygame.display.set_mode(
            (self.config.width, self.config.height)
        )
        pygame.display.set_caption(
            "Algoritmo Genético - Otimização de Rotas Hospitalares"
        )
        
        self.clock = pygame.time.Clock()
        
        # Carrega fontes
        self.fonts = {
            'small': pygame.font.SysFont('Arial', 10),
            'normal': pygame.font.SysFont('Arial', self.config.font_size),
            'title': pygame.font.SysFont('Arial', self.config.title_font_size, bold=True),
            'subtitle': pygame.font.SysFont('Arial', 16, bold=True),
        }
        
        self.running = True
    
    def update(self, generation: int, population: Population,
               best_chromosome: Chromosome):
        """
        Atualiza a visualização com novos dados.
        
        Args:
            generation: Número da geração atual
            population: População atual
            best_chromosome: Melhor cromossomo encontrado
        """
        self.generation = generation
        self.best_chromosome = best_chromosome
        
        # Atualiza histórico
        stats = population.calculate_stats()
        self.fitness_history.append(stats.best_fitness)
        self.avg_fitness_history.append(stats.avg_fitness)
    
    def render(self):
        """Renderiza um frame da visualização."""
        if not self.running or self.screen is None:
            return
        
        # Processa eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
        
        if self.paused:
            return
        
        # Limpa tela
        self.screen.fill(WHITE)
        
        # Desenha componentes
        self._draw_title()
        self._draw_map()
        self._draw_fitness_graph()
        self._draw_statistics()
        self._draw_controls_info()
        
        # Atualiza display
        pygame.display.flip()
        self.clock.tick(self.config.fps)
    
    def _draw_title(self):
        """Desenha o título."""
        title = self.fonts['title'].render(
            "Otimização de Rotas - Hospitais de São Paulo",
            True, BLACK
        )
        self.screen.blit(title, (20, 10))
        
        subtitle = self.fonts['subtitle'].render(
            f"Geração: {self.generation}",
            True, GRAY
        )
        self.screen.blit(subtitle, (20, 45))
    
    def _draw_map(self):
        """Desenha o mapa com hospitais e rotas."""
        # Área do mapa
        map_rect = pygame.Rect(20, 80, self.config.map_width, self.config.map_height)
        pygame.draw.rect(self.screen, LIGHT_GRAY, map_rect)
        pygame.draw.rect(self.screen, BLACK, map_rect, 2)
        
        # Título do mapa
        map_title = self.fonts['subtitle'].render("Mapa de Rotas", True, BLACK)
        self.screen.blit(map_title, (30, 85))
        
        # Desenha rotas se houver solução
        if self.best_chromosome is not None:
            routes = self.best_chromosome.get_routes()
            self._draw_routes(routes, map_rect)
        
        # Desenha hospitais
        self._draw_hospitals(map_rect)
    
    def _draw_hospitals(self, map_rect: pygame.Rect):
        """Desenha os marcadores dos hospitais."""
        for i, point in enumerate(self.delivery_points):
            x, y = self._normalize_coords(
                point.x, point.y,
                map_rect.x + 30, map_rect.y + 30
            )
            
            # Cor baseada na prioridade
            if i == self.depot_index:
                color = BLUE
                radius = 12
            else:
                priority = getattr(point, 'priority', 3)
                if priority == 1:
                    color = RED
                elif priority == 2:
                    color = ORANGE
                else:
                    color = GREEN
                radius = 8
            
            # Desenha círculo
            pygame.draw.circle(self.screen, color, (x, y), radius)
            pygame.draw.circle(self.screen, BLACK, (x, y), radius, 2)
            
            # Label (apenas para pontos importantes)
            if i == self.depot_index or getattr(point, 'priority', 3) == 1:
                if self.config.show_labels:
                    name = point.name[:15] + '...' if len(point.name) > 15 else point.name
                    label = self.fonts['small'].render(name, True, BLACK)
                    self.screen.blit(label, (x + 10, y - 5))
    
    def _draw_routes(self, routes: List[Route], map_rect: pygame.Rect):
        """Desenha as rotas no mapa."""
        for i, route in enumerate(routes):
            color = ROUTE_COLORS[i % len(ROUTE_COLORS)]
            
            # Coordenadas da rota
            points = []
            
            # Depósito
            depot_pos = self._normalize_coords(
                route.depot.x, route.depot.y,
                map_rect.x + 30, map_rect.y + 30
            )
            points.append(depot_pos)
            
            # Pontos de entrega
            for point in route.points:
                pos = self._normalize_coords(
                    point.x, point.y,
                    map_rect.x + 30, map_rect.y + 30
                )
                points.append(pos)
            
            # Volta ao depósito
            points.append(depot_pos)
            
            # Desenha linhas
            if len(points) > 1:
                pygame.draw.lines(self.screen, color, False, points, 3)
                
                # Desenha setas
                for j in range(len(points) - 1):
                    self._draw_arrow(points[j], points[j+1], color)
    
    def _draw_arrow(self, start: Tuple[int, int], end: Tuple[int, int],
                    color: Tuple[int, int, int], size: int = 8):
        """Desenha uma seta entre dois pontos."""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.sqrt(dx*dx + dy*dy)
        
        if length < 20:
            return
        
        # Ponto no meio da linha
        mid_x = (start[0] + end[0]) // 2
        mid_y = (start[1] + end[1]) // 2
        
        # Ângulo da linha
        angle = math.atan2(dy, dx)
        
        # Pontos da seta
        arrow_points = [
            (mid_x + size * math.cos(angle),
             mid_y + size * math.sin(angle)),
            (mid_x + size * math.cos(angle + 2.5),
             mid_y + size * math.sin(angle + 2.5)),
            (mid_x + size * math.cos(angle - 2.5),
             mid_y + size * math.sin(angle - 2.5)),
        ]
        
        pygame.draw.polygon(self.screen, color, 
                           [(int(p[0]), int(p[1])) for p in arrow_points])
    
    def _draw_fitness_graph(self):
        """Desenha o gráfico de evolução do fitness."""
        # Área do gráfico
        graph_x = self.config.map_width + 60
        graph_y = 80
        graph_width = self.config.graph_width
        graph_height = self.config.graph_height
        
        graph_rect = pygame.Rect(graph_x, graph_y, graph_width, graph_height)
        pygame.draw.rect(self.screen, WHITE, graph_rect)
        pygame.draw.rect(self.screen, BLACK, graph_rect, 2)
        
        # Título
        title = self.fonts['subtitle'].render("Evolução do Fitness", True, BLACK)
        self.screen.blit(title, (graph_x + 10, graph_y + 5))
        
        if len(self.fitness_history) < 2:
            return
        
        # Área de plotagem
        plot_x = graph_x + 50
        plot_y = graph_y + 40
        plot_width = graph_width - 70
        plot_height = graph_height - 70
        
        # Eixos
        pygame.draw.line(self.screen, BLACK, 
                        (plot_x, plot_y), (plot_x, plot_y + plot_height), 2)
        pygame.draw.line(self.screen, BLACK,
                        (plot_x, plot_y + plot_height), 
                        (plot_x + plot_width, plot_y + plot_height), 2)
        
        # Escala
        min_fitness = min(self.fitness_history)
        max_fitness = max(self.fitness_history)
        fitness_range = max_fitness - min_fitness
        
        if fitness_range == 0:
            fitness_range = 1
        
        # Plota linhas
        num_points = len(self.fitness_history)
        
        # Melhor fitness (verde)
        best_points = []
        for i, fitness in enumerate(self.fitness_history):
            x = plot_x + int(i / num_points * plot_width)
            y = plot_y + plot_height - int((fitness - min_fitness) / fitness_range * plot_height)
            best_points.append((x, y))
        
        if len(best_points) > 1:
            pygame.draw.lines(self.screen, GREEN, False, best_points, 2)
        
        # Média (azul)
        avg_points = []
        for i, fitness in enumerate(self.avg_fitness_history):
            x = plot_x + int(i / num_points * plot_width)
            y = plot_y + plot_height - int((fitness - min_fitness) / fitness_range * plot_height)
            avg_points.append((x, y))
        
        if len(avg_points) > 1:
            pygame.draw.lines(self.screen, BLUE, False, avg_points, 2)
        
        # Labels dos eixos
        y_label = self.fonts['small'].render("Fitness", True, BLACK)
        self.screen.blit(y_label, (graph_x + 5, plot_y + plot_height // 2))
        
        x_label = self.fonts['small'].render("Geração", True, BLACK)
        self.screen.blit(x_label, (plot_x + plot_width // 2, plot_y + plot_height + 10))
        
        # Valores
        max_label = self.fonts['small'].render(f"{max_fitness:.0f}", True, BLACK)
        self.screen.blit(max_label, (plot_x - 45, plot_y - 5))
        
        min_label = self.fonts['small'].render(f"{min_fitness:.0f}", True, BLACK)
        self.screen.blit(min_label, (plot_x - 45, plot_y + plot_height - 10))
        
        # Legenda
        legend_y = graph_y + graph_height - 25
        pygame.draw.line(self.screen, GREEN, 
                        (graph_x + 60, legend_y), (graph_x + 90, legend_y), 2)
        best_text = self.fonts['small'].render("Melhor", True, BLACK)
        self.screen.blit(best_text, (graph_x + 95, legend_y - 5))
        
        pygame.draw.line(self.screen, BLUE,
                        (graph_x + 160, legend_y), (graph_x + 190, legend_y), 2)
        avg_text = self.fonts['small'].render("Média", True, BLACK)
        self.screen.blit(avg_text, (graph_x + 195, legend_y - 5))
    
    def _draw_statistics(self):
        """Desenha estatísticas da solução atual."""
        stats_x = self.config.map_width + 60
        stats_y = 400
        
        # Título
        title = self.fonts['subtitle'].render("Estatísticas", True, BLACK)
        self.screen.blit(title, (stats_x, stats_y))
        
        if self.best_chromosome is None:
            return
        
        routes = self.best_chromosome.get_routes()
        
        # Informações
        y_offset = stats_y + 30
        line_height = 25
        
        stats = [
            f"Fitness: {self.best_chromosome.fitness:.2f}",
            f"Número de Rotas: {len(routes)}",
            f"Total de Hospitais: {len(self.delivery_points) - 1}",
            "",
            "Detalhes das Rotas:",
        ]
        
        for i, route in enumerate(routes):
            stats.append(f"  Rota {i+1}: {len(route.points)} paradas, {route.total_distance:.1f}km")
        
        for stat in stats:
            text = self.fonts['normal'].render(stat, True, BLACK)
            self.screen.blit(text, (stats_x, y_offset))
            y_offset += line_height
    
    def _draw_controls_info(self):
        """Desenha informações de controles."""
        controls_y = self.config.height - 40
        
        controls = [
            "Controles: [ESPAÇO] Pausar/Continuar | [ESC] Sair"
        ]
        
        for i, control in enumerate(controls):
            text = self.fonts['normal'].render(control, True, GRAY)
            self.screen.blit(text, (20, controls_y + i * 20))
        
        # Status
        if self.paused:
            status = self.fonts['subtitle'].render("PAUSADO", True, RED)
            self.screen.blit(status, (self.config.width - 120, controls_y))
    
    def close(self):
        """Fecha a visualização."""
        self.running = False
        if pygame.get_init():
            pygame.quit()
    
    def is_running(self) -> bool:
        """Verifica se a visualização está rodando."""
        return self.running


class EvolutionCallback:
    """
    Callback para integração com o algoritmo genético.
    
    Permite atualizar a visualização durante a execução do AG.
    """
    
    def __init__(self, visualizer: EvolutionVisualizer,
                 update_interval: int = 1):
        """
        Inicializa o callback.
        
        Args:
            visualizer: Instância do visualizador
            update_interval: Intervalo de atualização (gerações)
        """
        self.visualizer = visualizer
        self.update_interval = update_interval
    
    def __call__(self, generation: int, population: Population,
                 best_chromosome: Chromosome):
        """
        Chamado a cada geração do AG.
        
        Args:
            generation: Número da geração
            population: População atual
            best_chromosome: Melhor cromossomo
        """
        if generation % self.update_interval == 0:
            self.visualizer.update(generation, population, best_chromosome)
            self.visualizer.render()
            
            if not self.visualizer.is_running():
                raise KeyboardInterrupt("Visualização fechada pelo usuário")

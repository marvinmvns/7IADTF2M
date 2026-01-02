"""
Módulo de Visualização de Rotas
===============================

Este módulo implementa visualizações de rotas usando:
- Folium: Mapas interativos baseados em OpenStreetMap
- Matplotlib: Gráficos estáticos de alta qualidade

A visualização mostra:
- Localização dos hospitais no mapa de São Paulo
- Rotas otimizadas entre os pontos
- Cores diferenciadas por prioridade e veículo
- Informações detalhadas em popups interativos
"""

import os
import math
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass

try:
    import folium
    from folium import plugins
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.collections import LineCollection
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.genetic_algorithm.chromosome import Chromosome, DeliveryPoint, Route


# Cores para diferentes prioridades
PRIORITY_COLORS = {
    1: '#FF0000',  # Vermelho - Crítico
    2: '#FFA500',  # Laranja - Urgente
    3: '#00FF00',  # Verde - Regular
    0: '#0000FF',  # Azul - Depósito
}

# Cores para diferentes veículos
VEHICLE_COLORS = [
    '#1f77b4',  # Azul
    '#ff7f0e',  # Laranja
    '#2ca02c',  # Verde
    '#d62728',  # Vermelho
    '#9467bd',  # Roxo
    '#8c564b',  # Marrom
    '#e377c2',  # Rosa
    '#7f7f7f',  # Cinza
    '#bcbd22',  # Amarelo-verde
    '#17becf',  # Ciano
]


class RouteVisualizer:
    """
    Visualizador de rotas em mapas.
    
    Gera mapas interativos com Folium e gráficos estáticos com Matplotlib.
    """
    
    def __init__(self, delivery_points: List[DeliveryPoint],
                 depot_index: int = 0):
        """
        Inicializa o visualizador.
        
        Args:
            delivery_points: Lista de pontos de entrega
            depot_index: Índice do depósito
        """
        self.delivery_points = delivery_points
        self.depot_index = depot_index
        self.depot = delivery_points[depot_index]
        
        # Calcula centro do mapa
        self.center_lat = sum(p.y for p in delivery_points) / len(delivery_points)
        self.center_lon = sum(p.x for p in delivery_points) / len(delivery_points)
        self._route_line_names: List[str] = []
        self._route_line_colors: List[str] = []
    
    def create_base_map(self, zoom_start: int = 10) -> 'folium.Map':
        """
        Cria mapa base com Folium.
        
        Args:
            zoom_start: Nível de zoom inicial
        
        Returns:
            Objeto folium.Map
        """
        if not FOLIUM_AVAILABLE:
            raise ImportError("Folium não está instalado. Use: pip install folium")
        
        # Cria mapa centrado em São Paulo
        m = folium.Map(
            location=[self.center_lat, self.center_lon],
            zoom_start=zoom_start,
            tiles='OpenStreetMap'
        )
        
        # Adiciona controles
        plugins.Fullscreen().add_to(m)
        plugins.MiniMap().add_to(m)
        
        return m
    
    def add_hospitals_to_map(self, m: 'folium.Map',
                             show_labels: bool = True) -> 'folium.Map':
        """
        Adiciona marcadores de hospitais ao mapa.
        
        Args:
            m: Mapa Folium
            show_labels: Se deve mostrar labels
        
        Returns:
            Mapa atualizado
        """
        for i, point in enumerate(self.delivery_points):
            # Determina cor e ícone baseado na prioridade
            if i == self.depot_index:
                color = 'blue'
                icon = 'warehouse'
                prefix = 'fa'
            else:
                priority = getattr(point, 'priority', 3)
                if priority == 1:
                    color = 'red'
                    icon = 'hospital'
                elif priority == 2:
                    color = 'orange'
                    icon = 'hospital'
                else:
                    color = 'green'
                    icon = 'hospital'
                prefix = 'fa'
            
            # Cria popup com informações
            popup_html = f"""
            <div style="font-family: Arial; width: 200px;">
                <h4 style="margin: 0; color: {color};">{point.name}</h4>
                <hr style="margin: 5px 0;">
                <p><b>ID:</b> {point.id}</p>
                <p><b>Prioridade:</b> {self._priority_text(getattr(point, 'priority', 3))}</p>
                <p><b>Demanda:</b> {getattr(point, 'demand', 0):.1f} unidades</p>
                <p><b>Coordenadas:</b><br>
                   Lat: {point.y:.4f}<br>
                   Lon: {point.x:.4f}</p>
            </div>
            """
            
            # Adiciona marcador
            folium.Marker(
                location=[point.y, point.x],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=point.name if show_labels else None,
                icon=folium.Icon(color=color, icon=icon, prefix=prefix)
            ).add_to(m)
        
        return m
    
    def add_routes_to_map(self, m: 'folium.Map',
                          routes: List[Route],
                          show_direction: bool = True,
                          show_distance: bool = True,
                          show_segment_distances: bool = True,
                          show_order: bool = True) -> 'folium.Map':
        """
        Adiciona rotas ao mapa.
        
        Args:
            m: Mapa Folium
            routes: Lista de rotas
            show_direction: Se deve mostrar setas de direção
            show_distance: Se deve mostrar distâncias
        
        Returns:
            Mapa atualizado
        """
        self._route_line_names = []
        self._route_line_colors = []
        for i, route in enumerate(routes):
            color = VEHICLE_COLORS[i % len(VEHICLE_COLORS)]
            
            # Constrói lista de coordenadas da rota
            coords = [[route.depot.y, route.depot.x]]  # Começa no depósito
            
            for point in route.points:
                coords.append([point.y, point.x])
            
            coords.append([route.depot.y, route.depot.x])  # Volta ao depósito
            
            # Adiciona linha da rota
            route_line = folium.PolyLine(
                locations=coords,
                weight=3,
                color=color,
                opacity=0.8,
                popup=f"Rota {i+1} - Veículo {route.vehicle.id}<br>"
                      f"Distância: {route.total_distance:.2f} km<br>"
                      f"Paradas: {len(route.points)}"
            )
            route_line.add_to(m)
            self._route_line_names.append(route_line.get_name())
            self._route_line_colors.append(color)
            
            if show_segment_distances:
                for a, b in zip(coords, coords[1:]):
                    segment_distance = self._haversine_km(a[0], a[1], b[0], b[1])
                    folium.PolyLine(
                        locations=[a, b],
                        weight=6,
                        color=color,
                        opacity=0.0,
                        tooltip=f"{segment_distance:.2f} km"
                    ).add_to(m)
            
            if show_order:
                for order_index, point in enumerate(route.points, start=1):
                    folium.Marker(
                        location=[point.y, point.x],
                        icon=folium.DivIcon(
                            html=(
                                "<div style='"
                                "background:{color};"
                                "color:#fff;"
                                "border-radius:10px;"
                                "padding:2px 6px;"
                                "font-size:10px;"
                                "border:1px solid #222;"
                                "text-align:center;'>"
                                "{order}"
                                "</div>"
                            ).format(color=color, order=order_index)
                        ),
                        tooltip=f"Ordem: {order_index}"
                    ).add_to(m)
            
            # Adiciona setas de direção
            if show_direction:
                plugins.AntPath(
                    locations=coords,
                    weight=2,
                    color=color,
                    delay=1000,
                    dash_array=[10, 20],
                    pulse_color=color
                ).add_to(m)
        
        return m
    
    def visualize_solution(self, chromosome: Chromosome,
                           output_path: str = "mapa_rotas.html",
                           title: str = "Otimização de Rotas - Hospitais SP",
                           algorithm_info: Optional[str] = None,
                           animate_car: bool = True) -> str:
        """
        Gera visualização completa da solução.
        
        Args:
            chromosome: Cromossomo com a solução
            output_path: Caminho para salvar o HTML
            title: Título do mapa
        
        Returns:
            Caminho do arquivo salvo
        """
        if not FOLIUM_AVAILABLE:
            raise ImportError("Folium não está instalado")
        
        # Cria mapa
        m = self.create_base_map()
        
        # Adiciona título
        algorithm_html = f"<p style='margin: 5px 0;'>{algorithm_info}</p>" if algorithm_info else ""
        title_html = f'''
        <div style="position: fixed; 
                    top: 10px; left: 50px; width: 400px;
                    background-color: white; 
                    border: 2px solid grey; 
                    z-index: 9999; 
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 5px;">
            <h3 style="margin: 0;">{title}</h3>
            <p style="margin: 5px 0;">Fitness: {chromosome.fitness:.2f}</p>
            {algorithm_html}
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Adiciona hospitais
        m = self.add_hospitals_to_map(m)
        
        # Adiciona rotas
        routes = chromosome.get_routes()
        m = self.add_routes_to_map(m, routes)
        
        # Adiciona legenda
        m = self._add_legend(m, routes)
        
        if animate_car:
            self._add_car_animation(m, routes)
        
        # Salva mapa
        m.save(output_path)
        
        return output_path

    def _add_car_animation(self, m: 'folium.Map', routes: List[Route]) -> None:
        """Adiciona animação de 'carro' simples no mapa."""
        map_name = m.get_name()
        routes_coords = []
        for route in routes:
            coords = [[route.depot.y, route.depot.x]]
            for point in route.points:
                coords.append([point.y, point.x])
            coords.append([route.depot.y, route.depot.x])
            routes_coords.append(coords)
        
        animation_js = f"""
        <style>
        .car-marker {{
            background: #111;
            color: #fff;
            padding: 2px 6px;
            border-radius: 6px;
            font-size: 10px;
            font-family: Arial, sans-serif;
        }}
        </style>
        <script>
        (function() {{
            var map = {map_name};
            var routes = {routes_coords};
            routes.forEach(function(coords, idx) {{
                if (!coords || coords.length === 0) return;
                var icon = L.divIcon({{
                    className: 'car-marker',
                    html: 'CAR',
                    iconSize: [28, 14],
                    iconAnchor: [14, 7]
                }});
                var marker = L.marker(coords[0], {{icon: icon}}).addTo(map);
                var i = 0;
                setInterval(function() {{
                    i = (i + 1) % coords.length;
                    marker.setLatLng(coords[i]);
                }}, 700 + (idx * 120));
            }});
        }})();
        </script>
        """
        m.get_root().html.add_child(folium.Element(animation_js))

    @staticmethod
    def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcula distância haversine em km entre dois pontos."""
        import math
        r = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c
    
    def _add_legend(self, m: 'folium.Map', routes: List[Route]) -> 'folium.Map':
        """Adiciona legenda ao mapa."""
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; right: 50px; 
                    width: 200px;
                    background-color: white; 
                    border: 2px solid grey; 
                    z-index: 9999; 
                    font-size: 12px;
                    padding: 10px;
                    border-radius: 5px;">
            <h4 style="margin: 0 0 10px 0;">Legenda</h4>
            <p><span style="color: blue;">●</span> Depósito</p>
            <p><span style="color: red;">●</span> Hospital Crítico</p>
            <p><span style="color: orange;">●</span> Hospital Urgente</p>
            <p><span style="color: green;">●</span> Hospital Regular</p>
            <hr>
            <h5 style="margin: 10px 0 5px 0;">Rotas:</h5>
        '''
        
        for i, route in enumerate(routes):
            color = VEHICLE_COLORS[i % len(VEHICLE_COLORS)]
            legend_html += f'''
            <p class="route-legend-item" data-route-index="{i}"
               style="cursor: pointer; margin: 4px 0;">
               <span style="color: {color};">━━</span> 
               Rota {i+1}: {route.total_distance:.1f}km</p>
            '''
        
        legend_html += '</div>'
        
        m.get_root().html.add_child(folium.Element(legend_html))

        if self._route_line_names:
            route_lines_js = ", ".join(self._route_line_names)
            route_colors_js = ", ".join(
                f"'{color}'" for color in self._route_line_colors
            )
            blink_js = f"""
            (function() {{
                var routeLines = [{route_lines_js}];
                var routeColors = [{route_colors_js}];
                function blinkRoute(idx) {{
                    var line = routeLines[idx];
                    if (!line) return;
                    if (!line.__blinkOriginal) {{
                        line.__blinkOriginal = {{
                            color: line.options.color,
                            weight: line.options.weight,
                            opacity: line.options.opacity
                        }};
                    }}
                    if (line.__blinkTimer) {{
                        clearInterval(line.__blinkTimer);
                        line.__blinkTimer = null;
                    }}
                    var original = line.__blinkOriginal;
                    var flashes = 0;
                    var visible = true;
                    line.setStyle({{weight: original.weight + 3}});
                    line.__blinkTimer = setInterval(function() {{
                        visible = !visible;
                        line.setStyle({{
                            opacity: visible ? 1.0 : 0.1,
                            color: routeColors[idx] || original.color
                        }});
                        flashes += 1;
                        if (flashes >= 6) {{
                            clearInterval(line.__blinkTimer);
                            line.__blinkTimer = null;
                            line.setStyle(original);
                        }}
                    }}, 250);
                }}
                function bindLegendClicks() {{
                    var items = document.querySelectorAll('.route-legend-item');
                    items.forEach(function(item) {{
                        item.addEventListener('click', function() {{
                            var idx = parseInt(
                                item.getAttribute('data-route-index'), 10
                            );
                            if (!isNaN(idx)) {{
                                blinkRoute(idx);
                            }}
                        }});
                    }});
                }}
                if (document.readyState === 'loading') {{
                    document.addEventListener('DOMContentLoaded', bindLegendClicks);
                }} else {{
                    bindLegendClicks();
                }}
            }})();
            """
            m.get_root().script.add_child(folium.Element(blink_js))
        
        return m
    
    def _priority_text(self, priority: int) -> str:
        """Converte prioridade numérica para texto."""
        texts = {
            0: "Depósito",
            1: "Crítico (Alta)",
            2: "Urgente (Média)",
            3: "Regular (Baixa)"
        }
        return texts.get(priority, "Desconhecida")
    
    # ========================================================================
    # VISUALIZAÇÃO COM MATPLOTLIB (alternativa sem mapa real)
    # ========================================================================
    
    def plot_routes_matplotlib(self, chromosome: Chromosome,
                               output_path: str = "rotas.png",
                               figsize: Tuple[int, int] = (14, 10)) -> str:
        """
        Plota rotas usando Matplotlib.
        
        Args:
            chromosome: Cromossomo com a solução
            output_path: Caminho para salvar a imagem
            figsize: Tamanho da figura
        
        Returns:
            Caminho do arquivo salvo
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("Matplotlib não está instalado")
        
        fig, ax = plt.subplots(figsize=figsize)
        
        routes = chromosome.get_routes()
        
        # Plota hospitais
        for i, point in enumerate(self.delivery_points):
            if i == self.depot_index:
                ax.scatter(point.x, point.y, c='blue', s=200, marker='s',
                          zorder=5, label='Depósito')
            else:
                priority = getattr(point, 'priority', 3)
                color = PRIORITY_COLORS.get(priority, '#00FF00')
                ax.scatter(point.x, point.y, c=color, s=100, marker='o',
                          zorder=4)
        
        # Plota rotas
        for i, route in enumerate(routes):
            color = VEHICLE_COLORS[i % len(VEHICLE_COLORS)]
            
            # Coordenadas da rota
            x_coords = [route.depot.x]
            y_coords = [route.depot.y]
            
            for point in route.points:
                x_coords.append(point.x)
                y_coords.append(point.y)
            
            x_coords.append(route.depot.x)
            y_coords.append(route.depot.y)
            
            # Plota linha
            ax.plot(x_coords, y_coords, c=color, linewidth=2, alpha=0.7,
                   label=f'Rota {i+1} ({route.total_distance:.1f}km)')
            
            # Adiciona setas
            for j in range(len(x_coords) - 1):
                dx = x_coords[j+1] - x_coords[j]
                dy = y_coords[j+1] - y_coords[j]
                ax.annotate('', xy=(x_coords[j+1], y_coords[j+1]),
                           xytext=(x_coords[j], y_coords[j]),
                           arrowprops=dict(arrowstyle='->', color=color, lw=1.5))
        
        # Adiciona labels dos hospitais
        for point in self.delivery_points:
            ax.annotate(point.name[:20] + '...' if len(point.name) > 20 else point.name,
                       (point.x, point.y), textcoords="offset points",
                       xytext=(5, 5), fontsize=8, alpha=0.7)
        
        # Configurações do gráfico
        ax.set_xlabel('Longitude', fontsize=12)
        ax.set_ylabel('Latitude', fontsize=12)
        ax.set_title(f'Otimização de Rotas - Hospitais SP\n'
                    f'Fitness: {chromosome.fitness:.2f}', fontsize=14)
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Adiciona legenda de prioridades
        priority_patches = [
            mpatches.Patch(color='red', label='Crítico'),
            mpatches.Patch(color='orange', label='Urgente'),
            mpatches.Patch(color='green', label='Regular'),
            mpatches.Patch(color='blue', label='Depósito'),
        ]
        ax.legend(handles=priority_patches, loc='upper right', title='Prioridade')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path


def create_delivery_points_from_hospitals(hospitals: list) -> List[DeliveryPoint]:
    """
    Converte dados de hospitais para DeliveryPoints.
    
    Args:
        hospitals: Lista de HospitalData
    
    Returns:
        Lista de DeliveryPoint
    """
    points = []
    
    for h in hospitals:
        point = DeliveryPoint(
            id=h.id,
            name=h.name,
            x=h.longitude,  # Longitude como X
            y=h.latitude,   # Latitude como Y
            demand=h.demand,
            priority=h.priority,
            time_window=(0, 480)  # 8 horas de janela
        )
        points.append(point)
    
    return points

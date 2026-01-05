import streamlit as st
import pandas as pd
import requests
import json
import subprocess
import os
import sys
import pytz
from datetime import datetime
from streamlit_folium import st_folium

# Adiciona o diretório raiz ao path para evitar ModuleNotFoundError
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.web.components.styles import apply_custom_styles

# Config
st.set_page_config(
    page_title="Saúdelog - Otimização Logística",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Helper de Fuso Horário
def format_date_br(date_str):
    try:
        if not date_str: return "-"
        # Assume UTC do banco
        dt_utc = pd.to_datetime(date_str)
        if dt_utc.tzinfo is None:
            dt_utc = dt_utc.tz_localize('UTC')
        
        # Converte para SP
        dt_br = dt_utc.tz_convert('America/Sao_Paulo')
        return dt_br.strftime('%d/%m/%Y %H:%M')
    except:
        return date_str

# Aplica Estilização CSS Customizada (Segregada)
apply_custom_styles()

# Sidebar
# Navbar Superior
col_nav1, col_nav2 = st.columns([1.5, 2.5])

with col_nav1:
    # Carrega e codifica o logo para uso em HTML (Flexbox para alinhamento perfeito)
    import base64
    logo_path = "assets/logo.png"  # Valor padrão
    try:
        config_opts_logo = get_config_options()
        logo_path = config_opts_logo.get("logo_path", "assets/logo.png")
    except:
        pass
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 15px; margin-top: -15px;">
                <img src="data:image/png;base64,{logo_b64}" style="height: 90px; width: auto;">
                <h1 style="margin: 0; padding: 0; color: #007BFF; font-family: 'Inter', sans-serif; font-size: 3rem; line-height: 1.2;">Saúdelog</h1>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        st.markdown("<h1 style='color: #007BFF;'>Saúdelog</h1>", unsafe_allow_html=True)

    # Estilos globais para botões de navegação
    st.markdown(
        """
        <style>
        [data-testid="stBaseButton-segmented_control"] {
            padding: 10px 20px !important;
            height: auto !important;
        }
        [data-testid="stBaseButton-segmented_controlActive"] {
            padding: 10px 20px !important;
            height: auto !important;
        }
        [data-testid="stBaseButton-segmented_control"] p {
            font-size: 1.2rem !important;
            font-weight: 600 !important;
        }
        [data-testid="stBaseButton-segmented_controlActive"] p {
            font-size: 1.2rem !important;
            font-weight: 600 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


with col_nav2:
    # Inicializa página no session_state se não existir
    if 'nav_page' not in st.session_state:
        st.session_state.nav_page = "Dashboard"

    # Callback para mudar página pelo menu
    def on_page_change():
        # Impede seleção vazia: se usuário desmarcar, volta para Dashboard
        if st.session_state.nav_page is None:
            st.session_state.nav_page = "Dashboard"

    page = st.segmented_control(
        "Navegação", 
        ["Dashboard", "Nova Execução", "Análise Detalhada", "Gerador Logístico", "Logistic LLM", "⚙️"],
        key="nav_page",
        on_change=on_page_change,
        label_visibility="collapsed",
        selection_mode="single"
    )
    
    # Fallback local se vier vazio (para garantir renderização correta nesta execução)
    if not page:
        page = "Dashboard"
    


# Configuração da API - busca da própria API
def get_api_config():
    """Obtém configurações da API, com prioridade para variável de ambiente."""
    # 1. Variável de Ambiente (Docker/Cloud)
    env_url = os.getenv("API_URL")
    if env_url:
        return env_url

    # 2. Tentativa de conexão local (Fallback)
    try:
        response = requests.get("http://localhost:8000/config/options", timeout=1)
        if response.status_code == 200:
            return response.json().get("api_url", "http://localhost:8000")
    except:
        pass
        
    return "http://localhost:8000"

API_URL = get_api_config()

# Cache de configurações para evitar múltiplas chamadas
@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_default_config():
    """Obtém configuração padrão da API."""
    try:
        response = requests.get(f"{API_URL}/config/defaults", timeout=2)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    # Fallback para valores hardcoded se API não responder
    return {
        "population_size": 100,
        "max_generations": 200,
        "crossover_rate": 0.9,
        "mutation_rate": 0.15,
        "scenario": "large",
        "num_vehicles": 3,
        "vehicle_capacity": 100.0,
        "vehicle_speed": 40.0,
        "vehicle_max_distance": 200.0,
        "selection_method": "tournament",
        "crossover_method": "order_crossover",
        "mutation_method": "inversion",
        "elite_size": 2,
        "tournament_size": 3,
        "stagnation_limit": 50,
        "w_distance": 1.0,
        "w_priority": 10.0,
        "w_capacity": 100.0,
        "w_autonomy": 100.0,
        "w_window": 50.0,
        "heuristic_init_ratio": 0.2
    }

@st.cache_data(ttl=300)
def get_config_options():
    """Obtém opções de configuração da API."""
    try:
        response = requests.get(f"{API_URL}/config/options", timeout=2)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    # Fallback
    return {
        "scenarios": ["small", "medium", "large", "critical"],
        "selection_methods": ["roulette_wheel", "tournament", "rank", "truncation", "elitist", "stochastic_universal_sampling", "boltzmann", "steady_state"],
        "crossover_methods": ["order_crossover", "partially_mapped_crossover", "cycle_crossover", "alternating_edges_crossover", "edge_recombination_crossover", "sequential_constructive_crossover", "order_based_crossover", "position_based_crossover"],
        "mutation_methods": ["inversion", "swap", "scramble", "insert", "displacement", "2-opt", "3-opt", "reverse_sequence"],
        "replacement_strategies": ["generational", "steady_state", "elitist"],
        "fitness_types": ["weighted_multi_objective", "distance_only", "penalty_based", "priority_aware"],
        "logo_path": "assets/logo.png"
    }

def run_pygame_visual(config):
    """Lança o processo Pygame."""
    try:
        # Salva config temporária
        with open("temp_config.json", "w") as f:
            json.dump(config, f)
        
        # Executa comando
        cmd = f"{sys.executable} main.py --mode visual --config temp_config.json"
        subprocess.Popen(cmd, shell=True)
        st.success("Visualizador iniciado! Verifique a nova janela.")
    except Exception as e:
        st.error(f"Erro ao iniciar visualizador: {e}")

if page == "Dashboard":
    st.title("📊 Dashboard Executivo")
    
    # Métricas Gerais
    col1, col2, col3 = st.columns(3)
    
    try:
        exp_response = requests.get(f"{API_URL}/experiments", timeout=5)
        exp_response.raise_for_status()
        experiments = pd.DataFrame(exp_response.json())
        
        if not experiments.empty:
            # === PREPARAÇÃO DE DADOS (Moved Up) ===
            # === PREPARAÇÃO DE DADOS (Moved Up) ===
            def get_fitness_label(config):
                if not isinstance(config, dict): return "🧬 Padrão"
                ftype = config.get('fitness_type', 'N/A')
                mapping = {
                    "weighted_multi_objective": "⚖️ Multiobjetivo Ponderado",
                    "distance_only": "📏 Apenas Distância",
                    "penalty_based": "⚠️ Baseado em Penalidades",
                    "priority_aware": "🚨 Foco em Prioridade"
                }
                return mapping.get(ftype, ftype.replace("_", " ").title())

            experiments['fitness'] = experiments['config'].apply(get_fitness_label)

            # === FILTROS ===
            st.markdown("### 🔍 Filtros")
            all_types = sorted(experiments['fitness'].unique())
            selected_types = st.multiselect(
                "Filtrar por Abordagem/Fitness:",
                options=all_types,
                default=all_types
            )
            
            # Aplica Filtro
            if selected_types:
                filtered_df = experiments[experiments['fitness'].isin(selected_types)].copy()
            else:
                filtered_df = experiments.copy()

            # === MÉTRICAS (Usando dados filtrados) ===
            st.divider()
            
            if not filtered_df.empty:
                # Filtrar apenas completados para métricas de eficiência
                completed_df = filtered_df[filtered_df['status'] == 'completed']
                
                if not completed_df.empty:
                    best_fitness = completed_df['best_fitness'].min()
                    avg_gens = completed_df['generations_run'].mean()
                else:
                    best_fitness = 0.0
                    avg_gens = 0
                
                # Total deve refletir o que está na tabela (completados + running + failed)
                # SE o usuário quiser apenas sucesso, ele deve filtrar. 
                # PORÉM, o user reclamou que o número estava errado (200).
                # Vou exibir "Total (Sucesso)" para ser mais claro.
                total_runs = len(filtered_df)
                success_runs = len(completed_df)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Melhor Fitness (Global)</h3>
                        <h1>{best_fitness:.2f}</h1>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Execuções (Sucesso / Total)</h3>
                        <h1>{success_runs} <small>/{total_runs}</small></h1>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Média de Gerações</h3>
                        <h1>{avg_gens:.0f}</h1>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("Nenhum dado encontrado com os filtros selecionados.")

            st.markdown("### 🕒 Histórico Detalhado")
            
            # Cálculo de Ganho na Tabela
            def calc_gain(row):
                if not row.get('result_details'): return 0.0
                try:
                    details = row['result_details']
                    if isinstance(details, str):
                        details = json.loads(details)
                    
                    init = details.get('initial_fitness', 0)
                    final = row['best_fitness']
                    if init > 0:
                        return ((init - final) / init) * 100
                    return 0.0
                except:
                    return 0.0

            def get_initial_fitness(row):
                if not row.get('result_details'): return 0.0
                try:
                    details = row['result_details']
                    if isinstance(details, str):
                        details = json.loads(details)
                    return details.get('initial_fitness', 0.0)
                except:
                    return 0.0

            # Ações de Limpeza e Atualização
            c_clean1, c_clean2, c_refresh, c_spacer = st.columns([1, 1, 1, 3])
            
            with c_refresh:
                if st.button("🔄 Atualizar"):
                    st.rerun()

            with c_clean1:
                if st.button("🧹 Limpar Falhas"):
                    try:
                        requests.delete(f"{API_URL}/experiments/failed")
                        st.rerun()
                    except:
                        st.error("Erro ao limpar falhas.")
            with c_clean2:
                if st.button("🗑️ Limpar Tudo", type="primary"):
                    try:
                        requests.delete(f"{API_URL}/experiments/all")
                        st.rerun()
                    except:
                        st.error("Erro ao limpar tudo.")

            # Aplica calculos no DF filtrado para exibição
            filtered_df['ganho_pct'] = filtered_df.apply(calc_gain, axis=1)
            filtered_df['fitness_inicial'] = filtered_df.apply(get_initial_fitness, axis=1)
            
            # Formatando para exibição
            display_df = filtered_df[['id', 'status', 'created_at', 'fitness', 'fitness_inicial', 'best_fitness', 'ganho_pct', 'execution_time', 'generations_run']].copy()
            # Aplica conversão de fuso horário
            display_df['created_at'] = display_df['created_at'].apply(format_date_br)
            # Remove formatting from numerical columns to fix sorting
            display_df['fitness_inicial'] = display_df['fitness_inicial'].map('{:.2f}'.format)
            display_df['best_fitness'] = display_df['best_fitness'].map('{:.2f}'.format)
            
            # Ordenação padrão pelo ganho (decrescente) se não houver ordenação na UI
            # Mas o st.dataframe tem ordenação interativa, então apenas preparamos os dados
            
            event = st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": "ID",
                    "status": "Status",
                    "created_at": "Data (BRT)",
                    "fitness": st.column_config.TextColumn(
                        "Abordagem/Fitness ℹ️",
                        help="""
⚖️ **Multiobjetivo**: Equilíbrio ótimo entre Tempo, Custo e Prioridades.

📏 **Distância**: Foca apenas na menor quilometragem total percorrida.

🚨 **Prioridade**: Prioriza atendimentos críticos (Prio 1) acima de tudo.

⚠️ **Penalidades**: Foca em não violar limites de capacidade ou autonomia.
                        """
                    ),
                    "best_fitness": "Melhor Fitness",
                    "fitness_inicial": "Fit. Inicial",
                    "ganho_pct": st.column_config.NumberColumn(
                        "Ganho (%)",
                        format="%.1f%%"
                    ),
                    "execution_time": st.column_config.NumberColumn(
                        "Tempo (s)",
                        format="%.1f s"
                    ),
                    "generations_run": "Gerações"
                },
                on_select="rerun",
                selection_mode="single-row",
                key="history_table"
            )
            
            if len(event.selection.rows):
                selected_row = event.selection.rows[0]
                selected_id = int(display_df.iloc[selected_row]['id'])
                
                # Evita loop de redirecionamento (Trap)
                if 'last_redirected_id' not in st.session_state:
                    st.session_state.last_redirected_id = None
                
                if selected_id != st.session_state.last_redirected_id:
                    st.session_state.last_redirected_id = selected_id
                    st.session_state.analyze_exp_id = selected_id
                    st.session_state.nav_page = "Análise Detalhada"
                    st.rerun()

        else:
            st.info("Nenhuma execução registrada. Inicie um novo experimento.")
            
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        st.error("⚠️ Não foi possível conectar à API. Certifique-se de que o backend está rodando.")
        st.code("uvicorn src.api.main:app --reload")
    except (requests.exceptions.JSONDecodeError, requests.exceptions.HTTPError) as e:
        st.error(f"⚠️ API retornou resposta inválida. Aguarde a inicialização ou verifique o backend: {e}")

elif page == "Nova Execução":
    st.title("🚀 Configurar Experimento")

    # Busca configuração padrão e opções da API
    api_defaults = get_default_config()
    config_opts = get_config_options()

    defaults = {
        "population_size": api_defaults.get("population_size", 100),
        "max_generations": api_defaults.get("max_generations", 200),
        "crossover_rate": api_defaults.get("crossover_rate", 0.9),
        "mutation_rate": api_defaults.get("mutation_rate", 0.15),
        "scenario_name": api_defaults.get("scenario", "large"),
        "num_vehicles": api_defaults.get("num_vehicles", 3),
        "vehicle_capacity": api_defaults.get("vehicle_capacity", 100.0),
        "vehicle_speed": api_defaults.get("vehicle_speed", 40.0),
        "vehicle_max_distance": api_defaults.get("vehicle_max_distance", 200.0),
        "selection_method": api_defaults.get("selection_method", "tournament"),
        "crossover_method": api_defaults.get("crossover_method", "order_crossover"),
        "mutation_method": api_defaults.get("mutation_method", "inversion"),
        "elite_size": api_defaults.get("elite_size", 2),
        "tournament_size": api_defaults.get("tournament_size", 3),
        "stagnation_limit": api_defaults.get("stagnation_limit", 50),
        "heuristic_init_ratio": api_defaults.get("heuristic_init_ratio", 0.2),
        "w_distance": api_defaults.get("w_distance", 1.0),
        "w_priority": api_defaults.get("w_priority", 10.0),
        "w_capacity": api_defaults.get("w_capacity", 100.0),
        "w_autonomy": api_defaults.get("w_autonomy", 100.0),
        "w_window": api_defaults.get("w_window", 50.0)
    }

    # Tentar carregar última configuração (sobrescreve defaults da API)
    try:
        last_exp = requests.get(f"{API_URL}/experiments/latest").json()
        if last_exp and "config" in last_exp:
            lc = last_exp["config"]
            # Atualiza com segurança de tipos
            defaults["population_size"] = int(lc.get("population_size", defaults["population_size"]))
            defaults["max_generations"] = int(lc.get("max_generations", defaults["max_generations"]))
            defaults["crossover_rate"] = float(lc.get("crossover_rate", defaults["crossover_rate"]))
            defaults["mutation_rate"] = float(lc.get("mutation_rate", defaults["mutation_rate"]))
            defaults["scenario_name"] = lc.get("scenario_name", lc.get("scenario", defaults["scenario_name"]))
            defaults["num_vehicles"] = int(lc.get("num_vehicles", defaults["num_vehicles"]))
            defaults["vehicle_capacity"] = float(lc.get("vehicle_capacity", defaults["vehicle_capacity"]))
            defaults["vehicle_speed"] = float(lc.get("vehicle_speed", defaults["vehicle_speed"]))
            defaults["vehicle_max_distance"] = float(lc.get("vehicle_max_distance", defaults["vehicle_max_distance"]))
            defaults["selection_method"] = lc.get("selection_method", defaults["selection_method"])
            defaults["crossover_method"] = lc.get("crossover_method", defaults["crossover_method"])
            defaults["mutation_method"] = lc.get("mutation_method", defaults["mutation_method"])
            defaults["elite_size"] = int(lc.get("elite_size", defaults["elite_size"]))
            defaults["tournament_size"] = int(lc.get("tournament_size", defaults["tournament_size"]))
    except Exception:
        pass # Falha silenciosa, usa defaults da API

    with st.container():
        st.subheader("⚙️ Configuração do Experimento")
        
        # Tabs para organizar
        tab1, tab2, tab3, tab4 = st.tabs(["Evolução (AG)", "Veículos e Cenário", "Estratégias Avançadas", "Pesos & Objetivos"])
        
        with tab1:
            # Layout mais denso: 4 colunas em vez de 2x2
            c_gen1, c_gen2, c_gen3, c_gen4 = st.columns(4)
            with c_gen1:
                pop_size = st.number_input("População", min_value=10, max_value=2000, value=defaults["population_size"])
            with c_gen2:
                generations = st.number_input("Gerações", min_value=10, max_value=5000, value=defaults["max_generations"])
            with c_gen3:
                crossover_rate = st.number_input("Taxa Crossover", 0.0, 1.0, defaults["crossover_rate"], step=0.05)
            with c_gen4:
                mutation_rate = st.number_input("Taxa Mutação", 0.0, 1.0, defaults["mutation_rate"], step=0.01)
            
        with tab2:
            # Linha única para configuração básica de veículos
            c_scen, c_nveh, c_cap, c_spd, c_dist = st.columns([1.5, 1, 1, 1, 1])

            with c_scen:
                # Encontrar index do cenário salvo
                # Mapeamento Reverso e Direto
                scenario_map = {
                    "small": "Pequeno", "medium": "Médio", "large": "Grande", "critical": "Crítico",
                    "Pequeno": "small", "Médio": "medium", "Grande": "large", "Crítico": "critical"
                }
                
                # Lista de opções em Português
                scenarios_opts_pt = ["Pequeno", "Médio", "Grande", "Crítico"]
                
                defaults_scen_pt = scenario_map.get(defaults["scenario_name"], "Grande")
                
                try:
                    scen_idx = scenarios_opts_pt.index(defaults_scen_pt)
                except:
                    scen_idx = 2 # Grande
                    
                scenario_pt = st.selectbox("Cenário", scenarios_opts_pt, index=scen_idx)
                
                # Converte de volta para inglês para usar na API/Logic
                scenario = scenario_map.get(scenario_pt, "large")
            with c_nveh:
                num_vehicles = st.number_input("Qtd. Veículos", 1, 20, defaults["num_vehicles"])
            with c_cap:
                v_cap = st.number_input("Capacidade", 10.0, 1000.0, defaults["vehicle_capacity"])
            with c_spd:
                v_speed = st.number_input("Vel (km/h)", 10.0, 120.0, defaults["vehicle_speed"])
            with c_dist:
                v_dist = st.number_input("Autonomia", 10.0, 2000.0, defaults["vehicle_max_distance"])

            # Preview do Mapa em Container Expansível
            with st.expander("📍 Visualizar Mapa do Cenário", expanded=True):
                 try:
                     scenario_res = requests.get(f"{API_URL}/scenarios/{scenario}")
                     
                     if scenario_res.status_code == 200:
                         points_data = scenario_res.json()
                         
                         import folium
                         from streamlit_folium import st_folium
                         from folium.plugins import FloatImage

                         # Cores (iguais ao Pygame)
                         COLOR_DEPOT = '#007BFF'  # Azul
                         COLOR_CRITICAL = '#DC3545'  # Vermelho
                         COLOR_URGENT = '#FF8000'    # Laranja
                         COLOR_REGULAR = '#28A745'   # Verde
                         
                         # Centro do mapa
                         lats = [p['lat'] for p in points_data]
                         lons = [p['lon'] for p in points_data]
                         center = [sum(lats)/len(lats), sum(lons)/len(lons)]
                         
                         # Mapa com estilo Dark (CartoDB Dark Matter)
                         m = folium.Map(location=center, zoom_start=11 if scenario == 'small' else 9, tiles='CartoDB dark_matter')
                         
                         # Adicionando Pontos
                         for p in points_data:
                             tooltip_text = f"<b>{p['name']}</b><br>ID: {p['id']}<br>Prioridade: {p.get('priority', '-')}"
                             
                             if p['type'] == 'depot':
                                 folium.Marker(
                                     [p['lat'], p['lon']],
                                     tooltip="Depósito Central",
                                     icon=folium.Icon(color='blue', icon='home', prefix='fa')
                                 ).add_to(m)
                             else:
                                 # Define cor baseada na prioridade
                                 prio = p.get('priority', 3)
                                 color = COLOR_REGULAR
                                 radius = 6
                                 if prio == 1: 
                                     color = COLOR_CRITICAL
                                     radius = 9
                                 elif prio == 2: 
                                     color = COLOR_URGENT
                                     radius = 7
                                     
                                 folium.CircleMarker(
                                     location=[p['lat'], p['lon']],
                                     radius=radius,
                                     color=color,
                                     fill=True,
                                     fill_color=color,
                                     fill_opacity=0.8,
                                     tooltip=tooltip_text
                                 ).add_to(m)

                         # Legenda Flutuante (HTML)
                         legend_html = '''
                             <div style="
                             position: fixed; 
                             bottom: 50px; left: 50px; width: 150px; height: 130px; 
                             background-color: rgba(30, 41, 55, 0.9); z-index:9999; font-size:12px;
                             border: 2px solid #00e676; border-radius: 10px; padding: 10px; color: white;">
                             <b>Legenda</b><br>
                             <i class="fa fa-home" style="color:#38aadd"></i>&nbsp; Depósito<br>
                             <i class="fa fa-circle" style="color:#DC3545"></i>&nbsp; Crítico<br>
                             <i class="fa fa-circle" style="color:#FF8000"></i>&nbsp; Urgente<br>
                             <i class="fa fa-circle" style="color:#28A745"></i>&nbsp; Regular
                             </div>
                             '''
                         m.get_root().html.add_child(folium.Element(legend_html))
                         
                         # Renderiza com altura reduzida para ser compacto
                         st_folium(m, width=None, height=350, key=f"preview_map_{scenario}")
                         st.caption(f"Total de Pontos: {len(points_data)}")

                 except Exception as e:
                     st.warning(f"Não foi possível carregar o preview do mapa. {e}")

        with tab3:
            col_sel, col_cross = st.columns(2)

            with col_sel:
                st.markdown("#### Seleção")

                sel_opts = config_opts.get("selection_methods", ["tournament"])
                try:
                    sel_idx = sel_opts.index(defaults["selection_method"])
                except:
                    sel_idx = 0

                selection = st.selectbox(
                    "Método de Seleção",
                    options=sel_opts,
                    index=sel_idx
                )
                
                # Parâmetros condicionais de Seleção
                tournament_size = 3
                truncation_threshold = 0.5
                boltzmann_temp = 100.0
                steady_state_ratio = 0.2
                elite_size = defaults["elite_size"]
                
                if selection == 'tournament':
                    tournament_size = st.number_input("Tamanho do Torneio", 2, 10, defaults["tournament_size"])
                elif selection == 'truncation':
                    truncation_threshold = st.slider("Limiar de Truncamento", 0.1, 1.0, 0.5)
                elif selection == 'boltzmann':
                    boltzmann_temp = st.number_input("Temperatura Inicial (Boltzmann)", 1.0, 1000.0, 100.0)
                elif selection == 'steady_state':
                    steady_state_ratio = st.slider("Taxa de Substituição (Steady State)", 0.05, 1.0, 0.2)
                
                st.divider()
                st.markdown("#### Substituição & Elitismo")

                replace_opts = config_opts.get("replacement_strategies", ["elitist"])
                try:
                    rep_idx = replace_opts.index(defaults.get("replacement_strategy", "elitist"))
                except:
                    rep_idx = 0

                replacement = st.selectbox(
                    "Estratégia de Substituição",
                    options=replace_opts,
                    index=rep_idx,
                    help="Determina como a nova geração substitui a antiga."
                )
                
                if replacement == 'elitist':
                    elite_size = st.number_input("Tamanho da Elite", 0, pop_size//2, defaults.get("elite_size", 2))
                else:
                    elite_size = defaults.get("elite_size", 2)


            with col_cross:
                st.markdown("#### Crossover & Mutação")

                cross_opts = config_opts.get("crossover_methods", ["order_crossover"])
                try:
                     cross_idx = cross_opts.index(defaults["crossover_method"])
                except:
                     cross_idx = 0

                crossover = st.selectbox(
                    "Método de Crossover",
                    options=cross_opts,
                    index=cross_idx
                )

                # Somente mutações combinatórias para este problema
                mut_opts = config_opts.get("mutation_methods", ["inversion"])
                try:
                    mut_idx = mut_opts.index(defaults["mutation_method"])
                except:
                    mut_idx = 0

                mutation = st.selectbox(
                    "Método de Mutação",
                    options=mut_opts,
                    index=mut_idx
                )
                
            st.divider()
            st.markdown("#### Diversidade & Convergência")

            c_div1, c_div2 = st.columns(2)
            with c_div1:
                heuristic_init = st.slider("Inicialização Heurística (%)", 0.0, 1.0, defaults.get("heuristic_init_ratio", 0.2), help="Proporção da população inicial gerada com heurística (Gulosa) versus Aleatória.")
            with c_div2:
                stagnation_limit = st.number_input("Limite de Estagnação", 5, 500, defaults.get("stagnation_limit", 50), help="Número de gerações sem melhoria antes de parar")

        with tab4:
            st.info("Ajuste a importância de cada objetivo na função de fitness.")
            # Mapeamento reverso para exibição amigável
            fitness_mapping = {
                "weighted_multi_objective": "⚖️ Multiobjetivo Ponderado",
                "distance_only": "📏 Apenas Distância",
                "penalty_based": "⚠️ Baseado em Penalidades",
                "priority_aware": "🚨 Foco em Prioridade"
            }
            
            fitness_opts_keys = config_opts.get("fitness_types", ["weighted_multi_objective"])
            fitness_opts_labels = [fitness_mapping.get(k, k.replace('_', ' ').title()) for k in fitness_opts_keys]
            
            try:
                current_ft = defaults.get("fitness_type", "weighted_multi_objective")
                fitness_idx = fitness_opts_keys.index(current_ft)
            except:
                fitness_idx = 0
                
            selected_label = st.selectbox("Tipo de Fitness", fitness_opts_labels, index=fitness_idx)
            
            # Recupera a chave original para usar na config
            # Assumindo que a ordem é preservada ou buscando por valor
            fitness_type = fitness_opts_keys[fitness_opts_labels.index(selected_label)]
            
            if fitness_type == "weighted_multi_objective":
                c1, c2 = st.columns(2)
                with c1:
                    w_dist = st.number_input("Peso Distância", 0.0, 100.0, defaults.get("w_distance", 1.0))
                    w_prio = st.number_input("Peso Prioridade", 0.0, 1000.0, defaults.get("w_priority", 10.0))
                with c2:
                    w_cap = st.number_input("Penalidade Capacidade", 0.0, 1000.0, defaults.get("w_capacity", 100.0))
                    w_auto = st.number_input("Penalidade Autonomia", 0.0, 1000.0, defaults.get("w_autonomy", 100.0))
                    w_wind = st.number_input("Penalidade Janela Tempo", 0.0, 1000.0, defaults.get("w_window", 50.0))
            else:
                # Usa valores padrão da API para outros tipos de fitness
                w_dist = defaults.get("w_distance", 1.0)
                w_prio = defaults.get("w_priority", 10.0)
                w_cap = defaults.get("w_capacity", 100.0)
                w_auto = defaults.get("w_autonomy", 100.0)
                w_wind = defaults.get("w_window", 50.0)


        
    config = {
        "population_size": pop_size,
        "max_generations": generations,
        "crossover_rate": crossover_rate,
        "mutation_rate": mutation_rate,
        "selection_method": selection,
        "crossover_method": crossover,
        "mutation_method": mutation,
        "replacement_strategy": replacement,
        "fitness_type": fitness_type,
        "num_vehicles": num_vehicles,
        "vehicle_capacity": v_cap,
        "vehicle_speed": v_speed,
        "vehicle_max_distance": v_dist,
        "scenario": scenario,
        "elite_size": elite_size,
        "tournament_size": tournament_size,
        "truncation_threshold": truncation_threshold,
        "boltzmann_temperature": boltzmann_temp,
        "steady_state_ratio": steady_state_ratio,
        "heuristic_init_ratio": heuristic_init,
        "w_distance": w_dist,
        "w_priority": w_prio,
        "w_capacity": w_cap,
        "w_autonomy": w_auto,
        "w_window": w_wind,
        "stagnation_limit": stagnation_limit
    }
    
    # Colunas assimétricas para alinhar os botões à esquerda
    col_act1, col_act2, col_spacer = st.columns([1, 1.2, 3])
    
    with col_act1:
        # Verifica se está rodando no Docker
        is_docker = os.getenv("SERVICE_TYPE") is not None
        
        if is_docker:
            st.warning("⚠️ Visualização indisponível no Docker (apenas local)")
        else:
            if st.button("🎮 Executar Visualmente (Pygame)"):
                run_pygame_visual(config)
            
    with col_act2:
        if st.button("⚡ Executar em Background (API)"):
            try:
                res = requests.post(f"{API_URL}/run", json=config)
                if res.status_code == 200:
                    # Mensagem de sucesso abaixo dos botões
                    pass 
                else:
                    st.error(f"Erro: {res.text}")
            except Exception as e:
                st.error(f"Erro de conexão: {e}")
    
    # Exibe sucesso fora das colunas para não quebrar o layout
    if 'res' in locals() and res.status_code == 200:
        st.success(f"Experimento iniciado! ID: {res.json()['id']}")


elif page == "Análise Detalhada":
    st.title("📈 Análise de Resultados")
    
    
    # Busca lista de experimentos para o Grid
    try:
        exp_list_res = requests.get(f"{API_URL}/experiments")
        if exp_list_res.status_code == 200:
            df_exps = pd.DataFrame(exp_list_res.json())
        else:
            df_exps = pd.DataFrame()
    except:
        df_exps = pd.DataFrame()

    selected_id_from_grid = None
    
    if not df_exps.empty:
        # Prepara DF para exibição
        df_display = df_exps[['id', 'status', 'created_at', 'best_fitness', 'generations_run']].copy()
        df_display['created_at'] = df_display['created_at'].apply(format_date_br)
        df_display['best_fitness'] = df_display['best_fitness'].apply(lambda x: f"{x:.2f}" if x else "-")
        
        # Adiciona coluna de Seleção
        df_display.insert(0, "Selecionar", False)
        
        st.markdown("##### Selecione um Experimento:")
        
        # Grid Editável (Checkbox)
        edited_df = st.data_editor(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Selecionar": st.column_config.CheckboxColumn(
                    "Selecionar",
                    help="Marque para visualizar os detalhes",
                    default=False,
                )
            },
            disabled=["id", "status", "created_at", "best_fitness", "generations_run"],
            key="analysis_editor",
            height=250
        )
        
        # Verifica qual linha foi marcada
        selected_rows = edited_df[edited_df["Selecionar"] == True]
        
        if not selected_rows.empty:
            # Pega o ID da última seleção (caso marque vários, foca num só ou no último clicado)
            # Para UX melhor, ideal seria radio button behavior, mas checkbox serve.
            selected_id_from_grid = int(selected_rows.iloc[-1]['id'])
    else:
        st.info("Nenhum experimento encontrado.")


    # Lógica de ID: 
    # 1. Se clicou no grid, usa do grid
    # 2. Se veio do Dashboard (session_state), usa dele (mas grid tem prioridade se clicado agora)
    # 3. Fallback para input manual se necessário (opcional, aqui vou manter escondido se tiver grid)
    
    final_exp_id = None
    
    if selected_id_from_grid:
        final_exp_id = selected_id_from_grid
        # Atualiza session state para sincronia
        st.session_state.analyze_exp_id = final_exp_id
    elif 'analyze_exp_id' in st.session_state:
        final_exp_id = st.session_state.analyze_exp_id

    # Se ainda não tem ID selecionado, tenta o último
    if final_exp_id is None and not df_exps.empty:
        # Opcional: Selecionar o primeiro automaticamente?
        # final_exp_id = df_display.iloc[0]['id']
        pass

    exp_id = final_exp_id
    load_current = False
    
    if exp_id:
        # Exibe controles apenas se houver um ID selecionado
        c_status, c_actions = st.columns([2, 3])
        with c_status:
             st.markdown(f"**Experimento Selecionado:** `{exp_id}`")
        
        with c_actions:
             c_reload, c_del = st.columns([1, 1])
             with c_reload:
                 if st.button("🔄 Recarregar", key="btn_reload_det"):
                     load_current = True
             with c_del:
                 if st.button("🗑️ Excluir", key="btn_del_exp", type="primary"):
                     try:
                        requests.delete(f"{API_URL}/experiments/{exp_id}")
                        st.success(f"Experimento {exp_id} excluído!")
                        # Limpa estado
                        st.session_state.nav_page = "Dashboard"
                        if 'loaded_exp_id' in st.session_state: del st.session_state['loaded_exp_id']
                        if 'analyze_exp_id' in st.session_state: del st.session_state['analyze_exp_id']
                        st.rerun()
                     except:
                        st.error("Erro ao excluir.")

        # Auto-load se veio do grid ou já estava carregado
        if selected_id_from_grid or ('loaded_exp_id' in st.session_state and st.session_state.loaded_exp_id == exp_id):
             load_current = True
    else:
        st.info("👆 Selecione um experimento na tabela acima para ver os detalhes.")

    # Lógica de Estado para manter dados visíveis
    if load_current:
        st.session_state.loaded_exp_id = exp_id
    
    # Se navegação veio do dashboard, já carrega
    if 'analyze_exp_id' in st.session_state and st.session_state.analyze_exp_id == exp_id:
         st.session_state.loaded_exp_id = exp_id
         # Limpa flag de navegação para permitir mudar ID manualmente sem forçar reload
         del st.session_state.analyze_exp_id

    if 'loaded_exp_id' in st.session_state and st.session_state.loaded_exp_id == exp_id:
        try:
            res = requests.get(f"{API_URL}/experiments/{exp_id}")
            if res.status_code == 200:
                data = res.json()
                
                # --- Cabeçalho com Métricas Principais ---
                st.divider()
                m1, m2, m3, m4, m5 = st.columns(5)
                
                # Garante que result_details é dict antes de acessar .get
                res_details = data.get('result_details')
                initial_fit = None
                if isinstance(res_details, dict):
                    initial_fit = res_details.get('initial_fitness')
                final_fit = data['best_fitness']
                gain = 0.0
                gain_pct = 0.0
                
                if initial_fit and final_fit:
                    gain = initial_fit - final_fit
                    if initial_fit > 0:
                        gain_pct = (gain / initial_fit) * 100
                
                with m1: st.metric("Status", data['status'])
                with m2: st.metric("Fitness Inicial", f"{initial_fit:.2f}" if initial_fit else "-")
                with m3: st.metric("Fitness Final", f"{final_fit:.2f}" if final_fit else "-", delta=f"{gain_pct:.1f}%" if gain_pct > 0 else None, delta_color="inverse")
                with m4: st.metric("Ganho Real", f"{gain:.2f}")
                with m5: st.metric("Gerações", data['generations_run'] or "-")
                
                # --- Tabs de Detalhes ---
                tab_config, tab_results, tab_json = st.tabs(["⚙️ Configuração Utilizada", "📍 Resultados & Rotas", "🔍 JSON Completo"])
                
                with tab_config:
                    cfg = data['config']
                    st.subheader("Parâmetros da Execução")
                    # ... rest of config display ...
                    
                    # Organizando em categorias visualmente agradáveis
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**Geral**")
                        st.write(f"- População: `{cfg.get('population_size')}`")
                        st.write(f"- Max Gerações: `{cfg.get('max_generations')}`")
                        st.write(f"- Taxa Crossover: `{cfg.get('crossover_rate')}`")
                        st.write(f"- Taxa Mutação: `{cfg.get('mutation_rate')}`")
                        st.write(f"- Inicialização Heurística: `{cfg.get('heuristic_init_ratio') if cfg.get('heuristic_init_ratio') else '0.0'}`")
                        
                        st.markdown("**Veículos e Cenário**")
                        st.write(f"- Cenário: `{cfg.get('scenario')}`")
                        st.write(f"- Veículos: `{cfg.get('num_vehicles')}`")
                        st.write(f"- Capacidade: `{cfg.get('vehicle_capacity')}`")
                        st.write(f"- Autonomia: `{cfg.get('vehicle_max_distance')}` km")
                        st.write(f"- Velocidade: `{cfg.get('vehicle_speed')}` km/h")

                    with c2:
                        st.markdown("**Estratégias**")
                        st.write(f"- Seleção: `{cfg.get('selection_method')}`")
                        if cfg.get('selection_method') == 'tournament':
                            st.write(f"  - Tamanho Torneio: `{cfg.get('tournament_size')}`")
                        
                        st.write(f"- Crossover: `{cfg.get('crossover_method')}`")
                        st.write(f"- Mutação: `{cfg.get('mutation_method')}`")
                        
                        st.write(f"- Substituição: `{cfg.get('replacement_strategy')}`")
                        if cfg.get('replacement_strategy') == 'elitist':
                            st.write(f"  - Elitismo: `{cfg.get('elite_size')}`")
                            
                        st.write(f"- Fitness: `{cfg.get('fitness_type')}`")
                        st.write(f"- Estagnação Limite: `{cfg.get('stagnation_limit')}`")
                        
                        st.markdown("**Pesos / Penalidades**")
                        st.write(f"- Distância: `{cfg.get('w_distance')}`")
                        st.write(f"- Prioridade: `{cfg.get('w_priority')}`")
                        st.write(f"- Capacidade: `{cfg.get('w_capacity')}`")
                        st.write(f"- Autonomia: `{cfg.get('w_autonomy')}`")
                        st.write(f"- Janela Tempo: `{cfg.get('w_window')}`")
                        
                with tab_results:
                    if data['result_details']:
                        details = data['result_details']
                        # Compatibilidade: Se for lista (legado), assume que são as rotas
                        if isinstance(details, list):
                            routes = details
                        else:
                            routes = details.get('routes', [])
                        
                        # --- DEBUG: Verificando Dados do Mapa ---
                        with st.expander("🛠️ Debug Mapa", expanded=False):
                            st.write(f"Total Rotas: {len(routes)}")
                            if routes:
                                st.write("Exemplo Rota 0 Points:", routes[0].get('points'))
                        
                        # --- TENTA RECONSTRUIR O MAPA ---
                        try:
                            # 1. Recupera o Cenario
                            scenario_name = cfg.get('scenario', 'large') # fallback
                            if 'scenario_name' in cfg: scenario_name = cfg['scenario_name']
                            
                            scen_res = requests.get(f"{API_URL}/scenarios/{scenario_name}")
                            if scen_res.status_code == 200:
                                points_db = scen_res.json()
                                # Mapa de ID (str) -> Dados
                                id_map = {str(p['id']): p for p in points_db}
                                
                                # Verifica se há rotas sem dados de trajeto (pontos ou stops)
                                missing_data = any(not r.get('points') and not r.get('stops') for r in routes)
                                if missing_data:
                                    st.warning("⚠️ Este experimento contém rotas sem dados de trajeto processados. A visualização pode estar incompleta.")

                                import folium
                                from streamlit_folium import st_folium
                                
                                # Cores para rotas
                                COLORS = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
                                
                                # Encontra o depósito
                                depot_pt = next((p for p in points_db if p['type'] == 'depot'), None)
                                
                                # MAPA BASE: CartoDB Dark Matter (Requisito: Fundo Escuro)
                                # MAPA BASE: CartoDB Dark Matter (Requisito: Fundo Escuro)
                                # Inicializa com Foco no ESTADO DE SÃO PAULO (Pedido do Usuário - Zoom Fixo)
                                # Centro aproximado de SP: -22.5, -48.0
                                m_res = folium.Map(location=[-22.5, -48.0], zoom_start=7, tiles='CartoDB dark_matter')
                                
                                # 1. Desenha TODOS os pontos com MARCADORES (Pins)
                                for pt in points_db:
                                    tooltip_text = f"{pt['name']}<br>ID: {pt['id']}"
                                    
                                    if pt['type'] == 'depot':
                                        folium.Marker(
                                            [pt['lat'], pt['lon']], 
                                            tooltip="Depósito Central",
                                            icon=folium.Icon(color='blue', icon='warehouse', prefix='fa')
                                        ).add_to(m_res)
                                    else:
                                        # Cor e Ícone baseada na prioridade (igual route_visualizer)
                                        priority = pt.get('priority', 3)
                                        if priority == 1:
                                            color = 'red'
                                        elif priority == 2:
                                            color = 'orange'
                                        else:
                                            color = 'green'
                                            
                                        folium.Marker(
                                            [pt['lat'], pt['lon']], 
                                            tooltip=tooltip_text,
                                            icon=folium.Icon(color=color, icon='hospital', prefix='fa')
                                        ).add_to(m_res)
                                
                                import folium.plugins as plugins
                                
                                all_route_points = []
                                
                                # 2. Desenha as Rotas
                                for i, r in enumerate(routes):
                                    # Tenta recuperar IDs dos pontos (Compatibilidade)
                                    path_ids = r.get('points')
                                    if not path_ids and 'stops' in r:
                                        # Fallback: Extrai IDs de 'stops' (experiments 396/398)
                                        path_ids = [s.get('id') for s in r.get('stops', [])]
                                        
                                    if not path_ids: continue # Pula rotas vazias

                                    route_color = COLORS[i % len(COLORS)]
                                    
                                    coords = []
                                    # Início no Depósito
                                    if depot_pt:
                                        coords.append([depot_pt['lat'], depot_pt['lon']])
                                        all_route_points.append([depot_pt['lat'], depot_pt['lon']])
                                    
                                    for pid in path_ids:
                                        # Lookup seguro com string
                                        pt = id_map.get(str(pid))
                                        if pt:
                                            c = [pt['lat'], pt['lon']]
                                            coords.append(c)
                                            all_route_points.append(c)
                                    
                                    # Fim no Depósito
                                    if depot_pt:
                                        coords.append([depot_pt['lat'], depot_pt['lon']])
                                    
                                    # Cria grupo para a rota (Camada Interativa)
                                    route_name = f"Rota {i+1} (Veículo {r.get('vehicle_id')})"
                                    route_fg = folium.FeatureGroup(name=route_name)
                                    
                                    if len(coords) > 1:
                                        # 1. Linha Sólida Base
                                        folium.PolyLine(
                                            locations=coords,
                                            weight=3,
                                            color=route_color,
                                            opacity=0.8,
                                            tooltip=f"Rota Base Veículo {r.get('vehicle_id')}"
                                        ).add_to(route_fg)

                                        # 2. AntPath por cima (Animação)
                                        plugins.AntPath(
                                            locations=coords,
                                            delay=1000,
                                            pulse_color=route_color,
                                            hardware_acceleration=False,
                                            tooltip=f"Fluxo Veículo {r.get('vehicle_id')}"
                                        ).add_to(route_fg)
                                    
                                    # Adiciona grupo ao mapa
                                    route_fg.add_to(m_res)
                                
                                # REMOVIDO: Ajuste de Zoom Automático (fit_bounds)
                                # O usuário solicitou zoom fixo no estado de SP.
                                # all_points_coords = [[p['lat'], p['lon']] for p in points_db]
                                # if all_points_coords:
                                #     m_res.fit_bounds(all_points_coords, padding=(50, 50))
                                
                                # Adiciona controle de camadas (LayerControl) para ligar/desligar rotas
                                folium.LayerControl(collapsed=False).add_to(m_res)
                                
                                # 3. LEGENDA ESCURA (Apenas Marcadores agora) - LADO ESQUERDO
                                legend_html = '''
                                <div style="position: fixed; 
                                            bottom: 30px; left: 20px; 
                                            width: 150px;
                                            background-color: #1a1a1a; 
                                            color: #ffffff;
                                            border: 2px solid #555; 
                                            box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
                                            z-index: 1000; 
                                            font-size: 13px;
                                            padding: 12px;
                                            border-radius: 8px;
                                            font-family: sans-serif;">
                                    <h5 style="margin: 0 0 10px 0; color: white; border-bottom: 1px solid #444; padding-bottom: 5px;">Legenda</h5>
                                    <div style="margin-bottom: 3px;"><span style="color: #3388ff;">●</span> Depósito</div>
                                    <div style="margin-bottom: 3px;"><span style="color: #ff3333;">●</span> Crítico</div>
                                    <div style="margin-bottom: 3px;"><span style="color: #ff9900;">●</span> Urgente</div>
                                    <div style="margin-bottom: 3px;"><span style="color: #33cc33;">●</span> Regular</div>
                                    <hr style="margin: 8px 0; border-color: #444;">
                                    <div style="font-size: 11px; color: #aaa;">* Controle as rotas no menu de camadas (topo direito)</div>
                                </div>
                                '''
                                m_res.get_root().html.add_child(folium.Element(legend_html))

                                st.subheader("🗺️ Visualização Geográfica (Estilo Padrão)")
                                st_folium(m_res, width=None, height=600)
                                    
                        except Exception as e:
                            st.warning(f"Não foi possível gerar o mapa da rota: {e}")
                            
                        st.subheader("📋 Detalhes das Rotas")
                        
                        # Agrupa rotas por Veículo
                        from collections import defaultdict
                        vehicle_routes = defaultdict(list)
                        for r in routes:
                            vid = r.get('vehicle_id', '?')
                            vehicle_routes[vid].append(r)
                            
                        # Ordena por ID do veículo
                        sorted_vids = sorted(vehicle_routes.keys(), key=lambda x: int(x) if isinstance(x, int) or (isinstance(x, str) and x.isdigit()) else 999)

                        for vid in sorted_vids:
                            v_routes = vehicle_routes[vid]
                            
                            # Calcula totais do veículo
                            total_dist = sum(r.get('distance', 0) for r in v_routes)
                            total_load = sum(r.get('load', r.get('demand', 0)) for r in v_routes)
                            num_trips = len(v_routes)
                            
                            with st.expander(f"🚛 Veículo {vid} (Total: {total_dist:.2f} km | Carga: {total_load:.1f} | {num_trips} {'viagem' if num_trips==1 else 'viagens'})"):
                                for idx, route in enumerate(v_routes):
                                    dist_val = route.get('distance', 0)
                                    load_val = route.get('load', route.get('demand', 0))
                                    
                                    st.markdown(f"**Viagem {idx + 1}** (Dist: {dist_val:.2f} km, Carga: {load_val:.1f})")
                                    # Lógica Híbrida: Tenta usar IDs para buscar nomes, senão usa dados legados
                                    if 'points' in route and 'id_map' in locals():
                                        stops_text = []
                                        for pid in route['points']:
                                            p_data = id_map.get(str(pid)) # Garante string lookup
                                            if p_data:
                                                stops_text.append(f"{p_data['name']}")
                                            else:
                                                stops_text.append(f"ID:{pid}")
                                        st.caption(" ➝ ".join(stops_text))
                                        
                                    elif 'stops' in route:
                                        # Fallback para dados antigos
                                        stops_data = route['stops']
                                        if stops_data and isinstance(stops_data[0], str):
                                            st.caption(", ".join(stops_data))
                                        else:
                                            st.dataframe(route['stops'])
                                    else:
                                        st.warning("Dados de paradas não disponíveis.")
                                    st.divider()
                    else:
                        st.info("Detalhes dos resultados não disponíveis.")
                
                with tab_json:
                    try:
                        import json
                        
                        st.markdown("#### 🤖 Contexto para LLM")
                        st.caption("JSON estruturado para reprodução via API e análise por IA.")
                        
                        # Define todas as variáveis localmente
                        cfg = data.get('config', {})
                        details = data.get('result_details', {})
                        
                        # Trata caso legado onde details é lista
                        if isinstance(details, list):
                            routes = details
                            history_summary = []
                        else:
                            routes = details.get('routes', []) if isinstance(details, dict) else []
                            history_summary = details.get('history_summary', []) if isinstance(details, dict) else []
                        
                        # Monta payload para reprodução
                        llm_context = {
                            "api_endpoint": "POST http://localhost:8000/run",
                            "request_payload": cfg,
                            "response": {
                                "experiment_id": exp_id,
                                "status": data.get('status'),
                                "best_fitness": data.get('best_fitness'),
                                "generations_run": data.get('generations_run'),
                                "execution_time": data.get('execution_time'),
                                "initial_fitness": details.get('initial_fitness') if isinstance(details, dict) else None,
                                "routes": routes,
                                "evolution_history": history_summary
                            },
                            "instructions": "Para melhorar o fitness, ajuste os parâmetros em 'request_payload' e faça POST no endpoint. Compare os resultados."
                        }
                        
                        st.json(llm_context, expanded=True)
                        
                        st.download_button(
                            label="📥 Baixar JSON",
                            data=json.dumps(llm_context, indent=2, ensure_ascii=False),
                            file_name=f"experiment_{exp_id}_llm.json",
                            mime="application/json"
                        )
                        
                    except Exception as e:
                        import traceback
                        st.error(f"Erro ao gerar JSON LLM: {str(e)}")
                        st.code(traceback.format_exc())


            else:
                st.warning("Experimento não encontrado.")
        except Exception as e:
             st.error(f"Erro: {e}")

# =====================================================
# PÁGINA: GERADOR LOGÍSTICO
# =====================================================
elif page == "Gerador Logístico":
    st.header("🚚 Gerador Logístico")
    st.caption("Visualize rotas detalhadas por veículo com mapas e relatórios individuais.")
    
    # 1. Lista de experimentos completados
    try:
        res = requests.get(f"{API_URL}/experiments")
        if res.status_code == 200:
            experiments = res.json()
            # Filtra apenas completados
            completed = [e for e in experiments if e.get('status') == 'completed']
            
            if not completed:
                st.info("Nenhum experimento completado encontrado. Execute um experimento primeiro.")
            else:
                # Calcula eficiência e ordena (menor fitness por geração = melhor)
                # Calcula eficiência e ordena
                for e in completed:
                    initial_fit = e.get('initial_fitness') or e.get('best_fitness', 0) * 1.5 # Estima se não tiver
                    best_fit = e.get('best_fitness', 9999)
                    
                    # Melhora percentual (Maior = Melhor)
                    if initial_fit > 0:
                        e['improvement'] = ((initial_fit - best_fit) / initial_fit) * 100
                    else:
                        e['improvement'] = 0.0
                
                # Ordena por % de melhora (maior primeiro)
                completed_sorted = sorted(completed, key=lambda x: x['improvement'], reverse=True)
                
                # Dropdown rico com mais informações
                exp_options = {}
                for e in completed_sorted:
                    alg = e.get('config', {}).get('fitness_type', 'Unknown')
                    imp = e['improvement']
                    fit = e.get('best_fitness', 0)
                    gens = e.get('generations_run', 0)
                    
                    label = f"🚀 {alg.upper()} | Melhoria: {imp:.1f}% | Fit: {fit:.1f} | Gens: {gens} | ID: {e['id']}"
                    exp_options[label] = e['id']
                
                selected_exp_label = st.selectbox("📊 Selecione um Experimento (ordenado por % de Eficiência)", options=list(exp_options.keys()))
                selected_exp_id = exp_options[selected_exp_label]
                
                # Carrega detalhes do experimento
                exp_res = requests.get(f"{API_URL}/experiments/{selected_exp_id}")
                if exp_res.status_code == 200:
                    exp_data = exp_res.json()
                    details = exp_data.get('result_details', {})
                    config = exp_data.get('config', {})
                    
                    # Extrai rotas
                    if isinstance(details, list):
                        routes = details
                    else:
                        routes = details.get('routes', []) if isinstance(details, dict) else []
                    
                    if not routes:
                        st.warning("Este experimento não possui dados de rotas detalhadas.")
                    else:
                        # Carrega pontos do cenário
                        scenario_name = config.get('scenario', 'small')
                        scenario_res = requests.get(f"{API_URL}/scenarios/{scenario_name}")
                        id_map = {}
                        if scenario_res.status_code == 200:
                            scenario_points = scenario_res.json()
                            id_map = {str(p['id']): p for p in scenario_points}
                        
                        # 2. Filtro de Veículo
                        vehicle_ids = sorted(set(r.get('vehicle_id', 0) for r in routes))
                        vehicle_options = ["Todos os Veículos"] + [f"Veículo {vid}" for vid in vehicle_ids]
                        selected_vehicle = st.selectbox("🚛 Filtrar por Veículo", options=vehicle_options)
                        
                        # Filtra rotas
                        if selected_vehicle == "Todos os Veículos":
                            filtered_routes = routes
                        else:
                            vid = int(selected_vehicle.split()[-1])
                            filtered_routes = [r for r in routes if r.get('vehicle_id') == vid]
                        
                        # Agrupa por veículo
                        from collections import defaultdict
                        vehicle_routes = defaultdict(list)
                        for r in filtered_routes:
                            vehicle_routes[r.get('vehicle_id', 0)].append(r)
                        
                        st.divider()

                        # --- COMPARAÇÃO DE EFICIÊNCIA ---
                        # Usa session_state para manter o estado do painel aberto
                        if 'show_efficiency_comparison' not in st.session_state:
                            st.session_state.show_efficiency_comparison = False
                        
                        if st.button("📊 Comparar Eficiência (Baseline vs Otimizado)", type="secondary", use_container_width=True):
                            st.session_state.show_efficiency_comparison = not st.session_state.show_efficiency_comparison
                        
                        if st.session_state.show_efficiency_comparison:
                            st.markdown("### 📉 Relatório de Eficiência por Algoritmo")
                            
                            try:
                                # Agrupa experimentos por Tipo de Fitness e Cenário
                                from collections import defaultdict
                                fitness_groups = defaultdict(list)
                                
                                for e in completed:
                                    # Normaliza chave
                                    cfg = e.get('config', {})
                                    f_type = cfg.get('fitness_type', 'N/A')
                                    # Corrige bug de scenario_name vs scenario
                                    scen_name = cfg.get('scenario_name') or cfg.get('scenario') or 'large'
                                    
                                    # Chave composta
                                    fitness_groups[(f_type, scen_name)].append(e)
                                
                                # Reorganiza dados para exibição por Fitness
                                from collections import defaultdict
                                display_by_fitness = defaultdict(list)
                                
                                for (f_type, scen_name), exps in fitness_groups.items():
                                    # 1. Processamento das métricas (mantido igual)
                                    best_ever_fitness = min(e.get('best_fitness', 999999) for e in exps)
                                    
                                    total_gain_pct = 0
                                    total_km_saved = 0
                                    num_valid_dist = 0
                                    
                                    for e in exps:
                                        details = e.get('result_details', {})
                                        if not isinstance(details, dict): details = {}
                                        
                                        init_fit = details.get('initial_fitness', 0.0)
                                        final_fit = e.get('best_fitness', 0.0)
                                        init_dist = details.get('initial_total_distance')
                                        final_dist = details.get('total_distance')
                                        
                                        if init_dist is None: init_dist = 0.0
                                        if final_dist is None: final_dist = 0.0
                                        
                                        if f_type == 'distance_only':
                                            init_dist = init_fit
                                            final_fit = e.get('best_fitness', 0.0)
                                            final_dist = final_fit
                                        
                                        km_saved = 0.0
                                        if init_dist > 0 and final_dist > 0:
                                            km_saved = init_dist - final_dist
                                            total_km_saved += km_saved
                                            num_valid_dist += 1
                                            
                                        gain_pct = 0.0
                                        if init_fit > 0:
                                            gain_pct = ((init_fit - final_fit) / init_fit) * 100
                                        total_gain_pct += gain_pct
                                    
                                    avg_gain = total_gain_pct / len(exps) if exps else 0
                                    avg_km = total_km_saved / num_valid_dist if num_valid_dist > 0 else 0
                                    
                                    avg_final_fitness = sum(e.get('best_fitness', 0) for e in exps) / len(exps)
                                    gap_to_uptimal = 0.0
                                    if best_ever_fitness > 0:
                                        gap_to_uptimal = ((avg_final_fitness - best_ever_fitness) / best_ever_fitness) * 100
                                    
                                    # Traduz nome do fitness para agrupamento
                                    fitness_mapping_pt = {
                                        "weighted_multi_objective": "⚖️ Multiobjetivo Ponderado",
                                        "distance_only": "📏 Apenas Distância",
                                        "penalty_based": "⚠️ Baseado em Penalidades",
                                        "priority_aware": "🚨 Foco em Prioridade"
                                    }
                                    fitness_pt_name = fitness_mapping_pt.get(f_type, f_type.replace('_', ' ').title())
                                    
                                    # Dados base
                                    row_data = {
                                        "Cenário": scen_name.title(),
                                        "Execuções": len(exps),
                                        "Melhor Histórico (Fit)": f"{best_ever_fitness:.2f}",
                                        "Economia Média (KM)": f"{avg_km:.1f} km",
                                        "Gap vs Melhor (%)": f"{gap_to_uptimal:.1f}%"
                                    }
                                    
                                    # Lógica de Métricas Específicas
                                    specific_metric_val = 0.0
                                    specific_metric_name = None
                                    
                                    if f_type == 'priority_aware':
                                        # Calcula redução de penalidade de prioridade
                                        total_prio_improv = 0
                                        count = 0
                                        for e in exps:
                                            d = e.get('result_details', {})
                                            if not isinstance(d, dict): continue
                                            init_c = d.get('initial_components', {})
                                            final_c = d.get('final_components', {})
                                            
                                            i_prio = init_c.get('priority_penalty', 0)
                                            f_prio = final_c.get('priority_penalty', 0)
                                            
                                            if i_prio > 0:
                                                total_prio_improv += ((i_prio - f_prio) / i_prio) * 100
                                                count += 1
                                        
                                        if count > 0:
                                            specific_metric_val = total_prio_improv / count
                                            row_data["Melhoria Prioridade (%)"] = f"{specific_metric_val:.1f}%"
                                        else:
                                            row_data["Melhoria Prioridade (%)"] = "-"

                                    elif f_type == 'penalty_based':
                                        # Calcula redução de violações (Capacity + Autonomy)
                                        total_viol_improv = 0
                                        count = 0
                                        for e in exps:
                                            d = e.get('result_details', {})
                                            if not isinstance(d, dict): continue
                                            init_c = d.get('initial_components', {})
                                            final_c = d.get('final_components', {})
                                            
                                            i_viol = init_c.get('capacity_violation', 0) + init_c.get('autonomy_violation', 0)
                                            f_viol = final_c.get('capacity_violation', 0) + final_c.get('autonomy_violation', 0)
                                            
                                            if i_viol > 0:
                                                total_viol_improv += ((i_viol - f_viol) / i_viol) * 100
                                                count += 1
                                        
                                        if count > 0:
                                            specific_metric_val = total_viol_improv / count
                                            row_data["Redução de Violações (%)"] = f"{specific_metric_val:.1f}%"
                                        else:
                                            row_data["Redução de Violações (%)"] = "-"
                                    
                                    # Adiciona à lista do grupo
                                    display_by_fitness[fitness_pt_name].append(row_data)

                                # Renderiza uma tabela por Fitness Type
                                if display_by_fitness:
                                    for fitness_name in sorted(display_by_fitness.keys()):
                                        st.subheader(fitness_name)
                                        
                                        # Ordena por cenrio
                                        rows = sorted(display_by_fitness[fitness_name], key=lambda x: x['Cenário'])
                                        
                                        # Configuração Dinâmica de Colunas
                                        col_config = {}
                                        
                                        # Adiciona config para colunas específicas se existirem
                                        if "Melhoria Prioridade (%)" in rows[0]:
                                             col_config["Melhoria Prioridade (%)"] = st.column_config.ProgressColumn(
                                                "Melhoria Prioridade (%)",
                                                format="%s",
                                                min_value=0,
                                                max_value=100
                                            )
                                        if "Redução de Violações (%)" in rows[0]:
                                             col_config["Redução de Violações (%)"] = st.column_config.ProgressColumn(
                                                "Redução de Violações (%)",
                                                format="%s",
                                                min_value=0,
                                                max_value=100
                                            )
                                        
                                        st.dataframe(
                                            rows, 
                                            hide_index=True, 
                                            use_container_width=True,
                                            column_config=col_config
                                        )
                                else:
                                    st.warning("Nenhum dado comparável encontrado.")
                                    
                                st.info(
                                    """
                                    ℹ️ **Entenda os Dados:**
                                    
                                    **Métricas Gerais:**
                                    - **Economia Média (KM)**: Quantos quilômetros foram economizados em média por execução.
                                    - **Melhor Histórico**: O melhor valor de fitness já alcançado com este algoritmo.
                                    - **Gap vs Melhor**: Diferença percentual entre a média das execuções e o recorde histórico (quanto menor, mais consistente).
                                    
                                    **Cenários (Complexidade):**
                                    - **Small**: Cenário pequeno, ideal para testes rápidos (poucos pontos de entrega).
                                    - **Medium**: Complexidade média, representa uma operação padrão.
                                    - **Large**: Cenário de alta escala com muitos pontos, exigindo maior esforço computacional.
                                    - **Critical**: Cenário focado em alta densidade de entregas críticas/urgentes, testando a capacidade de priorização do algoritmo.
                                    
                                    **Variáveis Consideradas por Fitness:**
                                    - **⚖️ Multiobjetivo Ponderado**: Considera Distância Total, Penalidade de Prioridade, Violação de Capacidade, Violação de Autonomia e Janelas de Tempo. Pondera todos esses fatores para encontrar um equilíbrio.
                                    - **🚨 Foco em Prioridade**: Foca na minimização do tempo de chegada para entregas de alta prioridade (Críticas e Urgentes). O atraso em itens críticos é penalizado severamente.
                                    - **📏 Apenas Distância**: Considera exclusivamente a minimização da Distância Total percorrida (KM), ignorando capacidades ou prioridades (ideal para TSPs puros).
                                    - **⚠️ Baseado em Penalidades**: Começa permitindo soluções inválidas e aumenta a penalidade por violações (Capacidade, Autonomia) gradualmente a cada geração para forçar a convergência.
                                    """
                                )
                                    
                            except Exception as e:
                                st.error(f"Erro ao processar comparação: {e}")

                        # 3. BOTÃO GERAR MAPA
                        if st.button("🗺️ Gerar Mapa Interativo", type="primary", use_container_width=True):
                            st.session_state.show_logistics_map = True
                        
                        # Exibe mapa se solicitado
                        if st.session_state.get('show_logistics_map', False):
                            import folium
                            from folium import plugins
                            
                            st.markdown("### 🗺️ Mapa de Rotas")
                            
                            # Cria mapa base
                            COLORS = ['#e6194B', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#42d4f4', '#f032e6']
                            all_coords = []
                            
                            # Primeiro ponto para centralizar
                            first_coord = None
                            
                            # Coleta todas as coordenadas das rotas filtradas
                            for vid in sorted(vehicle_routes.keys()):
                                for route in vehicle_routes[vid]:
                                    stops_list = route.get('stops', [])
                                    for stop in stops_list:
                                        if isinstance(stop, dict):
                                            # Busca coordenadas no id_map pelo ID ou nome
                                            stop_id = stop.get('id')
                                            stop_name = stop.get('name', '')
                                            
                                            # Tenta buscar por ID
                                            p = id_map.get(str(stop_id)) if stop_id else None
                                            
                                            # Se não encontrou, busca por nome
                                            if not p:
                                                for pid, pdata in id_map.items():
                                                    if pdata.get('name') == stop_name:
                                                        p = pdata
                                                        break
                                            
                                            if p:
                                                coord = [p['lat'], p['lon']]
                                                all_coords.append(coord)
                                                if first_coord is None:
                                                    first_coord = coord
                            
                            if first_coord:
                                m = folium.Map(location=first_coord, zoom_start=11, tiles='CartoDB dark_matter')
                                
                                # PRIMEIRO: Adiciona TODOS os hospitais do cenário
                                priority_colors = {1: '#ff3333', 2: '#ff9900', 3: '#33cc33'}  # Vermelho, Laranja, Verde
                                depot_added = False
                                
                                for pid, p in id_map.items():
                                    coord = [p['lat'], p['lon']]
                                    priority = p.get('priority', 3)
                                    
                                    # Depósito (primeiro ponto, prioridade 0 ou id=0)
                                    if p.get('id') == 0 or priority == 0:
                                        if not depot_added:
                                            folium.Marker(
                                                location=coord,
                                                popup=f"<b>🏭 DEPÓSITO</b><br>{p.get('name')}",
                                                icon=folium.Icon(color='blue', icon='home')
                                            ).add_to(m)
                                            depot_added = True
                                    else:
                                        # Hospital com cor baseada em prioridade
                                        marker_color = priority_colors.get(priority, '#33cc33')
                                        folium.CircleMarker(
                                            location=coord,
                                            radius=10,
                                            color=marker_color,
                                            fill=True,
                                            fill_color=marker_color,
                                            fill_opacity=0.8,
                                            popup=f"<b>{p.get('name')}</b><br>Prioridade: {priority}<br>Demanda: {p.get('demand')}"
                                        ).add_to(m)
                                
                                # DEPOIS: Desenha rota para cada veículo
                                for i, vid in enumerate(sorted(vehicle_routes.keys())):
                                    color = COLORS[i % len(COLORS)]
                                    vehicle_coords = []
                                    
                                    for route in vehicle_routes[vid]:
                                        stops_list = route.get('stops', [])
                                        for stop in stops_list:
                                            if isinstance(stop, dict):
                                                stop_id = stop.get('id')
                                                stop_name = stop.get('name', '')
                                                
                                                p = id_map.get(str(stop_id)) if stop_id else None
                                                if not p:
                                                    for pid, pdata in id_map.items():
                                                        if pdata.get('name') == stop_name:
                                                            p = pdata
                                                            break
                                                
                                                if p:
                                                    coord = [p['lat'], p['lon']]
                                                    vehicle_coords.append(coord)
                                    
                                    # Polyline + AntPath animado
                                    if len(vehicle_coords) > 1:
                                        folium.PolyLine(vehicle_coords, color=color, weight=3, opacity=0.7).add_to(m)
                                        plugins.AntPath(
                                            locations=vehicle_coords,
                                            weight=4,
                                            color=color,
                                            opacity=0.9,
                                            dash_array=[10, 20],
                                            delay=1000,
                                            pulse_color=color,
                                            tooltip=f"Veículo {vid}"
                                        ).add_to(m)
                                
                                # Ajusta zoom
                                if all_coords:
                                    m.fit_bounds(all_coords)
                                
                                st_folium(m, width=None, height=500)
                                
                                # LEGENDA DE VEÍCULOS
                                st.markdown("### 🚛 Legenda de Rotas")
                                leg_cols = st.columns(min(len(vehicle_routes), 4))
                                
                                for i, vid in enumerate(sorted(vehicle_routes.keys())):
                                    color = COLORS[i % len(COLORS)]
                                    v_routes = vehicle_routes[vid]
                                    total_dist = sum(r.get('distance', 0) for r in v_routes)
                                    total_load = sum(r.get('load', r.get('demand', 0)) for r in v_routes)
                                    
                                    
                                    # Formata viagens individualmente
                                    trips_html = []
                                    for t_idx, route in enumerate(v_routes):
                                        stops = [s.get('name', '?') for s in route.get('stops', []) if isinstance(s, dict)]
                                        trips_html.append(f"<b>Viagem {t_idx + 1}:</b> {' → '.join(stops)}")
                                    
                                    trips_display = "<br>".join(trips_html)
                                    
                                    with leg_cols[i % len(leg_cols)]:
                                        st.markdown(f"""
                                        <div style="border-left: 5px solid {color}; padding-left: 10px; margin-bottom: 15px;">
                                            <b style="color: {color};">Veículo {vid}</b><br>
                                            <small>📏 {total_dist:.2f} km | 📦 {total_load:.1f}</small><br>
                                            <small>{trips_display}</small>
                                        </div>
                                        """, unsafe_allow_html=True)
                                
                            else:
                                st.warning("Não foi possível encontrar coordenadas para as rotas selecionadas.")
                        
                        st.divider()
                        
                        # 4. Visualização por Veículo
                        for vid in sorted(vehicle_routes.keys()):
                            v_routes = vehicle_routes[vid]
                            total_dist = sum(r.get('distance', 0) for r in v_routes)
                            total_load = sum(r.get('load', r.get('demand', 0)) for r in v_routes)
                            
                            with st.expander(f"🚛 Veículo {vid} - Total: {total_dist:.2f} km | Carga: {total_load:.1f}", expanded=True):
                                # Para cada rota/viagem do veículo
                                for trip_idx, route in enumerate(v_routes):
                                    st.markdown(f"### 📍 Viagem {trip_idx + 1}")
                                    
                                    # Mapa Leaflet para esta rota
                                    import folium
                                    from folium import plugins
                                    
                                    # Tenta obter pontos: primeiro 'points', depois 'stops'
                                    points_ids = route.get('points', [])
                                    stops_data = route.get('stops', [])
                                    
                                    # Debug info (como caption para evitar nested expander)
                                    st.caption(f"🔍 Debug: points={len(points_ids)}, stops={len(stops_data)}, scenario_loaded={bool(id_map)}")
                                    
                                    # Se não tiver points mas tiver stops com dados estruturados
                                    point_details = []
                                    coords = []
                                    
                                    if points_ids and id_map:
                                        # Usa points para lookup no id_map
                                        for pid in points_ids:
                                            p = id_map.get(str(pid))
                                            if p:
                                                coords.append([p['lat'], p['lon']])
                                                point_details.append(p)
                                        
                                        if coords:
                                            # Cria mapa centrado no primeiro ponto
                                            m = folium.Map(location=coords[0], zoom_start=12, tiles='CartoDB positron')
                                            
                                            # Adiciona markers numerados
                                            for i, (coord, p) in enumerate(zip(coords, point_details)):
                                                priority_colors = {1: 'red', 2: 'orange', 3: 'green'}
                                                color = priority_colors.get(p.get('priority', 3), 'blue')
                                                
                                                folium.Marker(
                                                    location=coord,
                                                    popup=f"{p.get('name')} (Prioridade: {p.get('priority')})",
                                                    icon=folium.DivIcon(html=f'<div style="background:{color};color:white;border-radius:50%;width:25px;height:25px;text-align:center;line-height:25px;font-weight:bold;">{i+1}</div>')
                                                ).add_to(m)
                                            
                                            # Polyline da rota
                                            folium.PolyLine(coords, color='#007BFF', weight=4, opacity=0.8).add_to(m)
                                            
                                            # Ajusta zoom
                                            m.fit_bounds(coords)
                                            
                                            st_folium(m, width=None, height=400)
                                            
                                            # Box de informações
                                            st.markdown("#### 📋 Detalhes da Rota")
                                            
                                            # Tabela com hospitais e distâncias
                                            from src.genetic_algorithm.chromosome import haversine_distance
                                            
                                            route_info = []
                                            for i, p in enumerate(point_details):
                                                dist_to_next = 0
                                                if i < len(point_details) - 1:
                                                    next_p = point_details[i + 1]
                                                    dist_to_next = haversine_distance(p['lat'], p['lon'], next_p['lat'], next_p['lon'])
                                                
                                                route_info.append({
                                                    "Ordem": i + 1,
                                                    "Hospital": p.get('name', f"ID:{p.get('id')}"),
                                                    "Prioridade": p.get('priority', '-'),
                                                    "Demanda": p.get('demand', '-'),
                                                    "Dist. Próximo (km)": f"{dist_to_next:.2f}" if dist_to_next > 0 else "-"
                                                })
                                            
                                            st.dataframe(route_info, use_container_width=True, hide_index=True)
                                            
                                            # Totais
                                            st.markdown(f"**📏 Distância Total:** {route.get('distance', 0):.2f} km")
                                            st.markdown(f"**📦 Carga:** {route.get('load', route.get('demand', 0)):.1f}")
                                    
                                    elif stops_data:
                                        # Fallback: usa stops (dados legados ou estruturados)
                                        st.markdown("#### 📋 Detalhes da Rota (dados legados)")
                                        
                                        if isinstance(stops_data[0], dict):
                                            # Stops estruturados com nome, prioridade, etc
                                            route_info = []
                                            for i, stop in enumerate(stops_data):
                                                route_info.append({
                                                    "Ordem": i + 1,
                                                    "Hospital": stop.get('name', f"ID:{stop.get('id')}"),
                                                    "Prioridade": stop.get('priority', '-'),
                                                    "Demanda": stop.get('demand', '-')
                                                })
                                            st.dataframe(route_info, use_container_width=True, hide_index=True)
                                        else:
                                            # Stops são strings (nomes)
                                            for i, stop_name in enumerate(stops_data):
                                                st.write(f"{i+1}. {stop_name}")
                                        
                                        st.markdown(f"**📏 Distância Total:** {route.get('distance', 0):.2f} km")
                                        st.markdown(f"**📦 Carga:** {route.get('load', route.get('demand', 0)):.1f}")
                                    
                                    else:
                                        st.warning("Dados de pontos não disponíveis para esta rota.")
                                    
                                    st.divider()
                else:
                    st.error("Erro ao carregar detalhes do experimento.")
        else:
            st.error("Erro ao carregar lista de experimentos.")
    except Exception as e:
        st.error(f"Erro: {e}")
        import traceback
        st.code(traceback.format_exc())

# ========================================
# PÁGINA: CONFIG LLM
# ========================================
elif page == "⚙️":
    st.title("⚙️ Configuração do LLM")
    st.caption("Configure o provider de LLM para otimização automática.")
    
    from src.database.database import get_setting, set_setting
    
    # --- Gerenciamento de Configurações por Provider ---
    
    def get_default_provider_configs():
        """Retorna configurações padrão solicitadas"""
        return {
            "ollama": {
                "base_url": "http://ga-vrp-ollama:11434",
                "model": "gemma3:latest",
                "api_key": ""
            },
            "chatmock": {
                "base_url": "http://192.168.31.29:8000",
                "model": "gpt-5.1-codex-max",
                "api_key": ""
            },
            "llamacpp": {
                "base_url": "http://localhost:8080",
                "model": "default",
                "api_key": ""
            },
            "chatgpt": {
                "base_url": "",
                "model": "gpt-4o-mini",
                "api_key": ""
            },
            "openrouter": {
                "base_url": "",
                "model": "openai/gpt-4o-mini",
                "api_key": ""
            }
        }

    # Carrega configurações salvas de TODOS os providers (Registry)
    # Se não existir, inicia com os defaults
    saved_all_configs = get_setting('llm_all_configs', {})
    default_configs = get_default_provider_configs()
    
    # Mescla salvos com defaults (para garantir que novos providers tenham config)
    all_configs = {**default_configs, **saved_all_configs}
    
    # Carrega qual é o provider ATIVO atualmente
    active_config = get_setting('llm_config', {})
    current_active_provider = active_config.get('provider', 'ollama')

    # --- Interface ---

    # Seleção de Provider
    providers_list = ["ollama", "chatmock", "llamacpp", "chatgpt", "openrouter"]
    if current_active_provider not in providers_list:
        current_active_provider = "ollama"
        
    selected_provider = st.selectbox(
        "🔌 Provider", 
        providers_list, 
        index=providers_list.index(current_active_provider)
    )
    
    # Recupera config específica do provider selecionado
    provider_config = all_configs.get(selected_provider, {})
    
    # -- Campos do Formulário --
    # Usamos key dinâmica para forçar atualização dos campos ao trocar o provider
    
    if selected_provider in ["ollama", "llamacpp", "chatmock"]:
        base_url = st.text_input(
            "🌐 URL Base", 
            value=provider_config.get('base_url', ''),
            key=f"url_{selected_provider}"
        )
        api_key = ""
    else:
        api_key = st.text_input(
            "🔑 API Key", 
            type="password", 
            value=provider_config.get('api_key', ''),
            key=f"key_{selected_provider}"
        )
        base_url = ""
        
    # Botão Carregar Modelos
    col1, col2 = st.columns([1, 3])
    with col1:
        load_models = st.button("🔄 Carregar Modelos", key=f"load_{selected_provider}")
    
    if load_models:
        try:
            from src.llm.adapters import get_adapter
            if selected_provider in ["ollama", "llamacpp", "chatmock"]:
                adapter = get_adapter(selected_provider, base_url=base_url)
            else:
                adapter = get_adapter(selected_provider, api_key=api_key)
            
            models = adapter.list_models()
            st.session_state[f'models_{selected_provider}'] = models
            if models:
                st.success(f"✅ {len(models)} modelos encontrados!")
            else:
                st.warning("Nenhum modelo encontrado.")
        except Exception as e:
            st.error(f"Erro ao conectar: {e}")

    # Seleção de Modelo
    available_models = st.session_state.get(f'models_{selected_provider}', [])
    current_model_value = provider_config.get('model', '')
    
    if available_models:
        # Tenta selecionar o modelo que já estava salvo
        idx = 0
        if current_model_value in available_models:
            idx = available_models.index(current_model_value)
        model = st.selectbox("🤖 Modelo", options=available_models, index=idx, key=f"model_{selected_provider}")
    else:
        model = st.text_input("🤖 Modelo (manual)", value=current_model_value, key=f"model_manual_{selected_provider}")

    # Botão Salvar
    if st.button("💾 Salvar & Ativar Configuração", type="primary"):
        # 1. Atualiza o registro do provider atual
        all_configs[selected_provider] = {
            "base_url": base_url,
            "api_key": api_key,
            "model": model
        }
        
        # 2. Define como configuração ativa (compatibilidade com sistema)
        new_active_config = {
            "provider": selected_provider,
            "base_url": base_url,
            "api_key": api_key,
            "model": model
        }
        
        # 3. Persiste no Banco de Dados
        set_setting('llm_all_configs', all_configs)  # Salva o "banco" de configs
        set_setting('llm_config', new_active_config) # Salva a config ativa
        
        # Atualiza Session State
        st.session_state.llm_config = new_active_config
        
        st.success(f"✅ Configuração de **{selected_provider}** salva e ativada!")
        st.balloons()
    
    st.divider()
    
    # Botão de teste
    st.subheader("🧪 Testar Conexão")
    if st.button("🔬 Testar Modelo", use_container_width=True):
        with st.spinner("Testando conexão com LLM..."):
            st.info(f"📡 Conectando a: {base_url or provider}")
            st.info(f"🤖 Modelo: {model}")
            
            import requests as req
            try:
                raw_resp = req.post(
                    f"{base_url}/v1/chat/completions",
                    headers={"Authorization": "Bearer key", "Content-Type": "application/json"},
                    json={
                        "model": model, 
                        "messages": [{"role": "user", "content": "Return JSON: {\"test\": 1}"}]
                    },
                    timeout=120
                )
                st.info(f"Status HTTP: {raw_resp.status_code}")
                
                if raw_resp.status_code == 200:
                    raw_json = raw_resp.json()
                    content = raw_json.get('choices', [{}])[0].get('message', {}).get('content', '')
                    st.code(f"Raw: {content[:500]}")
                    
                    from src.llm.adapters import parse_llm_response
                    parsed = parse_llm_response(content)
                    st.info(f"Parsed: {parsed}")
                    
                    if parsed:
                        st.success("✅ Modelo respondeu corretamente!")
                        st.json(parsed)
                    else:
                        st.error("❌ Parsing falhou")
                else:
                    st.error(f"Erro HTTP: {raw_resp.text[:300]}")
            except Exception as e:
                st.error(f"❌ Erro: {e}")
                import traceback
                st.code(traceback.format_exc())
    
    # Mostra config atual
    with st.expander("📋 Configuração Atual"):
        cfg = st.session_state.llm_config
        st.json({
            "provider": cfg.get('provider'),
            "model": cfg.get('model'),
            "url": cfg.get('base_url') or "(API externa)"
        })

# ========================================
# PÁGINA: LOGISTIC LLM
# ========================================
elif page == "Logistic LLM":
    st.title("🤖 Logistic LLM")
    st.caption("Otimização automática de parâmetros via LLM.")
    
    # Carrega config do banco se não estiver em session_state
    from src.database.database import get_setting
    if 'llm_config' not in st.session_state or not st.session_state.llm_config.get('model'):
        db_config = get_setting('llm_config', {})
        if db_config:
            st.session_state.llm_config = db_config
    
    llm_cfg = st.session_state.get('llm_config', {})
    if not llm_cfg.get('model'):
        st.warning("⚠️ Configure o LLM primeiro na aba 'Config LLM'.")
        st.stop()
    
    st.info(f"🔌 Usando: **{llm_cfg.get('provider')}** / **{llm_cfg.get('model')}**")
    
    try:
        # Carrega experimentos agrupados por fitness_type
        res = requests.get(f"{API_URL}/experiments")
        if res.status_code == 200:
            experiments = res.json()
            completed = [e for e in experiments if e.get('status') == 'completed']
            
            if not completed:
                st.info("Nenhum experimento completado. Execute um primeiro.")
                st.stop()
            
            # Agrupa por fitness_type E cenário para estatísticas
            from collections import defaultdict
            # Key: (fitness_type, scenario_name)
            stats_by_fitness = defaultdict(lambda: {'count': 0, 'best_exp': None, 'sum_fitness': 0.0, 'times': []})
            
            for exp in completed:
                cfg = exp.get('config', {})
                ft = cfg.get('fitness_type', 'unknown')
                scen = cfg.get('scenario_name') or cfg.get('scenario') or 'unknown'
                
                fit = exp.get('best_fitness', float('inf')) or float('inf') # Handle None
                if fit == float('inf'): continue
                
                # Chave composta
                key = (ft, scen)

                stats = stats_by_fitness[key]
                stats['count'] += 1
                stats['sum_fitness'] += fit
                stats['times'].append(exp.get('execution_time', 0) or 0)
                
                current_best = stats['best_exp']
                if current_best is None or fit < (current_best.get('best_fitness') or float('inf')):
                    stats['best_exp'] = exp
            
            st.subheader("📊 Melhores por Tipo de Fitness e Cenário")
            
            # Tabela com melhores + estatísticas
            table_data = []
            for (ft, scen), stats in stats_by_fitness.items():
                best_exp = stats['best_exp']
                if best_exp:
                    avg_fit = stats['sum_fitness'] / stats['count']
                    avg_time = sum(stats['times']) / stats['count']
                    
                    table_data.append({
                        "Abordagem": ft,
                        "Cenário": scen,
                        "🏆 Melhor Fitness": f"{(best_exp.get('best_fitness') or 0):.2f}",
                        "📉 Média Fitness": f"{avg_fit:.2f}",
                        "🔢 Execuções": stats['count'],
                        "⏱️ Tempo Médio": f"{avg_time:.1f}s",
                        "ID Melhor": best_exp.get('id')
                    })
            
            # Filtro por Abordagem (Adicionado por request)
            if table_data:
                all_approaches = sorted(list(set(d['Abordagem'] for d in table_data)))
                selected_approaches = st.multiselect("Filtrar por Abordagem:", all_approaches, default=all_approaches, key="llm_grid_filter")
                
                filtered_table = [d for d in table_data if d['Abordagem'] in selected_approaches]
            else:
                filtered_table = []

            st.dataframe(filtered_table, use_container_width=True, hide_index=True)
            
            with st.expander("🕒 Histórico Recente (Todas as Execuções)", expanded=False):
                history_data = []
                for exp in experiments: # Lista completa sem filtro de 'melhor'
                    history_data.append({
                        "ID": exp.get('id'),
                        "Status": exp.get('status'),
                        "Fitness": f"{(exp.get('best_fitness') or 0):.2f}",
                        "Gerações": exp.get('generations_run'),
                        "Método": exp.get('config', {}).get('fitness_type', '?'),
                        "Criado em": exp.get('created_at', '?')
                    })
                st.dataframe(history_data, use_container_width=True, hide_index=True)
            
            st.divider()
            
            # Seleção do experimento base com label rica
            exp_options = {}
            for (ft, scen), stats in stats_by_fitness.items():
                if stats['best_exp']:
                    best = stats['best_exp']
                    # Label formatada conforme solicitado
                    # Ex: distance_only (🏆 Melhor: 128.71 | 🔢 N=132 | Tipo de Fitness = Critical)
                    # Nota: O usuário pediu "Tipo de Fitness = Critical" mas Critical é Cenário. 
                    # Usarei "Cenário" para clareza, mas mantendo a estrutura.
                    label = f"{ft} (🏆 Melhor: {(best.get('best_fitness') or 0):.2f} | 🔢 N={stats['count']} | Cenário: {scen})"
                    exp_options[label] = best

            selected_label = st.selectbox("📍 Selecione a Abordagem Base para Otimizar", options=list(exp_options.keys()))
            selected_exp = exp_options[selected_label]
            
            # Mostra JSON do experimento selecionado
            with st.expander("📋 Config do Experimento Base", expanded=True):
                config = selected_exp.get('config', {})
                st.json(config)
            
            # Configuração de iterações
            max_iterations = st.slider("🔄 Número de Iterações", min_value=1, max_value=50, value=5)
            
            st.divider()
            
            # Botão de execução
            col1, col2 = st.columns(2)
            with col1:
                start_btn = st.button("▶️ Iniciar Otimização", type="primary", use_container_width=True)
            with col2:
                stop_btn = st.button("⏹️ Parar", use_container_width=True)
            
            if stop_btn:
                st.session_state.llm_stop = True
                st.warning("Parando...")
            
            if start_btn:
                st.session_state.llm_stop = False
                
                # Prepara adapter
                # Prepara adapter e força recarregamento do código atualizado
                import importlib
                import sys
                import src.llm.adapters
                import src.llm.domains
                
                # Força recarregamento para garantir que o NOVO prompt seja usado
                importlib.reload(src.llm.domains)
                importlib.reload(src.llm.adapters)
                
                from src.llm.adapters import get_adapter
                from src.llm.optimizer import LLMOptimizer
                
                if llm_cfg.get('provider') in ['ollama', 'llamacpp', 'chatmock']:
                    adapter = get_adapter(llm_cfg.get('provider'), base_url=llm_cfg.get('base_url'), model=llm_cfg.get('model'))
                else:
                    adapter = get_adapter(llm_cfg.get('provider'), api_key=llm_cfg.get('api_key'), model=llm_cfg.get('model'))
                
                optimizer = LLMOptimizer(max_iterations=max_iterations)
                
                base_params = selected_exp.get('config', {})
                base_fitness = selected_exp.get('best_fitness')
                if base_fitness is None: base_fitness = float('inf')
                best_exp_id = selected_exp.get('id')
                
                st.subheader("📈 Progresso")
                progress_bar = st.progress(0)
                status_text = st.empty()
                results_container = st.container()
                
                # Loop de otimização
                history = []
                for i in range(max_iterations):
                    if st.session_state.get('llm_stop', False):
                        break
                    
                    progress_bar.progress((i + 1) / max_iterations)
                    status_text.text(f"Iteração {i + 1}/{max_iterations}...")
                    
                    context = {
                        "fitness": base_fitness,
                        "params": base_params,
                        "history": history
                    }
                    
                    
                    # Obtém sugestão do LLM
                    try:
                        new_params = adapter.suggest_params(context)
                    except Exception as llm_error:
                        with results_container:
                            st.error(f"#{i+1}: Erro LLM - {llm_error}")
                        continue
                    
                    if not new_params:
                        with results_container:
                            st.warning(f"#{i+1}: LLM não retornou parâmetros válidos. Verifique conexão com {llm_cfg.get('provider')}:{llm_cfg.get('base_url', llm_cfg.get('model'))}")
                        continue
                    
                    # Mescla parâmetros usando o sistema de domínios
                    from src.llm.domains import GADomains

                    merged = base_params.copy()
                    merged.update(new_params)  # Atualiza com TODOS os parâmetros sugeridos pelo LLM

                    # Valida e corrige automaticamente usando os domínios
                    merged = GADomains.validate_params(merged)
                    
                    # Executa experimento
                    api_res = requests.post(f"{API_URL}/run", json=merged)
                    if api_res.status_code != 200:
                        st.error(f"Erro na API: {api_res.text}")
                        continue
                    
                    exp_id = api_res.json().get('id')
                    
                    # Aguarda conclusão (polling simples)
                    import time
                    for _ in range(60):  # max 2 min
                        time.sleep(2)
                        check = requests.get(f"{API_URL}/experiments/{exp_id}").json()
                        if check.get('status') == 'completed':
                            break
                    
                    new_fitness = check.get('best_fitness')
                    if new_fitness is None: new_fitness = float('inf')
                    
                    change_pct = ((new_fitness - base_fitness) / base_fitness) * 100 if base_fitness else 0

                    improved = new_fitness < base_fitness

                    # CRÍTICO: Adiciona parâmetros completos ao histórico para o LLM aprender
                    history.append({
                        "iteration": i + 1,
                        "old_fitness": base_fitness,
                        "new_fitness": new_fitness,
                        "change_pct": change_pct,
                        "improved": improved,
                        "params": merged,  # ← ADICIONA OS PARÂMETROS COMPLETOS!
                        "experiment_id": exp_id
                    })
                    
                    with results_container:
                        icon = "✅" if improved else "❌"
                        st.markdown(f"**#{i+1}:** {base_fitness:.2f} → {new_fitness:.2f} ({change_pct:+.1f}%) {icon}")

                        # Mostra algoritmos mudados em destaque
                        algo_domains = GADomains.get_algorithmic_domains()
                        algo_changes = []
                        for key in algo_domains.keys():
                            if key in merged and merged.get(key) != base_params.get(key):
                                algo_changes.append(f"**{key}**: {base_params.get(key)} → :green[{merged.get(key)}]")

                        if algo_changes:
                            st.markdown("🧬 **Algoritmos Alterados:**")
                            for change in algo_changes:
                                st.markdown(f"  - {change}")

                        # Expander com configuração completa
                        with st.expander(f"📊 Configuração #{i+1} (Completa)"):
                            # Separa por prioridade
                            st.markdown("### 🔴 Algoritmos (Prioridade 1)")
                            for key in algo_domains.keys():
                                val = merged.get(key, "N/A")
                                old_val = base_params.get(key)
                                if old_val != val:
                                    st.markdown(f"- **{key}**: :green[{val}] (era {old_val})")
                                else:
                                    st.markdown(f"- {key}: {val}")

                            st.markdown("### 🟢 Parâmetros Numéricos (Prioridade 3)")
                            numeric_keys = ['population_size', 'max_generations', 'crossover_rate',
                                          'mutation_rate', 'elite_size', 'tournament_size',
                                          'stagnation_limit', 'heuristic_init_ratio']
                            for key in numeric_keys:
                                if key in merged:
                                    val = merged.get(key)
                                    old_val = base_params.get(key)
                                    if old_val != val:
                                        st.markdown(f"- **{key}**: :green[{val}] (era {old_val})")
                                    else:
                                        st.markdown(f"- {key}: {val}")
                    
                    # Atualiza base se melhorou
                    if improved:
                        base_fitness = new_fitness
                        base_params = merged
                        best_exp_id = exp_id
                
                progress_bar.progress(1.0)
                status_text.text("Concluído!")
                
                # Resumo final
                if history:
                    initial_fit = history[0]['old_fitness']
                    final_fit = base_fitness
                    total_change = ((final_fit - initial_fit) / initial_fit) * 100 if initial_fit else 0
                    
                    st.success(f"🎯 **Resultado Final:** {initial_fit:.2f} → {final_fit:.2f} ({total_change:+.1f}%)")
                    st.info(f"💾 **Melhor Experimento Salvo:** ID `{best_exp_id}`")
                    
                    if st.button("🔄 Atualizar Lista para Reutilizar"):
                        st.rerun()
        else:
            st.error("Erro ao carregar experimentos.")
    except Exception as e:
        st.error(f"Erro: {e}")
        import traceback
        st.code(traceback.format_exc())

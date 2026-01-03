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
    page_title="Saudelog - Otimização Logística",
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
    logo_path = "assets/logo.png"
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 15px; margin-top: -15px;">
                <img src="data:image/png;base64,{logo_b64}" style="height: 90px; width: auto;">
                <h1 style="margin: 0; padding: 0; color: #007BFF; font-family: 'Inter', sans-serif; font-size: 3rem; line-height: 1.2;">Saudelog</h1>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        st.markdown("<h1 style='color: #007BFF;'>Saudelog</h1>", unsafe_allow_html=True)

with col_nav2:
    # Inicializa página no session_state se não existir
    if 'nav_page' not in st.session_state:
        st.session_state.nav_page = "Dashboard"

    # Callback para mudar página pelo menu
    def on_page_change():
        pass

    page = st.segmented_control(
        "Navegação", 
        ["Dashboard", "Nova Execução", "Análise Detalhada"],
        key="nav_page",
        on_change=on_page_change,
        label_visibility="collapsed",
        selection_mode="single"
    )
    
    # Se nada estiver selecionado (clique para desmarcar), força Dashboard
    if not page:
        st.session_state.nav_page = "Dashboard"
        st.rerun()
    


API_URL = "http://localhost:8000"

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
        experiments = pd.DataFrame(requests.get(f"{API_URL}/experiments").json())
        
        if not experiments.empty:
            best_fitness = experiments['best_fitness'].min()
            total_runs = len(experiments)
            avg_gens = experiments['generations_run'].mean()
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Melhor Fitness Global</h3>
                    <h1>{best_fitness:.2f}</h1>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Total de Execuções</h3>
                    <h1>{total_runs}</h1>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Média de Gerações</h3>
                    <h1>{avg_gens:.0f}</h1>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("### 🕒 Histórico Recente")
            
            # Cálculo de Ganho na Tabela
            def calc_gain(row):
                if not row.get('result_details'): return 0.0
                try:
                    # result_details pode vir como string JSON do banco se não for parseado automaticaemnte pelo requests/dataframe
                    # mas requests.json() converte tudo recursivamente, então deve ser dict
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

            # Extração do Tipo de Fitness e Ganho
            def get_fitness_label(config):
                if not isinstance(config, dict): return "🧬 Padrão"
                ftype = config.get('fitness_type', 'N/A')
                mapping = {
                    "weighted_multi_objective": "⚖️ Multiobjetivo",
                    "distance_only": "📏 Distância",
                    "penalty_based": "⚠️ Penalidades",
                    "priority_aware": "🚨 Prioridade"
                }
                return mapping.get(ftype, ftype)

            experiments['ganho_pct'] = experiments.apply(calc_gain, axis=1)
            experiments['fitness_inicial'] = experiments.apply(get_initial_fitness, axis=1)
            experiments['fitness'] = experiments['config'].apply(get_fitness_label)
            
            # Formatando para exibição
            display_df = experiments[['id', 'status', 'created_at', 'fitness', 'fitness_inicial', 'best_fitness', 'ganho_pct', 'execution_time', 'generations_run']].copy()
            # Aplica conversão de fuso horário
            display_df['created_at'] = display_df['created_at'].apply(format_date_br)
            display_df['ganho_pct'] = display_df['ganho_pct'].map('{:.1f}%'.format)
            display_df['fitness_inicial'] = display_df['fitness_inicial'].map('{:.2f}'.format)
            display_df['best_fitness'] = display_df['best_fitness'].map('{:.2f}'.format)
            display_df['execution_time'] = display_df['execution_time'].map('{:.1f}s'.format)

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
                    "fitness_inicial": "Fitness Inicial",
                    "ganho_pct": "Ganho (%)",
                    "execution_time": "Tempo",
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
            
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Não foi possível conectar à API. Certifique-se de que o backend está rodando.")
        st.code("uvicorn src.api.main:app --reload")

elif page == "Nova Execução":
    st.title("🚀 Configurar Experimento")
    
    # Tentar carregar última configuração
    defaults = {
        "population_size": 100,
        "max_generations": 200,
        "crossover_rate": 0.9,
        "mutation_rate": 0.15,
        "scenario_name": "large",
        "num_vehicles": 3,
        "vehicle_capacity": 100.0,
        "vehicle_speed": 40.0,
        "vehicle_max_distance": 200.0,
        "selection_method": "tournament",
        "crossover_method": "order_crossover",
        "mutation_method": "inversion",
        "elite_size": 2,
        "tournament_size": 3
    }
    
    try:
        last_exp = requests.get(f"{API_URL}/experiments/latest").json()
        if last_exp and "config" in last_exp:
            lc = last_exp["config"]
            # Atualiza com segurança de tipos
            defaults["population_size"] = int(lc.get("population_size", 100))
            defaults["max_generations"] = int(lc.get("max_generations", 200))
            defaults["crossover_rate"] = float(lc.get("crossover_rate", 0.9))
            defaults["mutation_rate"] = float(lc.get("mutation_rate", 0.15))
            defaults["scenario_name"] = lc.get("scenario_name", "large")
            defaults["num_vehicles"] = int(lc.get("num_vehicles", 3))
            defaults["vehicle_capacity"] = float(lc.get("vehicle_capacity", 100.0))
            defaults["vehicle_speed"] = float(lc.get("vehicle_speed", 40.0))
            defaults["vehicle_max_distance"] = float(lc.get("vehicle_max_distance", 200.0))
            defaults["selection_method"] = lc.get("selection_method", "tournament")
            defaults["crossover_method"] = lc.get("crossover_method", "order_crossover")
            defaults["mutation_method"] = lc.get("mutation_method", "inversion")
            defaults["elite_size"] = int(lc.get("elite_size", 2))
            defaults["tournament_size"] = int(lc.get("tournament_size", 3))

    except Exception:
        pass # Falha silenciosa, usa defaults padrão

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
                scenarios_opts = ["small", "medium", "large", "critical"]
                try:
                    scen_idx = scenarios_opts.index(defaults["scenario_name"])
                except:
                    scen_idx = 2
                scenario = st.selectbox("Cenário", scenarios_opts, index=scen_idx)
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
                
                sel_opts = ["roulette_wheel", "tournament", "rank", "truncation", 
                        "elitist", "stochastic_universal_sampling", "boltzmann", "steady_state"]
                try:
                    sel_idx = sel_opts.index(defaults["selection_method"])
                except:
                    sel_idx = 1
                
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
                
                replace_opts = ["generational", "steady_state", "elitist"]
                try:
                    rep_idx = replace_opts.index(defaults.get("replacement_strategy", "elitist"))
                except:
                    rep_idx = 2
                
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
                
                cross_opts = [
                        "order_crossover", "partially_mapped_crossover", "cycle_crossover",
                        "alternating_edges_crossover", "edge_recombination_crossover",
                        "sequential_constructive_crossover", "order_based_crossover",
                        "position_based_crossover"
                    ]
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
                mut_opts = [
                        "inversion", "swap", "scramble", "insert", "displacement",
                        "2-opt", "3-opt", "reverse_sequence"
                    ]
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
            st.markdown("#### Diversidade")
            heuristic_init = st.slider("Inicialização Heurística (%)", 0.0, 1.0, 0.2, help="Proporção da população inicial gerada com heurística (Gulosa) versus Aleatória.")

        with tab4:
            st.info("Ajuste a importância de cada objetivo na função de fitness.")
            fitness_type = st.selectbox("Tipo de Fitness", ["weighted_multi_objective", "distance_only", "penalty_based", "priority_aware"], index=0)
            
            if fitness_type == "weighted_multi_objective":
                c1, c2 = st.columns(2)
                with c1:
                    w_dist = st.number_input("Peso Distância", 0.0, 100.0, 1.0)
                    w_prio = st.number_input("Peso Prioridade", 0.0, 1000.0, 10.0)
                with c2:
                    w_cap = st.number_input("Penalidade Capacidade", 0.0, 1000.0, 100.0)
                    w_auto = st.number_input("Penalidade Autonomia", 0.0, 1000.0, 100.0)
                    w_wind = st.number_input("Penalidade Janela Tempo", 0.0, 1000.0, 50.0)
            else:
                w_dist, w_prio, w_cap, w_auto, w_wind = 1.0, 10.0, 100.0, 100.0, 50.0


        
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
        "stagnation_limit": 50
    }
    
    # Colunas assimétricas para alinhar os botões à esquerda
    col_act1, col_act2, col_spacer = st.columns([1, 1.2, 3])
    
    with col_act1:
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
        # Prepara DF para exibição (mesma lógica do Dashboard mas simplificada)
        df_display = df_exps[['id', 'status', 'created_at', 'best_fitness', 'generations_run']].copy()
        df_display['created_at'] = df_display['created_at'].apply(format_date_br)
        df_display['best_fitness'] = df_display['best_fitness'].apply(lambda x: f"{x:.2f}" if x else "-")
        
        st.markdown("##### Selecione um Experimento:")
        
        # Grid de Seleção
        event_grid = st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            selection_mode="single-row",
            on_select="rerun",
            key="analysis_grid",
            height=200
        )
        
        if len(event_grid.selection.rows) > 0:
            selected_row_idx = event_grid.selection.rows[0]
            selected_id_from_grid = int(df_display.iloc[selected_row_idx]['id'])
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

    # Input Manual (Fallback ou visualizador do ID atual)
    # Se tiver ID, mostra ele. Se não, permite digitar.
    cols_input = st.columns([1, 4])
    with cols_input[0]:
        exp_id = st.number_input(
            "ID Selecionado", 
            min_value=1, 
            step=1, 
            value=final_exp_id if final_exp_id else 1
        )
    
    # Botão de Carregar/Excluir agindo sobre o exp_id (que reflete a seleção)
    c_load, c_del_rec, c_spacer = st.columns([1.2, 1, 4])
    with c_load:
        # Se veio do grid, talvez já queira carregar automático?
        # Para manter o padrão "Master-Detail" fluido, podemos considerar que a seleção JÁ carrega.
        # Mas mantemos o botão para forçar recarga ou clareza.
        # Vamos fazer AUTO-LOAD se selecionou no grid.
        pass 

    load_current = False
    if selected_id_from_grid or ('loaded_exp_id' in st.session_state and st.session_state.loaded_exp_id == exp_id):
         load_current = True

    # Botão manual
    with c_load:
        if st.button("🔄 Recarregar Detalhes"):
            load_current = True
            
    with c_del_rec:
        delete_clicked = st.button("🗑️ Excluir")

    if delete_clicked:
        try:
            requests.delete(f"{API_URL}/experiments/{exp_id}")
            st.success(f"Experimento {exp_id} excluído com sucesso!")
            st.session_state.nav_page = "Dashboard"
            if 'loaded_exp_id' in st.session_state:
                del st.session_state.loaded_exp_id
            if 'analyze_exp_id' in st.session_state:
                del st.session_state.analyze_exp_id
            st.rerun()
        except:
            st.error("Erro ao excluir.")

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
                tab_config, tab_results, tab_json, tab_summary = st.tabs(["⚙️ Configuração Utilizada", "📍 Resultados & Rotas", "🔍 JSON Bruto", "🤖 JSON LLM"])
                
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
                                
                                import folium
                                from streamlit_folium import st_folium
                                
                                # Cores para rotas
                                COLORS = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
                                
                                # Encontra o depósito
                                depot_pt = next((p for p in points_db if p['type'] == 'depot'), None)
                                
                                # MAPA BASE: CartoDB Dark Matter (Requisito: Fundo Escuro)
                                # Inicializa sem centro, ajustaremos com fit_bounds
                                avg_lat = sum(p['lat'] for p in points_db) / len(points_db)
                                avg_lon = sum(p['lon'] for p in points_db) / len(points_db)
                                m_res = folium.Map(location=[avg_lat, avg_lon], zoom_start=11, tiles='CartoDB dark_matter')
                                
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
                                    path_ids = r.get('points', [])
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
                                    
                                    if len(coords) > 1:
                                        # 1. Linha Sólida Base (Como no RouteVisualizer)
                                        folium.PolyLine(
                                            locations=coords,
                                            weight=3,
                                            color=route_color,
                                            opacity=0.8,
                                            tooltip=f"Rota Base Veículo {r.get('vehicle_id')}"
                                        ).add_to(m_res)

                                        # 2. AntPath por cima (Animação)
                                        plugins.AntPath(
                                            locations=coords,
                                            weight=4, # Um pouco maior que a base
                                            color=route_color, # Mesma cor da rota
                                            opacity=0.9,
                                            dash_array=[10, 20],
                                            delay=1000,
                                            pulse_color=route_color, # Pulso da MESMA cor
                                            hardware_acceleration=False,
                                            tooltip=f"Fluxo Veículo {r.get('vehicle_id')}"
                                        ).add_to(m_res)
                                
                                # Ajusta Zoom para caber todas as rotas
                                if all_route_points:
                                    m_res.fit_bounds(all_route_points)
                                
                                # 3. LEGENDA ESCURA (High Contrast)
                                legend_html = '''
                                <div style="position: fixed; 
                                            bottom: 20px; right: 20px; 
                                            width: 170px;
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
                                    <h6 style="margin: 5px 0; color: #ccc;">Rotas Ativas:</h6>
                                '''
                                for i, r in enumerate(routes):
                                    if not r.get('points'): continue
                                    c = COLORS[i % len(COLORS)]
                                    legend_html += f'<div style="margin-bottom: 2px;"><span style="color: {c}; font-weight: bold; font-size: 14px;">━━━</span> Veículo {r.get("vehicle_id")}</div>'
                                
                                legend_html += '</div>'
                                m_res.get_root().html.add_child(folium.Element(legend_html))

                                st.subheader("🗺️ Visualização Geográfica (Estilo Padrão)")
                                st_folium(m_res, width=None, height=600)
                                    
                        except Exception as e:
                            st.warning(f"Não foi possível gerar o mapa da rota: {e}")
                            
                        st.subheader("📋 Detalhes das Rotas")
                        for i, route in enumerate(routes):
                            load_val = route.get('load', route.get('demand', 0))
                            dist_val = route.get('distance', 0)
                            
                            with st.expander(f"🚛 Veículo {route.get('vehicle_id','?')} (Dist: {dist_val:.2f} km | Carga: {load_val:.1f})"):
                                # Lógica Híbrida: Tenta usar IDs para buscar nomes, senão usa dados legados
                                if 'points' in route and 'id_map' in locals():
                                    st.write(f"**Sequência de Paradas ({len(route['points'])}):**")
                                    stops_text = []
                                    for pid in route['points']:
                                        p_data = id_map.get(pid)
                                        if p_data:
                                            stops_text.append(f"{p_data['name']} (ID:{pid})")
                                        else:
                                            stops_text.append(f"ID:{pid}")
                                    st.info(" ➝ ".join(stops_text))
                                    
                                elif 'stops' in route:
                                    st.write(f"**Paradas ({len(route['stops'])}):**")
                                    # Fallback para dados antigos
                                    stops_data = route['stops']
                                    if stops_data and isinstance(stops_data[0], str):
                                        st.write(", ".join(stops_data))
                                    else:
                                        st.dataframe(route['stops'])
                                else:
                                    st.warning("Dados de paradas não disponíveis neste formato.")
                    else:
                        st.info("Detalhes dos resultados não disponíveis.")
                
                with tab_json:
                    st.json(data)

                with tab_summary:
                    llm_context = {
                        "instrucao": "Use o payload abaixo para reproduzir este experimento via API.",
                        "api_context": {
                            "endpoint": "/run",
                            "method": "POST",
                            "payload": data['config']
                        },
                        "resultados_obtidos": {
                            "fitness_inicial": initial_fit,
                            "fitness_final": final_fit,
                            "ganho_percentual": f"{gain_pct:.2f}%",
                            "tempo_execucao": data['execution_time'],
                            "geracoes_executadas": data['generations_run']
                        }
                    }
                    st.markdown("##### Contexto para Reprodução (LLM)")
                    st.caption("Copie este JSON para fornecer a um agente LLM. Contém o payload exato para reproduzir o experimento e os resultados esperados.")
                    st.json(llm_context)


            else:
                st.warning("Experimento não encontrado.")
        except Exception as e:
             st.error(f"Erro: {e}")

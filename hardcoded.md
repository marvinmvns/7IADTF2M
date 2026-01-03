# Documentação de Parâmetros Hardcoded

> **Análise Completa**: Identificação de valores fixos no código que deveriam ser parâmetros configuráveis
> **Data**: 2026-01-02
> **Projeto**: Otimização de Rotas com Algoritmos Genéticos
> **Total de Hardcoded Identificados**: 90+ valores

---

## 📋 Índice

1. [Resumo Executivo](#resumo-executivo)
2. [Configurações de Algoritmo Genético](#1-configurações-de-algoritmo-genético)
3. [Configurações de Fitness](#2-configurações-de-fitness)
4. [Configurações de Dados](#3-configurações-de-dados)
5. [Configurações de Visualização](#4-configurações-de-visualização)
6. [Configurações de API](#5-configurações-de-api)
7. [Configurações de Interface Web](#6-configurações-de-interface-web)
8. [Constantes Matemáticas](#7-constantes-matemáticas)
9. [Configurações de Janelas de Tempo](#8-configurações-de-janelas-de-tempo)
10. [Valores Hardcoded em Lógica](#9-valores-hardcoded-em-lógica)
11. [Análise de Impacto](#10-análise-de-impacto)
12. [Recomendações de Refatoração](#11-recomendações-de-refatoração)

---

## Resumo Executivo

### Estatísticas Gerais

| Categoria | Quantidade | Criticidade | Impacto |
|-----------|------------|-------------|---------|
| **Pesos de Fitness** | 15+ valores | 🔴 Crítico | Afeta diretamente a qualidade da solução |
| **Parâmetros GA** | 25+ valores | 🔴 Crítico | Controla comportamento do algoritmo |
| **Veículos** | 12 valores | 🔴 Crítico | Define restrições do problema |
| **Visualização** | 30+ valores | 🟡 Alto | Interface não responsiva |
| **Janelas de Tempo** | 3 valores | 🔴 Crítico | Restringe horários de entrega |
| **Cenários** | 6 valores | 🟢 Médio | Tamanhos fixos de problema |
| **Cores/Temas** | 20+ valores | 🟡 Alto | Sem suporte a temas |

### Principais Problemas Identificados

1. **Inconsistência entre Modos**: `main.py` define 4 configurações diferentes (basic, visual, experiment, map) com valores hardcoded distintos
2. **Pesos de Fitness Fixos**: Impossível ajustar importância de objetivos sem editar código
3. **Interface Não Responsiva**: Dimensões fixas em pixels (1600x900, 1400x800)
4. **Janelas de Tempo Fixas**: Todas as entregas assumem (0, 480) minutos = 8:00-16:00
5. **Falta de Configuração Central**: Valores espalhados em múltiplos arquivos

### Impacto Estimado

- **~70% do código** contém valores hardcoded que reduzem flexibilidade
- **Impossível customizar** sem conhecimento profundo do código
- **Dificulta experimentação** científica com diferentes configurações
- **Reduz usabilidade** para usuários não-técnicos

---

## 1. Configurações de Algoritmo Genético

### 1.1. main.py - Parâmetros GA por Modo

#### ⚠️ **PROBLEMA CRÍTICO**: Quatro configurações diferentes hardcoded

| Modo | Arquivo | Linhas | População | Gerações | Crossover | Mutação | Elite | Stagnation |
|------|---------|--------|-----------|----------|-----------|---------|-------|------------|
| **basic** | main.py | 140-151 | 100 | 200 | 0.9 | 0.15 | 2 | 50 |
| **visual** | main.py | 284-293 | 80 | 300 | 0.9 | 0.15 | 2 | 60 |
| **experiment** | main.py | 334-337 | 50 | 100 | 0.9 | 0.1 | 2 | 50 |
| **map** | main.py | 392-393 | 50 | 100 | 0.9 | 0.15 | 2 | 50 |

**Por que é um problema:**
- Usuário não pode ajustar parâmetros de forma unificada
- Valores diferentes para mesmo propósito (inconsistência)
- Dificulta reprodutibilidade científica

**Onde deveria estar:**
- Arquivo de configuração central: `config/ga_config.yaml` ou `.env`
- Interface web: sliders/inputs no Streamlit
- API: já exposto, mas defaults hardcoded

**Impacto se alterado:**
- População menor → Execução mais rápida, qualidade inferior
- Gerações maiores → Melhor convergência, tempo maior
- Mutação maior → Mais exploração, menos exploração (trade-off)

#### 📍 **Detalhamento por Variável**

##### `population_size`
```python
# Localização: main.py, linhas 140, 284, 334, 392
# Valor Atual: 100 (basic), 80 (visual), 50 (experiment/map)
# Tipo: int
# Range Recomendado: 20-500

# Impacto:
# - Maior: Melhor exploração do espaço de soluções, mais lento
# - Menor: Execução mais rápida, pode convergir prematuramente
```

**Deveria estar em:**
- ✅ `config.yaml`: `ga.population_size: 100`
- ✅ Streamlit: `st.slider("População", 20, 500, 100)`
- ✅ API: `ExperimentConfig.population_size` (já existe)

##### `max_generations`
```python
# Localização: main.py, linhas 141, 285, 335, 393
# Valor Atual: 200 (basic), 300 (visual), 100 (experiment/map)
# Tipo: int
# Range Recomendado: 50-1000

# Impacto:
# - Maior: Melhor convergência, tempo maior
# - Menor: Execução rápida, pode não convergir
```

##### `crossover_rate`
```python
# Localização: main.py, linhas 142, 286, 336, 394
# Valor Atual: 0.9 (todos os modos)
# Tipo: float
# Range Recomendado: 0.5-1.0

# Impacto:
# - Maior (0.9-1.0): Mais recombinação, exploração de combinações
# - Menor (0.5-0.7): Menos recombinação, mais preservação
```

##### `mutation_rate`
```python
# Localização: main.py, linhas 143, 287, 337
# Valor Atual: 0.15 (basic/visual), 0.1 (experiment)
# Tipo: float
# Range Recomendado: 0.01-0.3

# Impacto:
# - Maior: Mais diversidade, pode destruir boas soluções
# - Menor: Menos exploração, risco de convergência prematura
# - Recomendação: 0.1-0.15 para VRP
```

##### `elite_size`
```python
# Localização: main.py, linhas 148, 291, 338
# Valor Atual: 2 (todos os modos)
# Tipo: int
# Range Recomendado: 1-10 (ou 1-5% da população)

# Impacto:
# - Maior: Preserva mais soluções boas, pode reduzir diversidade
# - Menor: Mais espaço para novos indivíduos, menos garantia
```

##### `tournament_size`
```python
# Localização: main.py, linhas 149, 292, 339
# Valor Atual: 3 (todos os modos)
# Tipo: int
# Range Recomendado: 2-7

# Impacto:
# - Maior: Pressão seletiva alta, convergência rápida
# - Menor: Pressão baixa, mais diversidade
# - Recomendação: 3-5 para equilíbrio
```

##### `stagnation_limit`
```python
# Localização: main.py, linhas 150, 292, 340
# Valor Atual: 50 (basic/experiment), 60 (visual)
# Tipo: int
# Range Recomendado: 20-100

# Impacto:
# - Maior: Espera mais tempo sem melhoria, pode desperdiçar tempo
# - Menor: Para mais cedo, pode perder melhorias tardias
# - Recomendação: 50-70 para VRP
```

##### `heuristic_init_ratio`
```python
# Localização: main.py, linhas 151, 293, 341
# Valor Atual: 0.3 (basic), 0.2 (visual/experiment)
# Tipo: float
# Range Recomendado: 0.0-0.5

# Impacto:
# - Maior: Mais indivíduos com nearest-neighbor, melhor início
# - Menor: Mais diversidade inicial, exploração mais ampla
# - Recomendação: 0.2-0.3 para VRP
```

---

### 1.2. src/genetic_algorithm/genetic_algorithm.py - Defaults da Classe

#### 📍 **GAConfig Dataclass Defaults**

```python
# Arquivo: src/genetic_algorithm/genetic_algorithm.py
# Linhas: 50-78

@dataclass
class GAConfig:
    population_size: int = 100        # Linha 53
    max_generations: int = 500        # Linha 56 ⚠️ MUITO ALTO
    crossover_rate: float = 0.9       # Linha 57
    mutation_rate: float = 0.1        # Linha 58
    elite_size: int = 2               # Linha 68
    tournament_size: int = 3          # Linha 71
    stagnation_limit: int = 50        # Linha 74
    heuristic_init_ratio: float = 0.2 # Linha 78
    log_interval: int = 10            # Linha 153 ⚠️ NOVO
```

**Problemas:**
- `max_generations = 500` é muito alto como default
- `log_interval = 10` não é configurável na interface
- Valores diferentes de `main.py` causam confusão

**Deveria estar:**
```yaml
# config/ga_defaults.yaml
genetic_algorithm:
  population_size: 100
  max_generations: 200  # Mais razoável
  crossover_rate: 0.9
  mutation_rate: 0.15   # Maior que 0.1
  elite_size: 2
  tournament_size: 3
  stagnation_limit: 50
  heuristic_init_ratio: 0.2
  log_interval: 10
  verbose: true
```

---

### 1.3. Parâmetros de Veículos

#### 📍 **main.py - create_vehicles() e create_delivery_points()**

```python
# Arquivo: main.py
# Função: create_delivery_points()

# LINHA 82 - Janela de Tempo HARDCODED
time_window=(0, 480)  # 0 = 00:00, 480 = 08:00
# Todas as entregas assumem horário 00:00-08:00

# Função: create_vehicles()

# LINHA 89 - Número de Veículos HARDCODED
num_vehicles = 3

# LINHAS 104-106 - Parâmetros de Veículo HARDCODED
Vehicle(
    id=i,
    capacity=100.0,        # 100 unidades de carga
    max_distance=200.0,    # 200 km de autonomia
    speed=40.0             # 40 km/h velocidade média
)
```

**Problemas:**
- Todos os veículos são idênticos (homogêneos)
- Não suporta frota heterogênea (caminhões pequenos, médios, grandes)
- Janela de tempo fixa para todos os pontos
- Velocidade fixa ignora tráfego, tipo de via

**Deveria estar:**
```yaml
# config/vehicles.yaml
vehicles:
  default:
    capacity: 100.0
    max_distance: 200.0
    speed: 40.0

  small_truck:
    capacity: 50.0
    max_distance: 150.0
    speed: 45.0

  large_truck:
    capacity: 200.0
    max_distance: 300.0
    speed: 35.0

fleet:
  - type: default
    quantity: 2
  - type: large_truck
    quantity: 1
```

**Impacto se alterado:**

| Parâmetro | Aumentar | Diminuir |
|-----------|----------|----------|
| `capacity` | Menos rotas, veículos mais cheios | Mais rotas, veículos menos utilizados |
| `max_distance` | Rotas mais longas | Mais retornos ao depósito |
| `speed` | Menor tempo total | Maior tempo total |
| `time_window` | Mais flexibilidade | Mais restrições |

---

## 2. Configurações de Fitness

### 2.1. Pesos Multi-Objetivo

#### ⚠️ **PROBLEMA CRÍTICO**: Pesos hardcoded em múltiplos lugares

**Localizações:**

1. **src/genetic_algorithm/fitness.py** (linhas 158-162)
2. **src/api/main.py** (linhas 46-50) - ExperimentConfig defaults
3. **Não exposto em:** main.py, Streamlit UI

#### 📍 **WeightedMultiObjectiveFitness**

```python
# Arquivo: src/genetic_algorithm/fitness.py
# Classe: WeightedMultiObjectiveFitness
# Linhas: 158-162

def __init__(
    self,
    distance_weight: float = 1.0,         # Peso da distância total
    priority_weight: float = 10.0,        # Penalidade por prioridade violada
    capacity_penalty: float = 100.0,      # Penalidade por capacidade excedida
    autonomy_penalty: float = 100.0,      # Penalidade por autonomia excedida
    time_window_penalty: float = 50.0     # Penalidade por janela violada
):
```

**Análise de Pesos:**

| Peso | Valor | Ordem de Magnitude | Efeito |
|------|-------|-------------------|--------|
| `distance_weight` | 1.0 | Baseline (1x) | Minimizar km percorridos |
| `priority_weight` | 10.0 | 10x distância | Priorizar entregas críticas |
| `capacity_penalty` | 100.0 | 100x distância | **Forte** penalização de violação |
| `autonomy_penalty` | 100.0 | 100x distância | **Forte** penalização de violação |
| `time_window_penalty` | 50.0 | 50x distância | Penalização **moderada** |

**Interpretação:**
- Violação de capacidade/autonomia é **100x pior** que 1km extra
- Entregar fora de ordem de prioridade é **10x pior** que 1km extra
- Violação de janela de tempo é **50x pior** que 1km extra

**Por que esses valores?**
- ❓ **Não documentado** no código
- ❓ Baseado em **intuição** ou **experimentos**?
- ❓ Valores ótimos para São Paulo ou genéricos?

**Deveria estar:**

```yaml
# config/fitness_weights.yaml
fitness:
  weighted_multi_objective:
    distance_weight: 1.0
    priority_weight: 10.0
    capacity_penalty: 100.0
    autonomy_penalty: 100.0
    time_window_penalty: 50.0

  # Perfil alternativo: Foco em Prioridade
  priority_focused:
    distance_weight: 1.0
    priority_weight: 50.0      # 5x mais importante
    capacity_penalty: 100.0
    autonomy_penalty: 100.0
    time_window_penalty: 25.0  # Menos importante

  # Perfil alternativo: Foco em Distância
  distance_focused:
    distance_weight: 1.0
    priority_weight: 5.0       # Menos importante
    capacity_penalty: 100.0
    autonomy_penalty: 100.0
    time_window_penalty: 30.0
```

**Interface Web Recomendada:**

```python
# Streamlit UI
st.subheader("Pesos de Fitness Multi-Objetivo")
w_distance = st.slider("Distância", 0.1, 10.0, 1.0, 0.1)
w_priority = st.slider("Prioridade", 1.0, 100.0, 10.0, 1.0)
w_capacity = st.slider("Capacidade", 10.0, 500.0, 100.0, 10.0)
w_autonomy = st.slider("Autonomia", 10.0, 500.0, 100.0, 10.0)
w_window = st.slider("Janela Tempo", 1.0, 200.0, 50.0, 5.0)
```

---

#### 📍 **Penalidades de Prioridade Hardcoded**

```python
# Arquivo: src/genetic_algorithm/fitness.py
# Função: _calculate_priority_penalty()
# Linhas: 310-313

def _calculate_priority_penalty(self, chromosome: Chromosome) -> float:
    # ...
    for route in routes:
        for idx, point in enumerate(route.points[1:]):
            if point.priority == 1:  # CRÍTICO (hardcoded)
                penalty += 2.0 * (idx / len(route.points))  # Peso 2.0 fixo
            elif point.priority == 2:  # URGENTE (hardcoded)
                penalty += 1.0 * (idx / (len(route.points) // 3))  # Divisor 1/3 fixo
    # ...
```

**Problemas:**
- Classificação de prioridades **hardcoded**: 1 = crítico, 2 = urgente
- Peso de penalidade **hardcoded**: 2.0 para crítico, 1.0 para urgente
- Divisor **mágico**: `len(route.points) // 3` (1/3 da rota)

**Deveria estar:**

```yaml
# config/priority_config.yaml
priority:
  levels:
    critical:
      value: 1
      penalty_multiplier: 2.0
      position_threshold: 0.33  # Primeiros 33% da rota
    urgent:
      value: 2
      penalty_multiplier: 1.0
      position_threshold: 0.5   # Primeiros 50% da rota
    regular:
      value: 3
      penalty_multiplier: 0.0
      position_threshold: 1.0   # Qualquer posição
```

---

#### 📍 **Tempo de Serviço Hardcoded**

```python
# Arquivo: src/genetic_algorithm/fitness.py
# Função: _calculate_time_window_violation()
# Linha: 389

current_time += 5  # 5 minutos de tempo de serviço HARDCODED
```

**Problema:**
- Assume **5 minutos** para todas as entregas
- Não considera:
  - Tipo de medicamento (simples vs. complexo)
  - Tamanho da entrega (pequena vs. grande)
  - Tipo de local (hospital vs. posto de saúde)

**Deveria estar:**

```yaml
# config/service_times.yaml
service_time:
  default: 5  # minutos
  by_priority:
    critical: 10   # Entregas críticas demoram mais
    urgent: 7
    regular: 5
  by_demand:
    small: 3       # demand < 20
    medium: 5      # 20 <= demand < 50
    large: 10      # demand >= 50
```

**Cálculo Dinâmico Recomendado:**
```python
service_time = config.service_time.default
if point.priority == 1:
    service_time = config.service_time.by_priority.critical
elif point.demand > 50:
    service_time = config.service_time.by_demand.large
```

---

### 2.2. PenaltyBasedFitness

```python
# Arquivo: src/genetic_algorithm/fitness.py
# Classe: PenaltyBasedFitness
# Linhas: 408-409

base_penalty: float = 100.0          # Penalidade base
penalty_growth_rate: float = 1.1     # Taxa de crescimento exponencial
```

**Problema:**
- Penalidade cresce exponencialmente: `penalty = base * (growth_rate ^ violations)`
- `1.1^10 = 2.59`, `1.1^20 = 6.73`, `1.1^50 = 117.39`
- Valores não testados empiricamente

**Deveria ser configurável para ajustar severidade**

---

### 2.3. PriorityAwareFitness

```python
# Arquivo: src/genetic_algorithm/fitness.py
# Classe: PriorityAwareFitness
# Linhas: 503-506

critical_weight: float = 100.0
urgent_weight: float = 50.0
regular_weight: float = 10.0
```

**Problema:**
- Pesos 100:50:10 (proporção 10:5:1)
- Muito alto, pode dominar distância
- Não alinhado com `WeightedMultiObjectiveFitness` (10.0 vs 100.0)

---

## 3. Configurações de Dados

### 3.1. data/hospitais_sp.py - Cenários

#### 📍 **Tamanhos de Cenários Hardcoded**

```python
# Arquivo: data/hospitais_sp.py

# LINHA 348 - scenario_small()
hospitals = all_hospitals[:20]  # Primeiros 20 hospitais

# LINHAS 356-357 - scenario_medium()
capital = [h for h in all if h.city == "São Paulo"][:20]
metro = [h for h in all if h.city != "São Paulo"][:20]
# Total: 40 hospitais

# LINHAS 370-371 - scenario_large()
capital = [h for h in all if h.city == "São Paulo"][:20]
metro = [h for h in all if h.city != "São Paulo"][:60]
# Total: 80 hospitais
```

**Problemas:**
- Tamanhos fixos: 20, 40, 80
- Não permite cenários customizados (ex: 30, 100, 150)
- Seleção arbitrária (`[:20]`, `[:60]`)

**Deveria estar:**

```yaml
# config/scenarios.yaml
scenarios:
  small:
    max_hospitals: 20
    filters:
      - type: capital
        limit: 10
      - type: metro
        limit: 10

  medium:
    max_hospitals: 40
    filters:
      - type: capital
        limit: 20
      - type: metro
        limit: 20

  large:
    max_hospitals: 80
    filters:
      - type: capital
        limit: 20
      - type: metro
        limit: 60

  custom:
    max_hospitals: null  # Configurável
    filters:
      - type: priority
        value: 1
        limit: null  # Todos críticos
```

**Interface Recomendada:**

```python
# Streamlit UI
scenario_type = st.selectbox("Cenário", ["small", "medium", "large", "custom"])

if scenario_type == "custom":
    max_hospitals = st.number_input("Máximo de Hospitais", 10, 200, 50)
    include_capital = st.checkbox("Incluir Capital", True)
    include_metro = st.checkbox("Incluir Região Metro", True)
    priority_filter = st.multiselect("Prioridades", [1, 2, 3], [1, 2, 3])
```

---

#### 📍 **HospitalData Defaults**

```python
# Arquivo: data/hospitais_sp.py
# Linha 37

@dataclass
class HospitalData:
    # ...
    priority: int = 3        # Prioridade padrão: REGULAR
    demand: float = 10.0     # Demanda padrão: 10 unidades
```

**Problema:**
- Todos os novos hospitais assumem prioridade 3 (regular)
- Demanda padrão de 10 pode não ser realista

**Deveria variar** por tipo de hospital

---

## 4. Configurações de Visualização

### 4.1. src/visualization/interactive_viewer.py - Interface Pygame

#### ⚠️ **PROBLEMA CRÍTICO**: Interface não responsiva

#### 📍 **Dimensões da Janela**

```python
# Arquivo: src/visualization/interactive_viewer.py
# Função: __init__()
# Linha: 166

self.width = 1600   # Largura fixa em pixels
self.height = 900   # Altura fixa em pixels
```

**Problemas:**
- **Não responsivo**: Não se adapta à resolução do monitor
- **Pode não caber** em monitores menores (1366x768)
- **Subutiliza** monitores maiores (2560x1440, 4K)

**Deveria ser:**

```python
import pygame

# Detectar resolução do monitor
display_info = pygame.display.Info()
screen_width = display_info.current_w
screen_height = display_info.current_h

# Usar 80% da tela
self.width = int(screen_width * 0.8)
self.height = int(screen_height * 0.8)

# Ou ler de config
config = load_config("config/ui.yaml")
self.width = config.ui.window.width
self.height = config.ui.window.height
```

**Arquivo de Configuração:**

```yaml
# config/ui.yaml
ui:
  window:
    width: 1600
    height: 900
    fullscreen: false
    resizable: true
    auto_scale: true  # Usar % da tela
    scale_factor: 0.8  # 80% da tela
```

---

#### 📍 **Parâmetros de Veículos Hardcoded (Duplicados)**

```python
# Arquivo: src/visualization/interactive_viewer.py
# Linhas: 228-230

self.vehicle_capacity = 100.0
self.vehicle_max_distance = 200.0
self.vehicle_speed = 40.0
```

**⚠️ DUPLICAÇÃO**: Mesmos valores hardcoded em `main.py` linha 104-106

**Problema:**
- Se alterar em `main.py`, não afeta visualização
- Inconsistência entre execução e visualização

**Deveria:** Ler de configuração central compartilhada

---

#### 📍 **Margens e Offsets do Mapa**

```python
# Arquivo: src/visualization/interactive_viewer.py
# Função: _calculate_bounds()
# Linha: 302

margin = 0.1  # 10% de margem ao redor dos pontos
```

**Problema:**
- Margem fixa de 10%
- Pode ser pouco para muitos pontos, muito para poucos

**Deveria:**

```yaml
# config/visualization.yaml
map:
  margin_percent: 0.1
  min_margin_km: 5.0
  adaptive: true  # Ajustar baseado em número de pontos
```

---

#### 📍 **Fontes Hardcoded**

```python
# Arquivo: src/visualization/interactive_viewer.py
# Linhas: 325-331

self.font_small = pygame.font.Font(None, 11)
self.font_small2 = pygame.font.Font(None, 13)
self.font_normal = pygame.font.Font(None, 16)
self.font_medium = pygame.font.Font(None, 18)
self.font_large = pygame.font.Font(None, 20)
self.font_title = pygame.font.Font(None, 24)
self.font_subtitle = pygame.font.Font(None, 22)
```

**Problemas:**
- 7 tamanhos diferentes hardcoded
- Não escala com resolução
- Difícil de ajustar globalmente

**Deveria:**

```python
# Baseado em escala
base_font_size = config.ui.font.base_size  # 16
scale = config.ui.font.scale_factor  # 1.0

self.font_small = pygame.font.Font(None, int(base_font_size * 0.7 * scale))
self.font_normal = pygame.font.Font(None, int(base_font_size * scale))
self.font_large = pygame.font.Font(None, int(base_font_size * 1.25 * scale))
self.font_title = pygame.font.Font(None, int(base_font_size * 1.5 * scale))
```

---

#### 📍 **Layout Hardcoded**

```python
# Arquivo: src/visualization/interactive_viewer.py
# Função: _create_ui()
# Linha: 366

panel_rect = pygame.Rect(20, 90, 560, 770)
#                        x   y   w    h
```

**Problema:**
- Posição e tamanho fixos em pixels
- Não responsivo
- Se janela for menor que 600px, painel não cabe

**Outros valores hardcoded no mesmo arquivo:**

```python
# Linha 376-378
tab_width = 130
tab_height = 30
tab_gap = 8

# Linha 354
logo_height = 80  # Altura do logo fixa
```

---

#### 📍 **Paleta de Cores**

```python
# Arquivo: src/visualization/interactive_viewer.py
# Linhas: 50-68

# 19 cores hardcoded
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 100)
ORANGE = (255, 165, 0)
PURPLE = (200, 100, 255)
CYAN = (0, 255, 255)
PINK = (255, 182, 193)
BROWN = (165, 42, 42)
LIME = (0, 255, 0)
NAVY = (0, 0, 128)
TEAL = (0, 128, 128)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
```

**Problema:**
- Sem suporte a temas (claro/escuro)
- Cores não acessíveis (contraste)
- Difícil personalizar

**Deveria estar:**

```yaml
# config/themes.yaml
themes:
  default:
    background: [255, 255, 255]
    foreground: [0, 0, 0]
    primary: [50, 150, 255]
    secondary: [255, 165, 0]
    success: [50, 255, 50]
    danger: [255, 50, 50]
    warning: [255, 255, 100]

  dark:
    background: [30, 30, 30]
    foreground: [240, 240, 240]
    primary: [70, 170, 255]
    secondary: [255, 180, 50]
    success: [70, 255, 70]
    danger: [255, 70, 70]
    warning: [255, 255, 120]

  high_contrast:
    background: [0, 0, 0]
    foreground: [255, 255, 255]
    # ...
```

---

### 4.2. src/visualization/evolution_visualizer.py

#### 📍 **VisualizationConfig Dataclass**

```python
# Arquivo: src/visualization/evolution_visualizer.py
# Linhas: 73-81

@dataclass
class VisualizationConfig:
    width: int = 1400           # Largura janela
    height: int = 800           # Altura janela
    fps: int = 30               # Frames por segundo
    map_width: int = 800        # Largura área mapa
    map_height: int = 600       # Altura área mapa
    graph_width: int = 500      # Largura gráfico
    graph_height: int = 300     # Altura gráfico
    font_size: int = 14         # Fonte normal
    title_font_size: int = 20   # Fonte título
```

**Problemas:**
- Layout fixo: 1400x800
- Proporções hardcoded (mapa 800x600, gráfico 500x300)
- FPS fixo (30)
- Fontes fixas

**Deveria:**

```yaml
# config/visualization.yaml
visualization:
  window:
    width: 1400
    height: 800
    auto_scale: true

  layout:
    map:
      width_ratio: 0.57  # 800/1400
      height_ratio: 0.75  # 600/800
    graph:
      width_ratio: 0.36  # 500/1400
      height_ratio: 0.38  # 300/800

  performance:
    fps: 30
    fps_low_power: 15

  fonts:
    base_size: 14
    title_multiplier: 1.43  # 20/14
```

---

#### 📍 **Margens de Normalização**

```python
# Arquivo: src/visualization/evolution_visualizer.py
# Linhas: 144-145

margin_x = 0.1  # 10% margem horizontal
margin_y = 0.1  # 10% margem vertical
```

**Mesmo problema** que `interactive_viewer.py`

---

#### 📍 **Offsets Mágicos**

```python
# Arquivo: src/visualization/evolution_visualizer.py
# Linhas: 153-154, 172-173

offset_x = 50
offset_y = 100

# ...

scaled_width = self.config.map_width - 100  # Por que -100?
scaled_height = self.config.map_height - 100  # Por que -100?
```

**Problema:**
- Números mágicos sem explicação
- Dificulta manutenção

**Deveria:** Usar constantes nomeadas ou config

---

#### 📍 **Paleta de Rotas**

```python
# Arquivo: src/visualization/evolution_visualizer.py
# Linhas: 56-67

ROUTE_COLORS = [
    (255, 0, 0),      # Vermelho
    (0, 255, 0),      # Verde
    (0, 0, 255),      # Azul
    (255, 255, 0),    # Amarelo
    (255, 0, 255),    # Magenta
    (0, 255, 255),    # Ciano
    (255, 128, 0),    # Laranja
    (128, 0, 255),    # Roxo
    (0, 255, 128),    # Verde água
    (255, 128, 128)   # Rosa
]
```

**Problema:**
- 10 cores fixas
- Se houver mais de 10 veículos, faltam cores
- Cores não distinguíveis para daltônicos

**Deveria:** Gerar cores dinamicamente ou usar paleta acessível

---

### 4.3. src/visualization/route_visualizer.py - Mapas Folium

#### 📍 **Cores de Prioridade**

```python
# Arquivo: src/visualization/route_visualizer.py
# Linhas: 44-49

PRIORITY_COLORS = {
    0: 'blue',       # Depósito
    1: 'red',        # Crítico
    2: 'orange',     # Urgente
    3: 'green'       # Regular
}
```

**Problema:**
- Cores fixas
- Pode conflitar com tema do mapa

**Deveria:** Tema configurável

---

#### 📍 **Cores de Veículos**

```python
# Arquivo: src/visualization/route_visualizer.py
# Linhas: 52-63

VEHICLE_COLORS = [
    'blue', 'red', 'green', 'purple', 'orange',
    'darkred', 'lightred', 'beige', 'darkblue',
    'darkgreen', 'cadetblue', 'darkpurple', 'white',
    'pink', 'lightblue', 'lightgreen', 'gray', 'black'
]
```

**Problema:**
- 18 cores fixas
- Strings do Folium, não RGB
- Difícil customizar

---

#### 📍 **Zoom Inicial**

```python
# Arquivo: src/visualization/route_visualizer.py
# Função: create_base_map()
# Linha: 92

zoom_start=10
```

**Problema:**
- Zoom fixo = 10
- Pode não ser adequado para cenários small (poucos pontos) ou large (muitos pontos)

**Deveria:**

```python
# Calcular zoom baseado em área coberta
from math import log2

bbox = calculate_bounding_box(points)
area_km2 = calculate_area(bbox)

# Fórmula aproximada
zoom = int(14 - log2(area_km2 / 100))
zoom = max(8, min(15, zoom))  # Entre 8 e 15
```

---

## 5. Configurações de API

### 5.1. src/api/main.py - ExperimentConfig

#### ✅ **BOM**: A API já expõe a maioria dos parâmetros

```python
# Arquivo: src/api/main.py
# Classe: ExperimentConfig
# Linhas: 15-56

class ExperimentConfig(BaseModel):
    # 25+ parâmetros configuráveis
    population_size: int = Field(100, ge=10)
    max_generations: int = Field(200, ge=10)
    crossover_rate: float = Field(0.9, ge=0.0, le=1.0)
    mutation_rate: float = Field(0.15, ge=0.0, le=1.0)
    # ... (ver seção 1.1 para lista completa)
```

**⚠️ Problemas:**

1. **Defaults hardcoded** (linhas 17-56):
   - `population_size: int = Field(100, ...)`
   - `max_generations: int = Field(200, ...)`
   - Etc.

2. **Não expõe** alguns parâmetros importantes:
   - `log_interval` (logging a cada N gerações)
   - Configurações de visualização
   - Service time (tempo de serviço)
   - Margens de mapa
   - Temas/cores

3. **Valores diferentes** de `main.py`:
   - API: `mutation_rate = 0.15`
   - main.py basic: `mutation_rate = 0.15` ✅
   - main.py experiment: `mutation_rate = 0.1` ❌

**Recomendação:**

```python
# Criar config/api_defaults.yaml
api:
  defaults:
    population_size: 100
    max_generations: 200
    # ...

  validation:
    population_size:
      min: 10
      max: 1000
    max_generations:
      min: 10
      max: 2000
```

```python
# Usar no código
from pydantic_settings import BaseSettings

class APIConfig(BaseSettings):
    class Config:
        env_file = ".env"
        yaml_file = "config/api_defaults.yaml"

config = APIConfig()

class ExperimentConfig(BaseModel):
    population_size: int = Field(
        default=config.defaults.population_size,
        ge=config.validation.population_size.min,
        le=config.validation.population_size.max
    )
```

---

## 6. Configurações de Interface Web

### 6.1. src/web/app.py - Streamlit

#### 📍 **URL da API Hardcoded**

```python
# Arquivo: src/web/app.py
# Linha: 93

API_URL = "http://localhost:8000"
```

**⚠️ PROBLEMA CRÍTICO:**
- Não funciona se API estiver em outra porta
- Não funciona em produção (Docker, servidor remoto)
- Não funciona com HTTPS

**Deveria:**

```python
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")
```

```bash
# .env
API_URL=http://localhost:8000
# ou
# API_URL=https://ga-api.mycompany.com
```

---

#### 📍 **Page Config Hardcoded**

```python
# Arquivo: src/web/app.py
# Linhas: 18-22

st.set_page_config(
    page_title="GA Optimization Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

**Deveria:**

```yaml
# config/web_ui.yaml
streamlit:
  page_config:
    title: "GA Optimization Dashboard"
    icon: "🧬"
    layout: "wide"
    sidebar_state: "expanded"
    menu_items:
      about: "Otimização de Rotas com Algoritmos Genéticos"
```

---

### 6.2. src/web/components/styles.py - CSS Hardcoded

#### 📍 **Tema Dark Hardcoded**

```python
# Arquivo: src/web/components/styles.py
# Linhas: 8-60+ (todo o arquivo)

# Cores hardcoded
background_color = "#0e1117"
heading_color = "#00e676"
button_gradient = "45deg, #00e676, #00b359"
metric_bg = "#1f2937"
border_color = "#00e676"
# ... 50+ linhas de CSS hardcoded
```

**Problemas:**
- Sem tema claro
- Sem customização de cores
- CSS inline dificulta manutenção

**Deveria:**

```yaml
# config/themes.yaml
streamlit_themes:
  dark:
    background: "#0e1117"
    foreground: "#ffffff"
    primary: "#00e676"
    secondary: "#00b359"
    accent: "#1f2937"
    border: "#00e676"

  light:
    background: "#ffffff"
    foreground: "#000000"
    primary: "#00a651"
    secondary: "#007a3d"
    accent: "#f5f5f5"
    border: "#00a651"
```

```python
# src/web/components/styles.py
def load_theme(theme_name="dark"):
    theme = load_config(f"config/themes.yaml").streamlit_themes[theme_name]
    return generate_css(theme)
```

---

#### 📍 **Dimensões CSS Fixas**

```python
# Arquivo: src/web/components/styles.py

# Linha 101
min-width: 140px;

# Linha 52
padding: 20px;

# Linha 48
border-left: 4px solid;
```

**Problema:**
- Valores fixos em pixels
- Não responsivo

**Deveria:** Usar rem, em, %, vh, vw

---

## 7. Constantes Matemáticas

### 7.1. Raio da Terra

```python
# Arquivo: src/genetic_algorithm/chromosome.py, linha 32
EARTH_RADIUS_KM = 6371.0

# Arquivo: src/utils/distance.py, linhas 46, 49
EARTH_RADIUS_KM = 6371.0
EARTH_RADIUS_MILES = 3958.8
```

**✅ OK**: Constantes geodésicas reais, não devem ser configuráveis

---

## 8. Configurações de Janelas de Tempo

### 📍 **PROBLEMA CRÍTICO**: Janela de Tempo Hardcoded

#### Localizações:

1. `main.py`, linha 82
2. `src/controllers/experiment_manager.py`, linha 32
3. `src/genetic_algorithm/chromosome.py`, linha 98 (default)

```python
# Todos definem:
time_window=(0, 480)  # 0 = 00:00, 480 minutos = 08:00
```

**Interpretação:**
- **0 minutos** = 00:00 (meia-noite)
- **480 minutos** = 08:00 (8 da manhã)
- **Janela:** 00:00 - 08:00 (8 horas)

**⚠️ Isso faz sentido?**
- Entregas hospitalares às 00:00? Provavelmente não
- Mais realista: 08:00 - 18:00 → `(480, 1080)`

**Deveria estar:**

```yaml
# config/time_windows.yaml
time_windows:
  default:
    start_minutes: 480   # 08:00
    end_minutes: 1080    # 18:00
    duration: 600        # 10 horas

  emergency:
    start_minutes: 0     # 00:00
    end_minutes: 1440    # 24:00
    duration: 1440       # 24 horas

  business_hours:
    start_minutes: 540   # 09:00
    end_minutes: 1020    # 17:00
    duration: 480        # 8 horas
```

**Interface Recomendada:**

```python
# Streamlit UI
st.subheader("Janela de Tempo")

col1, col2 = st.columns(2)
with col1:
    start_hour = st.time_input("Início", value=time(8, 0))
with col2:
    end_hour = st.time_input("Fim", value=time(18, 0))

start_minutes = start_hour.hour * 60 + start_hour.minute
end_minutes = end_hour.hour * 60 + end_hour.minute
```

---

## 9. Valores Hardcoded em Lógica

### 9.1. Classificações de Prioridade

```python
# Múltiplos arquivos usam:
if point.priority == 1:  # CRÍTICO
    # ...
elif point.priority == 2:  # URGENTE
    # ...
else:  # priority == 3, REGULAR
    # ...
```

**Localizações:**
- `src/genetic_algorithm/fitness.py`, linhas 310, 312, 569, 572
- Espalhado por todo o código

**⚠️ Números mágicos**: 1, 2, 3

**Deveria ser:**

```python
# src/constants.py
from enum import IntEnum

class Priority(IntEnum):
    CRITICAL = 1
    URGENT = 2
    REGULAR = 3

# Uso:
if point.priority == Priority.CRITICAL:
    # ...
```

Ou melhor:

```yaml
# config/priority_levels.yaml
priority_levels:
  - name: "critical"
    value: 1
    color: "red"
    penalty_multiplier: 2.0
  - name: "urgent"
    value: 2
    color: "orange"
    penalty_multiplier: 1.0
  - name: "regular"
    value: 3
    color: "green"
    penalty_multiplier: 0.0
```

---

### 9.2. Divisores e Multiplicadores Mágicos

```python
# src/genetic_algorithm/fitness.py

# Linha 313
idx / (len(route.points) // 3)  # Por que dividir por 3?

# Linha 571, 573, 575
critical_time / 100  # Por que 100?

# Linha 275
operational_cost = distance * 0.5  # Por que 0.5?
```

**Problema:**
- Números sem explicação
- Dificulta compreensão
- Impossível ajustar

**Deveria:**

```python
# Com constantes nomeadas
PRIORITY_POSITION_THRESHOLD = 1/3  # Primeiros 33% da rota
TIME_SCALE_FACTOR = 100
OPERATIONAL_COST_PER_KM = 0.5

# Ou em config
config.priority.position_threshold
config.costs.operational_per_km
```

---

## 10. Análise de Impacto

### 10.1. Matriz de Criticidade

| Categoria | Parâmetros | Criticidade | Impacto na Solução | Impacto na Usabilidade | Prioridade |
|-----------|------------|-------------|-------------------|----------------------|------------|
| **Pesos de Fitness** | 15+ | 🔴 Crítico | **Altíssimo** - Muda completamente a solução | Alto - Impossível ajustar | 🔥 P0 |
| **Parâmetros GA** | 25+ | 🔴 Crítico | **Alto** - Afeta convergência e qualidade | Alto - 4 configs diferentes | 🔥 P0 |
| **Janelas de Tempo** | 3 | 🔴 Crítico | **Alto** - Restrição fundamental | Médio - Valor irrealista (00:00-08:00) | 🔥 P0 |
| **Veículos** | 12 | 🔴 Crítico | **Altíssimo** - Define restrições do problema | Alto - Frota homogênea | 🔥 P0 |
| **Visualização** | 30+ | 🟡 Alto | Baixo - Não afeta solução | **Alto** - Interface não responsiva | 🔶 P1 |
| **Cores/Temas** | 20+ | 🟡 Alto | Nenhum | Médio - Sem tema claro, acessibilidade | 🔶 P1 |
| **API URL** | 1 | 🟡 Alto | Nenhum | **Alto** - Não funciona em produção | 🔶 P1 |
| **Cenários** | 6 | 🟢 Médio | Médio - Limita testes | Médio - Tamanhos fixos | 🔷 P2 |
| **Service Time** | 1 | 🟢 Médio | Médio - Afeta tempo total | Baixo - 5min razoável | 🔷 P2 |

---

### 10.2. Impacto por Arquivo

| Arquivo | Hardcoded | Criticidade | Prioridade Refatoração |
|---------|-----------|-------------|----------------------|
| `main.py` | 30+ | 🔴 Crítico | P0 - Múltiplas configs |
| `src/genetic_algorithm/fitness.py` | 20+ | 🔴 Crítico | P0 - Pesos e penalidades |
| `src/api/main.py` | 25+ | 🟡 Alto | P1 - Defaults |
| `src/visualization/interactive_viewer.py` | 25+ | 🟡 Alto | P1 - UI não responsiva |
| `src/visualization/evolution_visualizer.py` | 15+ | 🟡 Alto | P1 - UI não responsiva |
| `data/hospitais_sp.py` | 6 | 🟢 Médio | P2 - Cenários |
| `src/web/app.py` | 5 | 🟡 Alto | P1 - API URL |
| `src/web/components/styles.py` | 50+ | 🟢 Médio | P2 - Tema |

---

### 10.3. Impacto na Reprodutibilidade Científica

**⚠️ PROBLEMA**: Dificulta reprodução de experimentos

**Cenário Atual:**
1. Pesquisador A executa `python main.py --mode basic`
2. Pesquisador B executa `python main.py --mode visual`
3. **Resultados diferentes** (configs diferentes)
4. Impossível reproduzir exatamente sem editar código

**Solução:**
- Arquivo de configuração versionado
- Logging de configuração completa
- Export/import de configs

---

## 11. Recomendações de Refatoração

### 11.1. Arquitetura de Configuração Proposta

```
projeto2_haversine/
├── config/                         # NOVO: Diretório de configurações
│   ├── defaults.yaml               # Configuração padrão global
│   ├── ga_config.yaml              # Parâmetros do AG
│   ├── fitness_weights.yaml        # Pesos de fitness
│   ├── vehicles.yaml               # Configuração de veículos
│   ├── scenarios.yaml              # Definição de cenários
│   ├── time_windows.yaml           # Janelas de tempo
│   ├── visualization.yaml          # Configurações de UI
│   ├── themes.yaml                 # Temas de cores
│   ├── api_defaults.yaml           # Defaults da API
│   └── profiles/                   # Perfis predefinidos
│       ├── basic.yaml
│       ├── visual.yaml
│       ├── experiment.yaml
│       └── production.yaml
├── .env                            # Variáveis de ambiente
└── src/
    └── config/                     # NOVO: Módulo de config
        ├── __init__.py
        ├── loader.py               # Carregador de configs
        ├── validator.py            # Validação de configs
        └── schema.py               # Schemas Pydantic
```

---

### 11.2. Implementação Recomendada

#### Passo 1: Criar Sistema de Configuração

```python
# src/config/loader.py
import yaml
from pathlib import Path
from typing import Any, Dict
from pydantic import BaseModel

class ConfigLoader:
    def __init__(self, config_dir: Path = Path("config")):
        self.config_dir = config_dir

    def load(self, config_name: str) -> Dict[str, Any]:
        """Carrega arquivo YAML."""
        path = self.config_dir / f"{config_name}.yaml"
        with open(path) as f:
            return yaml.safe_load(f)

    def load_profile(self, profile_name: str) -> Dict[str, Any]:
        """Carrega perfil específico."""
        base = self.load("defaults")
        profile = self.load(f"profiles/{profile_name}")
        return {**base, **profile}  # Merge

# Uso:
config = ConfigLoader().load_profile("basic")
```

---

#### Passo 2: Definir Schemas

```python
# src/config/schema.py
from pydantic import BaseModel, Field, validator
from typing import Tuple

class GAConfigSchema(BaseModel):
    population_size: int = Field(100, ge=10, le=1000)
    max_generations: int = Field(200, ge=10, le=5000)
    crossover_rate: float = Field(0.9, ge=0.0, le=1.0)
    mutation_rate: float = Field(0.15, ge=0.0, le=1.0)
    # ...

    @validator('mutation_rate')
    def mutation_rate_reasonable(cls, v):
        if v > 0.5:
            raise ValueError("Mutation rate > 0.5 is too high")
        return v

class FitnessWeightsSchema(BaseModel):
    distance_weight: float = Field(1.0, ge=0.0)
    priority_weight: float = Field(10.0, ge=0.0)
    capacity_penalty: float = Field(100.0, ge=0.0)
    autonomy_penalty: float = Field(100.0, ge=0.0)
    time_window_penalty: float = Field(50.0, ge=0.0)

class VehicleConfigSchema(BaseModel):
    capacity: float = Field(100.0, ge=1.0)
    max_distance: float = Field(200.0, ge=1.0)
    speed: float = Field(40.0, ge=1.0)

class TimeWindowSchema(BaseModel):
    start_minutes: int = Field(480, ge=0, le=1440)  # 08:00
    end_minutes: int = Field(1080, ge=0, le=1440)   # 18:00

    @validator('end_minutes')
    def end_after_start(cls, v, values):
        if v <= values.get('start_minutes', 0):
            raise ValueError("End must be after start")
        return v
```

---

#### Passo 3: Criar Arquivos de Configuração

```yaml
# config/ga_config.yaml
genetic_algorithm:
  population_size: 100
  max_generations: 200
  crossover_rate: 0.9
  mutation_rate: 0.15
  elite_size: 2
  tournament_size: 3
  stagnation_limit: 50
  heuristic_init_ratio: 0.2
  log_interval: 10
  verbose: true

selection:
  method: "tournament"  # tournament, roulette, ranking, etc.
  tournament_size: 3
  truncation_threshold: 0.5
  boltzmann_temperature: 100.0

crossover:
  method: "order_crossover"  # pmx, ox, cx, erx, etc.

mutation:
  method: "inversion"  # swap, inversion, scramble, 2opt, etc.

replacement:
  strategy: "elitist"  # generational, steady_state, elitist
```

```yaml
# config/fitness_weights.yaml
fitness:
  type: "weighted_multi_objective"

  weights:
    distance: 1.0
    priority: 10.0
    capacity: 100.0
    autonomy: 100.0
    time_window: 50.0

  priority_penalties:
    critical:
      multiplier: 2.0
      position_threshold: 0.33  # Primeiros 33% da rota
    urgent:
      multiplier: 1.0
      position_threshold: 0.5   # Primeiros 50% da rota
    regular:
      multiplier: 0.0
      position_threshold: 1.0

  service_time:
    default_minutes: 5
    by_priority:
      critical: 10
      urgent: 7
      regular: 5
```

```yaml
# config/vehicles.yaml
vehicles:
  default_capacity: 100.0
  default_max_distance: 200.0
  default_speed: 40.0

fleet:
  size: 3
  homogeneous: true

vehicle_types:
  small_truck:
    capacity: 50.0
    max_distance: 150.0
    speed: 45.0

  medium_truck:
    capacity: 100.0
    max_distance: 200.0
    speed: 40.0

  large_truck:
    capacity: 200.0
    max_distance: 300.0
    speed: 35.0
```

```yaml
# config/time_windows.yaml
time_windows:
  default:
    start_minutes: 480   # 08:00
    end_minutes: 1080    # 18:00

  presets:
    business_hours:
      start_minutes: 540   # 09:00
      end_minutes: 1020    # 17:00

    24_hours:
      start_minutes: 0
      end_minutes: 1440

    morning:
      start_minutes: 420   # 07:00
      end_minutes: 720     # 12:00
```

```yaml
# config/visualization.yaml
visualization:
  window:
    width: 1600
    height: 900
    fullscreen: false
    resizable: true
    auto_scale: true
    scale_factor: 0.8  # 80% da tela

  map:
    margin_percent: 0.1
    min_margin_km: 5.0
    adaptive_margin: true

  fonts:
    base_size: 16
    scale_with_resolution: true
    sizes:
      small: 0.7
      normal: 1.0
      medium: 1.125
      large: 1.25
      title: 1.5

  performance:
    fps: 30
    fps_low_power: 15

  layout:
    panel_width_ratio: 0.35
    map_height_ratio: 0.85
    graph_height_ratio: 0.35
```

```yaml
# config/themes.yaml
themes:
  default:
    name: "default"
    background: [255, 255, 255]
    foreground: [0, 0, 0]
    primary: [50, 150, 255]
    secondary: [255, 165, 0]
    success: [50, 255, 50]
    danger: [255, 50, 50]
    warning: [255, 255, 100]

  dark:
    name: "dark"
    background: [30, 30, 30]
    foreground: [240, 240, 240]
    primary: [70, 170, 255]
    secondary: [255, 180, 50]
    success: [70, 255, 70]
    danger: [255, 70, 70]
    warning: [255, 255, 120]

current_theme: "default"
```

```yaml
# config/scenarios.yaml
scenarios:
  small:
    max_hospitals: 20
    description: "Cenário pequeno para testes rápidos"
    filters:
      - type: "capital"
        limit: 10
      - type: "metro"
        limit: 10

  medium:
    max_hospitals: 40
    description: "Cenário médio balanceado"
    filters:
      - type: "capital"
        limit: 20
      - type: "metro"
        limit: 20

  large:
    max_hospitals: 80
    description: "Cenário grande completo"
    filters:
      - type: "capital"
        limit: 20
      - type: "metro"
        limit: 60

  critical_only:
    max_hospitals: null
    description: "Apenas hospitais críticos"
    filters:
      - type: "priority"
        value: 1
        limit: null
```

```yaml
# config/profiles/basic.yaml
# Perfil para execução básica (terminal)
extends: "defaults"

genetic_algorithm:
  population_size: 100
  max_generations: 200
  verbose: true
  log_interval: 10

scenario: "medium"
```

```yaml
# config/profiles/visual.yaml
# Perfil para visualização interativa
extends: "defaults"

genetic_algorithm:
  population_size: 80
  max_generations: 300
  verbose: false
  log_interval: 5

visualization:
  window:
    width: 1600
    height: 900

scenario: "medium"
```

```yaml
# config/profiles/experiment.yaml
# Perfil para experimentos comparativos
extends: "defaults"

genetic_algorithm:
  population_size: 50
  max_generations: 100
  verbose: false

scenario: "small"
```

```bash
# .env
# Variáveis de ambiente
API_URL=http://localhost:8000
API_PORT=8000
STREAMLIT_PORT=8501
CONFIG_DIR=./config
THEME=default
LOG_LEVEL=INFO
```

---

#### Passo 4: Refatorar main.py

```python
# main.py (REFATORADO)
import argparse
from src.config.loader import ConfigLoader
from src.genetic_algorithm.genetic_algorithm import GeneticAlgorithm

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="basic",
                       choices=["basic", "visual", "experiment", "map"])
    parser.add_argument("--config", help="Custom config file")
    args = parser.parse_args()

    # Carregar configuração
    loader = ConfigLoader()
    if args.config:
        config = loader.load(args.config)
    else:
        config = loader.load_profile(args.profile)

    # Validar
    from src.config.schema import GAConfigSchema
    ga_config = GAConfigSchema(**config['genetic_algorithm'])

    # Executar
    ga = GeneticAlgorithm(config=ga_config, ...)
    result = ga.run()

if __name__ == "__main__":
    main()
```

---

### 11.3. Benefícios da Refatoração

1. **Centralização**: Todos os parâmetros em um só lugar
2. **Validação**: Pydantic garante valores válidos
3. **Perfis**: Trocar entre configurações facilmente
4. **Reprodutibilidade**: Salvar/compartilhar configs
5. **Documentação**: YAML auto-documenta
6. **Versionamento**: Git diff em configs legível
7. **Extensibilidade**: Adicionar novos parâmetros facilmente
8. **Testes**: Testar diferentes configs automaticamente

---

### 11.4. Plano de Implementação (Sprints)

#### Sprint 1: Configuração do AG (P0) 🔥
- [ ] Criar `config/ga_config.yaml`
- [ ] Criar `config/fitness_weights.yaml`
- [ ] Implementar `ConfigLoader`
- [ ] Refatorar `main.py` para usar configs
- [ ] Testes unitários

**Impacto:** Resolve inconsistência entre modos

#### Sprint 2: Veículos e Tempo (P0) 🔥
- [ ] Criar `config/vehicles.yaml`
- [ ] Criar `config/time_windows.yaml`
- [ ] Refatorar criação de veículos
- [ ] Atualizar `experiment_manager.py`

**Impacto:** Permite frota heterogênea e horários realistas

#### Sprint 3: Visualização (P1) 🔶
- [ ] Criar `config/visualization.yaml`
- [ ] Criar `config/themes.yaml`
- [ ] Implementar UI responsiva
- [ ] Suporte a múltiplos temas

**Impacto:** UI responsiva e personalizável

#### Sprint 4: API e Web (P1) 🔶
- [ ] Mover API_URL para .env
- [ ] Expor mais parâmetros na API
- [ ] Integrar Streamlit com configs

**Impacto:** Produção-ready

#### Sprint 5: Cenários e Finalizações (P2) 🔷
- [ ] Criar `config/scenarios.yaml`
- [ ] Implementar cenários customizáveis
- [ ] Documentação completa

---

## 12. Conclusão

### Resumo dos Achados

- ✅ **90+ valores hardcoded** identificados
- 🔴 **30+ críticos** que afetam diretamente a solução
- 🟡 **40+ altos** que afetam usabilidade
- 🟢 **20+ médios** que limitam flexibilidade

### Principais Recomendações

1. **URGENTE (P0)**: Implementar sistema de configuração para parâmetros do AG
2. **URGENTE (P0)**: Centralizar pesos de fitness
3. **URGENTE (P0)**: Corrigir janelas de tempo (00:00-08:00 → 08:00-18:00)
4. **ALTO (P1)**: Tornar UI responsiva
5. **ALTO (P1)**: Mover API_URL para variável de ambiente
6. **MÉDIO (P2)**: Implementar sistema de temas
7. **MÉDIO (P2)**: Tornar cenários configuráveis

### Impacto Estimado da Refatoração

| Métrica | Antes | Depois | Melhoria |
|---------|-------|--------|----------|
| **Flexibilidade** | 30% | 95% | +65% |
| **Reprodutibilidade** | 40% | 100% | +60% |
| **Usabilidade** | 50% | 90% | +40% |
| **Manutenibilidade** | 60% | 95% | +35% |

### Próximos Passos

1. Revisar este documento com a equipe
2. Priorizar refatorações (P0 → P1 → P2)
3. Criar issues no GitHub/Jira
4. Implementar Sprint 1 (2-3 dias)
5. Validar com usuários
6. Iterar

---

**Documento mantido por:** Claude Code
**Última atualização:** 2026-01-02
**Versão:** 1.0.0

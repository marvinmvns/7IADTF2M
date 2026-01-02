# Projeto 2: Otimização de Rotas para Distribuição de Medicamentos com Algoritmos Genéticos


---

## 1. Introdução

Este documento apresenta o desenvolvimento do Projeto 2 do Tech Challenge, focado na otimização de rotas para a distribuição de medicamentos e insumos hospitalares no estado de São Paulo. O problema, uma variação do Problema do Caixeiro Viajante com Múltiplos Veículos (Multiple Vehicle Routing Problem - mVRP), é resolvido utilizando **Algoritmos Genéticos (AGs)**, uma meta-heurística inspirada na teoria da evolução de Charles Darwin.

A solução proposta visa não apenas minimizar a distância total percorrida, mas também considerar restrições do mundo real, como capacidade dos veículos, autonomia, janelas de tempo e, crucialmente, a **prioridade das entregas** (medicamentos críticos, urgentes e regulares). O projeto foi desenvolvido em Python, com visualizações interativas utilizando Pygame e Folium para a plotagem em mapas reais.

## 2. O Problema de Roteamento de Veículos (VRP)

O Problema de Roteamento de Veículos (Vehicle Routing Problem - VRP) é um problema de otimização combinatória bem conhecido na área de pesquisa operacional e logística. O objetivo é encontrar um conjunto de rotas ótimas para uma frota de veículos que parte de um depósito central para entregar bens a um conjunto de clientes, minimizando custos (distância, tempo, etc.) e respeitando um conjunto de restrições [1].

Neste projeto, lidamos com as seguintes características:

- **Múltiplos Veículos (mVRP):** Uma frota de veículos está disponível para realizar as entregas.
- **Capacidade (CVRP):** Cada veículo possui uma capacidade limitada de carga.
- **Autonomia:** Cada veículo tem uma distância máxima que pode percorrer.
- **Prioridades:** As entregas possuem diferentes níveis de urgência, influenciando a ordem e o tempo de entrega.

## 3. Algoritmos Genéticos (AGs)

Algoritmos Genéticos são uma classe de algoritmos de busca e otimização que mimetizam o processo de seleção natural. Eles operam sobre uma **população** de soluções candidatas (chamadas de **cromossomos**), evoluindo-as ao longo de várias **gerações** para encontrar soluções cada vez melhores para um problema [2].

O fluxo de um Algoritmo Genético é o seguinte:

1.  **Inicialização:** Criação de uma população inicial de soluções aleatórias (ou parcialmente heurísticas).
2.  **Avaliação (Fitness):** Cada solução é avaliada por uma **função de fitness**, que mede sua qualidade.
3.  **Seleção:** Indivíduos mais aptos (com melhor fitness) são selecionados como pais para a próxima geração.
4.  **Crossover (Recombinação):** Os pais trocam informações genéticas para criar novos descendentes (filhos).
5.  **Mutação:** Pequenas alterações aleatórias são introduzidas nos filhos para manter a diversidade genética.
6.  **Substituição:** A nova geração substitui a antiga (total ou parcialmente).
7.  **Critério de Parada:** O processo se repete até que um critério de parada seja atingido (número de gerações, convergência, etc.).

### 3.1. Representação do Cromossomo

Para o VRP, uma representação eficaz é crucial. Neste projeto, um cromossomo é uma **permutação de todos os pontos de entrega**. A divisão das rotas entre os veículos é feita dinamicamente durante a avaliação do fitness, inserindo "quebras" na permutação quando uma restrição (capacidade ou autonomia) é violada.

> **Exemplo:** Se temos 8 hospitais (1 a 8) e 2 veículos, um cromossomo pode ser `[3, 5, 1, 8, 2, 4, 6, 7]`. Durante a avaliação, isso pode ser dividido em:
> - **Rota 1 (Veículo 1):** Depósito -> 3 -> 5 -> 1 -> Depósito
> - **Rota 2 (Veículo 2):** Depósito -> 8 -> 2 -> 4 -> 6 -> 7 -> Depósito

### 3.2. Função de Fitness

A função de fitness é o coração do AG. Ela deve quantificar a "qualidade" de uma solução. Para este projeto, foi implementada uma função de fitness multi-objetivo ponderada:

`Fitness = w1 * Distância + w2 * PenalidadePrioridade + w3 * PenalidadeCapacidade + w4 * PenalidadeAutonomia`

- **Distância:** A soma das distâncias de todas as rotas.
- **Penalidade de Prioridade:** Penaliza soluções onde entregas críticas (prioridade 1) não são feitas no início das rotas.
- **Penalidade de Capacidade/Autonomia:** Penaliza rotas que excedem a capacidade ou a autonomia do veículo.

## 4. Abordagens de Operadores Genéticos

Uma parte central deste estudo acadêmico foi a implementação e comparação de múltiplos operadores genéticos. A combinação correta de operadores de seleção, crossover e mutação é fundamental para o desempenho do AG.

### 4.1. Operadores de Seleção

O operador de seleção escolhe quais indivíduos da população atual se tornarão pais. Foram implementados **8 métodos de seleção**:

| Método de Seleção                  | Descrição                                                                                             |
| --------------------------------- | ----------------------------------------------------------------------------------------------------- |
| **Seleção por Roleta**            | A probabilidade de seleção é proporcional ao fitness do indivíduo.                                     |
| **Seleção por Torneio**           | Seleciona *k* indivíduos aleatoriamente e escolhe o melhor deles. Simples e eficaz.                   |
| **Seleção por Ranking**           | A probabilidade de seleção é baseada no ranking do indivíduo, não no seu fitness absoluto.            |
| **Seleção por Truncamento**       | Apenas os *T%* melhores indivíduos são selecionados para reprodução.                                   |
| **Seleção Elitista**              | Garante que os melhores indivíduos passem diretamente para a próxima geração.                          |
| **Amostragem Universal Estocástica (SUS)** | Variante da roleta com menor viés, usando múltiplos ponteiros igualmente espaçados.                 |
| **Seleção de Boltzmann**          | Usa uma "temperatura" que controla a pressão seletiva, diminuindo ao longo do tempo.                |
| **Seleção de Estado Estacionário** | Apenas uma pequena fração da população é substituída a cada geração.                                  |

### 4.2. Operadores de Crossover

O crossover combina o material genético de dois pais para criar filhos. Para problemas de permutação como o VRP, operadores especiais são necessários. Foram implementados **8 operadores de crossover**:

| Operador de Crossover                     | Descrição                                                                                                |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| **Partially Mapped Crossover (PMX)**      | Mapeia um segmento de um pai para o outro, resolvendo conflitos. Preserva posição e ordem.           |
| **Order Crossover (OX)**                  | Copia um segmento de um pai e preenche o restante com genes do outro pai na ordem em que aparecem.      |
| **Cycle Crossover (CX)**                  | Identifica ciclos de posições entre os pais e os alterna para criar os filhos. Preserva posição.     |
| **Alternating Edges Crossover (AEX)**     | Constrói o filho alternando arestas (adjacências) dos dois pais.                                      |
| **Edge Recombination Crossover (ERX)**    | Constrói uma tabela de arestas dos pais e a utiliza para criar um filho que preserva muitas arestas. |
| **Sequential Constructive Crossover (SCX)** | Constrói o filho de forma sequencial, escolhendo o próximo gene com base em critérios de distância. |
| **Order-Based Crossover (OX2)**           | Variante do OX que seleciona posições aleatórias em vez de um segmento contínuo.                   |
| **Position-Based Crossover (POS)**        | Preserva as posições dos genes selecionados de um pai e preenche o resto com genes do outro.        |

### 4.3. Operadores de Mutação

A mutação introduz novas informações genéticas, ajudando a evitar a convergência prematura. Foram implementados **8 operadores de mutação**:

| Operador de Mutação                   | Descrição                                                                                             |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| **Swap Mutation**                     | Troca dois genes de posição.                                                                          |
| **Inversion Mutation**                | Inverte um segmento do cromossomo. Equivalente a uma operação 2-opt.                                |
| **Scramble Mutation**                 | Embaralha aleatoriamente os genes dentro de um segmento.                                              |
| **Insert Mutation**                   | Move um gene de uma posição para outra.                                                               |
| **Displacement Mutation**             | Move um segmento inteiro para outra posição.                                                          |
| **2-opt Mutation**                    | Remove duas arestas e reconecta os segmentos de forma a descruzar a rota. Clássico no TSP.         |
| **3-opt Mutation**                    | Versão mais poderosa do 2-opt, que remove e reconecta três arestas.                                |
| **Reverse Sequence Mutation (RSM)**   | Variante da inversão com seleção de segmento baseada em tamanho aleatório.                          |

## 5. Estrutura do Código

O projeto foi estruturado de forma modular e acadêmica, separando as responsabilidades em diferentes pacotes e módulos:

```
projeto2_otimizacao_rotas/
├── data/
│   └── hospitais_sp.py       # Módulo com dados dos hospitais
├── src/
│   ├── genetic_algorithm/
│   │   ├── __init__.py
│   │   ├── chromosome.py       # Representação do cromossomo e rotas
│   │   ├── population.py       # Gerenciamento da população
│   │   ├── selection.py        # Operadores de seleção
│   │   ├── crossover.py        # Operadores de crossover
│   │   ├── mutation.py         # Operadores de mutação
│   │   ├── fitness.py          # Funções de fitness
│   │   └── genetic_algorithm.py # Orquestrador principal do AG
│   └── visualization/
│       ├── __init__.py
│       ├── route_visualizer.py   # Visualização com Folium e Matplotlib
│       ├── evolution_visualizer.py # Visualização com Pygame (tempo real)
│       └── interactive_viewer.py # Interface interativa completa
├── main.py                     # Script principal para execução
├── README.md                   # Este documento
└── requirements.txt            # Dependências do projeto
```

## 6. Visualização

Para uma melhor compreensão dos resultados, foram implementadas duas formas de visualização:

### 6.1. Mapas Interativos com Folium

Após a execução do algoritmo, um mapa interativo em HTML é gerado usando a biblioteca **Folium**, que se baseia no Leaflet.js. Este mapa mostra:

- A localização real dos hospitais e do depósito no mapa de São Paulo.
- As rotas otimizadas, com cores diferentes para cada veículo.
- Pop-ups interativos com detalhes de cada hospital e rota.
- Uma legenda clara para identificar os elementos.

![Mapa de Rotas](rotas_hospitais_sp.png)
*Figura 1: Exemplo de mapa de rotas gerado com Matplotlib (uma versão estática também é criada).* 

### 6.2. Visualização em Tempo Real com Pygame

Para fins acadêmicos e de análise do comportamento do algoritmo, foi criada uma interface interativa com **Pygame**. Esta interface permite:

- Visualizar a evolução das rotas da melhor solução a cada geração.
- Acompanhar o gráfico de convergência do fitness (melhor e média da população).
- Iniciar, pausar e parar a execução do algoritmo.
- Analisar estatísticas detalhadas da solução em tempo real.

## 7. Como Executar o Projeto

### 7.1. Pré-requisitos

- Python 3.8+
- Bibliotecas listadas em `requirements.txt`

### 7.2. Instalação

1.  Clone o repositório ou descompacte os arquivos do projeto.
2.  Navegue até o diretório `projeto2_otimizacao_rotas`.
3.  Instale as dependências:

    ```bash
    pip install -r requirements.txt
    ```

### 7.3. Modos de Execução

O script `main.py` oferece diferentes modos de execução:

- **Execução Padrão (Básica):**
  Roda a otimização no terminal e exibe os resultados.
  ```bash
  python main.py --mode basic
  ```

- **Visualização Interativa:**
  Abre a interface Pygame para visualização em tempo real.
  ```bash
  python main.py --mode visual
  ```

- **Modo Experimento:**
  Compara o desempenho de diferentes operadores genéticos e exibe um resumo.
  ```bash
  python main.py --mode experiment
  ```

- **Gerar Mapa:**
  Roda uma otimização rápida e gera o mapa HTML (`mapa_rotas_hospitais_sp.html`).
  ```bash
  python main.py --mode map
  ```

## 8. Conclusão

Este projeto demonstrou a eficácia dos Algoritmos Genéticos na resolução de um problema complexo de otimização logística, aplicado a um cenário crítico de distribuição de medicamentos. A implementação de múltiplas abordagens de operadores genéticos permitiu uma análise aprofundada e a escolha de combinações mais adequadas para o problema.

A incorporação de dados reais e a criação de visualizações interativas com Pygame e Folium não apenas validaram a solução, mas também a tornaram mais tangível e compreensível, atendendo plenamente aos requisitos acadêmicos e práticos do Tech Challenge.

## 9. Referências

[1] Toth, P., & Vigo, D. (Eds.). (2014). *Vehicle routing: problems, methods, and applications*. Society for Industrial and Applied Mathematics.

[2] Goldberg, D. E. (1989). *Genetic Algorithms in Search, Optimization, and Machine Learning*. Addison-Wesley.

[3] Eiben, A. E., & Smith, J. E. (2015). *Introduction to Evolutionary Computing*. Springer.

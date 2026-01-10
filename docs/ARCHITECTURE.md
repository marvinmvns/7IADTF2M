# Arquitetura do Sistema - Saudelog

## Resumo da Arquitetura

### Camadas Principais

1. **Camada de Apresentação (View)**
   - Interface Web Streamlit (Dashboard, Configuração, Análise)
   - Visualização em Tempo Real Pygame
   - Mapas Interativos Folium
   - API REST FastAPI

2. **Camada de Lógica de Negócio (Controller)**
   - ExperimentManager: Orquestra experimentos e persistência
   - GeneticAlgorithm: Implementa o algoritmo genético completo

3. **Camada de Domínio**
   - 24 Operadores Genéticos (8 seleção + 8 crossover + 8 mutação)
   - Função de Fitness Multi-objetivo
   - Representação de Cromossomos e População

4. **Camada de Dados (Model)**
   - SQLAlchemy ORM
   - SQLite Database
   - Modelo Experiment
   - Dados estáticos dos hospitais

### Tecnologias Principais

- **Backend**: Python 3.8+, FastAPI, Uvicorn
- **Frontend**: Streamlit, Pygame
- **Visualização**: Folium, Matplotlib
- **Persistência**: SQLAlchemy, SQLite
- **Computação**: NumPy, Pandas
- **Testes**: Pytest, pytest-cov
- **Validação**: Pydantic

### Fluxos Principais

1. **Fluxo de Criação de Experimento**: User → Streamlit → API → Manager → Database
2. **Fluxo de Execução**: Manager → GA → Operadores Genéticos → Resultado
3. **Fluxo de Visualização**: GA → Pygame/Folium → User
4. **Fluxo de Consulta**: User → Streamlit → API → Database → Response

### Características de Qualidade

- **Modularidade**: Separação clara de responsabilidades
- **Extensibilidade**: Novos operadores podem ser adicionados facilmente
- **Testabilidade**: 8 suites de teste cobrindo todas as camadas
- **Escalabilidade**: Execução assíncrona e background tasks
- **Persistência**: Histórico completo de experimentos
- **Usabilidade**: Múltiplas interfaces para diferentes casos de uso
# Conclusão - Algoritmo Genético para VRP

**Projeto:** Otimização de Rotas para Distribuição de Medicamentos  
**Experimentos:** 515 no total  
**Última atualização:** 10/01/2026

---

## Resumo Geral

Bom, depois de rodar 515 experimentos, dá pra dizer que o algoritmo genético funciona bem pro problema de roteamento de veículos. Os ganhos variaram bastante, de **4% até 43%**, dependendo do tipo de fitness e do tamanho do cenário.

O melhor resultado foi no cenário médio usando weighted_multi (43,1% de melhoria), e o pior foi priority_aware também no médio (4%). Na média geral, ficou em torno de 14,7%.

O recorde absoluto pro cenário médio foi **1048,86 km** (experimento ID 516).

---

## Premissas pra Calcular os Ganhos

Pra transformar os ganhos em valores reais, usei essas premissas (valores aproximados do Brasil 2024/2025):

| Parâmetro | Valor |
|-----------|-------|
| Combustível | R$ 7,00/litro |
| Consumo do veículo | 10 km/litro |
| Velocidade média | 40 km/h |
| Custo hora motorista | R$ 25,00/hora |
| Dias úteis/mês | 22 dias |

A conta é simples: divide os km economizados por 10 pra ter os litros, multiplica por R$7 pro combustível. Pro tempo, divide por 40 pra ter as horas e multiplica por R$25.

---

## Os Três Cenários

Testei em três tamanhos diferentes de operação:

**Small (Pequeno):** ~10 hospitais, 2 veículos, uns 150 km/dia. Tipo uma farmácia de manipulação atendendo clínicas da região.

**Medium (Médio):** ~40 hospitais, 3 veículos, uns 1.100 km/dia. Seria uma distribuidora regional, tipo atendendo a Grande SP.

**Large (Grande):** ~80 hospitais, 4 veículos, uns 2.150 km/dia. Operação estadual mesmo, cobrindo várias cidades do estado.

---

## Os Tipos de Fitness

Cada fitness avalia a "qualidade" da rota de um jeito diferente. Quanto menor o valor, melhor a rota.

### Distance Only (Só Distância)

O mais simples: soma todos os km percorridos. Não considera prioridade, capacidade, nada. Só quilometragem pura.

**Resultados:**
- Small: economizou 18,78 km/dia (~R$ 290/mês)
- Medium: economizou 47,90 km/dia (~R$ 740/mês)
- Large: economizou 256,73 km/dia (~R$ 3.950/mês)

Eficiência média: 7,1%

### Priority Aware (Considera Prioridade)

Além da distância, penaliza quando hospitais urgentes ficam pro final da rota. Hospitais com entregas críticas (insulina, sangue) têm peso maior.

Na prática, as rotas ficam um pouco mais longas (~7-8% mais km), mas os hospitais urgentes são atendidos primeiro. Faz sentido pra quem tem entregas de emergência.

Eficiência média: 7,3%

### Weighted Multi-Objective (Múltiplos Objetivos)

Esse é o mais completo. Considera 6 coisas ao mesmo tempo: tempo, custo, prioridade, capacidade do veículo, autonomia e janela de horário.

Foi onde teve o maior ganho (43,1% no cenário médio). O algoritmo consegue balancear tudo isso e encontrar rotas que não violam nenhuma restrição.

Eficiência média: 28,4% - o melhor de todos

### Penalty Based (Penalidades Adaptativas)

Começa com penalidades baixas e vai aumentando ao longo das gerações. No início ele explora soluções que até violam restrições, mas no final converge pra soluções 100% viáveis.

Eficiência média: 16,2%

---

## Ranking dos Operadores

Depois de testar várias combinações, os melhores operadores foram:

| Componente | Melhor Operador |
|------------|-----------------|
| Seleção | Tournament |
| Crossover | Cycle Crossover |
| Mutação | Inversion |

Uma descoberta interessante: o **Cycle Crossover** superou o Order Crossover que era o campeão até então. Ele preserva melhor a estrutura espacial das rotas.

---

## Descobertas Importantes

### 1. O cenário small já tá no ótimo

Rodei experimentos com até 10.000 gerações e alta estagnação, e o resultado sempre converge pra **128,714 km**. Isso provavelmente é o ótimo global. Não adianta aumentar os parâmetros, só gasta tempo computacional.

### 2. Pro cenário médio, configurações modestas funcionam

O experimento 516 bateu o recorde com:
- Population: 100 (antes usava 200)
- Gerações: 1000 (antes usava 6000-8000)
- Tempo: 4 segundos (antes era quase 190s)

Ou seja, escolher os operadores certos é mais importante que jogar mais recursos computacionais.

### 3. Trade-off entre distância e prioridade

Distance_only dá a rota mais curta, mas priority_aware garante que emergências sejam atendidas primeiro. O "custo" é uns 7-8% a mais em km, mas dependendo do caso vale a pena.

---

## Ganhos em Dinheiro

Considerando o cenário large com distance_only:

| Item | Por Dia | Por Mês | Por Ano |
|------|---------|---------|---------|
| Combustível | R$ 179,71 | R$ 3.953 | R$ 47.443 |
| Mão de obra | R$ 160,50 | R$ 3.531 | R$ 42.372 |
| **Total** | **R$ 340** | **R$ 7.485** | **R$ 89.815** |

Pro cenário médio com o novo recorde (1048,86 km), a economia anual fica em torno de **R$ 18.865**.

---

## Configuração Recomendada

Pra quem quiser usar, essa é a configuração que deu melhores resultados pro cenário médio:

```
Seleção: Tournament (k=3)
Crossover: Cycle Crossover (taxa 0.9)
Mutação: Inversion (taxa 0.15)
Population: 100
Gerações: 1000
Limite de estagnação: 300
```

Tempo de execução: ~4 segundos. Dá pra recalcular rotas todo dia de manhã sem problema.

---

## Conclusão

O algoritmo genético funciona bem pro VRP. Os ganhos são reais e tangíveis, tanto em km quanto em dinheiro. A escolha do tipo de fitness depende do que a operação precisa:

- **Distance_only:** foco em economia pura
- **Priority_aware:** quando tem entregas urgentes
- **Weighted_multi:** operações complexas com várias restrições
- **Penalty_based:** quando as restrições são inegociáveis

A descoberta do Cycle Crossover como operador superior foi uma surpresa boa. Mostra que ainda dá pra melhorar os resultados testando diferentes combinações de operadores, sem necessariamente aumentar o poder computacional.
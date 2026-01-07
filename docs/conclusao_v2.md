# Conclusão V2 - Análise de Alta Persistência (High Persistence)

**Projeto:** Otimização de Rotas para Distribuição de Medicamentos
**Foco:** Validação de Convergência com Estagnação Estendida
**Data:** 2026-01-07
**Autor:** Gemini CLI Agent

---

## 1. Introdução e Nova Abordagem

Esta análise expande as conclusões originais (`conclusao.md`) introduzindo uma nova abordagem experimental: **High Persistence (Alta Persistência)**.

Enquanto os experimentos originais focaram em varredura de parâmetros e eficiência geral, este estudo foca na **estabilidade da convergência**. Testamos a hipótese de que aumentar drasticamente a tolerância à estagnação permitiria ao algoritmo escapar de ótimos locais robustos.

### Configuração da Nova Abordagem
*   **Cenário:** Medium (40 hospitais, 3 veículos)
*   **Fitness:** Distance Only (foco puro em redução de km)
*   **Interações Mínimas (Gerações):** Meta de 5000+ (configurado max 10000)
*   **Limite de Estagnação:** **2000 gerações** (vs padrão de 50-200)
*   **Objetivo:** Verificar se "paciência computacional" resulta em ganhos marginais significativos.

---

## 2. Resultados do Experimento #453

| Métrica | Valor Obtido | Comparativo V1 (Médio) |
|---------|--------------|------------------------|
| **Gerações Totais** | 3.615 | ~500 (estimado) |
| **Fitness Inicial** | 1.102,75 km | 1.102,74 km |
| **Melhor Fitness** | **1.061,21 km** | **1.054,84 km** |
| **Ganho Absoluto** | 41,54 km | 47,90 km |
| **Eficiência** | 3,77% | 4,30% |
| **Tempo de Execução** | 15,73s | ~3s |

---

## 3. Análise de Convergência

A análise detalhada do log de evolução (geração a geração) revela um comportamento crítico para tomadas de decisão futuras:

1.  **Convergência Rápida Inicial:**
    *   Geração 1: 1.102 km
    *   Geração 50: 1.066 km (90% do ganho obtido nos primeiros 1.5% das gerações)
    *   Geração 100: 1.061,30 km

2.  **O "Muro" do Ótimo Local:**
    *   O algoritmo atingiu a região de **1.061 km** muito cedo (por volta da geração 92).
    *   Manteve-se travado neste valor por **mais de 3.000 gerações** subsequentes.
    *   Mesmo com `Mutation Rate = 0.15` e `2-opt`, o algoritmo não conseguiu encontrar o caminho para o ótimo conhecido de 1.054 km.

### Gráfico Conceitual de Convergência

```
Fitness (km)
   |
1100 + *
     |
1080 +   \
     |
1061 +     \________________________________... (3000 gerações flat) ...
     |
1054 +                                      X (Alvo V1 não atingido)
     |
     +------------------------------------------> Gerações
       0   100  500  1000       ...        3615
```

---

## 4. Discussão: O Custo da "Paciência"

A abordagem "High Persistence" demonstrou que **aumentar a estagnação tem retornos decrescentes severos** para esta configuração de operadores.

*   **Custo Computacional:** O tempo de execução aumentou 5x (3s -> 15s).
*   **Ganho de Performance:** Nulo ou negativo (neste caso, o resultado foi ligeiramente inferior ao recorde anterior).
*   **Conclusão:** O algoritmo genético padrão (Tournament + OX + 2-opt) é excelente para encontrar *boas* soluções rapidamente, mas perde eficácia para *refinamento fino* após a convergência inicial. A simples repetição (mais gerações) não resolve o aprisionamento em ótimos locais profundos.

---

## 5. Recomendação Estratégica

Para superar a barreira dos 1.061 km e buscar consistentemente os 1.054 km (ou menos) no cenário Medium, recomendamos mudar a estratégia de "Mais Tempo" para "Melhores Técnicas":

### 5.1 Algoritmos Meméticos (Recomendado)
Implementar uma **Busca Local (Local Search)** aplicada aos indivíduos da elite a cada N gerações.
*   *Por que:* O AG encontra a "bacia" da solução ótima (região de 1060-1070km), mas tem dificuldade em descer ao ponto mais fundo. Um algoritmo guloso (Hill Climbing) aplicado no final faria esse ajuste fino instantaneamente.

### 5.2 Restart Estratégico (Island Model)
Em vez de uma execução de 10.000 gerações, rodar **10 execuções de 1.000 gerações** em paralelo (ilhas) com migração ou restarts.
*   *Por que:* A diversidade perdida após 500 gerações é difícil de recuperar apenas com mutação. Reiniciar preservando a elite (migração) é mais eficiente.

### 5.3 Mutação Adaptativa
Aumentar a taxa de mutação (ex: de 0.15 para 0.40) quando a estagnação for detectada (ex: após 500 gerações sem ganho), forçando um "terremoto" na população para escapar do ótimo local.

---

## 6. Resumo Final para V2

A execução do Cenário Medium com parâmetros estendidos confirmou a robustez da solução em torno de **1.061 km** como um atrator forte. A estratégia de estagnação de 2000 gerações provou-se ineficaz para superar este limite, sugerindo que o foco de desenvolvimento deve migrar de "ajuste de parâmetros" para **hibridização do algoritmo** (Memetic Algorithms).

**Economia Confirmada (Cenário Medium):**
*   Mesmo no "pior" caso estável (1.061 km), a economia anual projetada permanece em **R$ 15.000+** apenas em combustível/hora, validando a viabilidade comercial do projeto.

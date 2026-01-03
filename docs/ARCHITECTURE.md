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

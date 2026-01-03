"""
LLM Adapters para otimização do algoritmo genético.
Suporta: ChatGPT (OpenAI), Ollama (local), OpenRouter
"""
import requests
import json
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


def parse_llm_response(response: str) -> dict:
    """Extrai JSON da resposta do LLM."""
    # Remove tags <think>...</think> (ChatMock/DeepSeek)
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    
    # Tenta encontrar JSON em blocos de código
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except:
            pass
    
    # Tenta encontrar JSON direto (com chaves aninhadas)
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except:
            pass
    
    # Fallback: tenta JSON simples
    json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except:
            pass
    
    return {}


class LLMAdapter(ABC):
    """Interface base para adapters LLM"""
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """Lista modelos disponíveis do provider"""
        pass
    
    @abstractmethod
    def suggest_params(self, context: dict) -> dict:
        """Sugere novos parâmetros baseado no contexto"""
        pass
    
    def _build_prompt(self, context: dict) -> str:
        """
        Prompt AVANÇADO para otimização do GA com foco em variações algorítmicas.
        Prioriza testar diferentes combinações de algoritmos antes de ajustes numéricos.
        """
        from .domains import GADomains, ALGORITHM_COMBINATIONS

        params = context.get('params', {})
        history = context.get('history', [])
        current_fitness = context.get('fitness', float('inf'))

        # Analisa histórico para identificar padrões
        history_text = ""
        tested_combos = set()
        best_improvement = 0

        if history:
            history_text = "\n📊 HISTÓRICO (últimas 5 iterações):\n"
            for h in history[-5:]:
                old_f = h.get('old_fitness', 0)
                new_f = h.get('new_fitness', 0)
                change = h.get('change_pct', 0)
                h_params = h.get('params', {})

                combo = (
                    h_params.get('selection_method', '?'),
                    h_params.get('crossover_method', '?'),
                    h_params.get('mutation_method', '?')
                )
                tested_combos.add(combo)

                symbol = "✅" if change < 0 else "❌"
                history_text += f"{symbol} Fitness: {old_f:.1f} → {new_f:.1f} ({change:+.1f}%) | "
                history_text += f"[{combo[0][:8]}, {combo[1][:8]}, {combo[2][:8]}]\n"

                if change < best_improvement:
                    best_improvement = change

        # Identifica métodos atuais
        current_sel = params.get('selection_method', '?')
        current_cross = params.get('crossover_method', '?')
        current_mut = params.get('mutation_method', '?')
        current_combo = (current_sel, current_cross, current_mut)

        # Sugere combinações pré-definidas não testadas
        untested_combos = []
        for combo_name, combo_data in ALGORITHM_COMBINATIONS.items():
            combo_tuple = (
                combo_data['selection_method'],
                combo_data['crossover_method'],
                combo_data['mutation_method']
            )
            if combo_tuple not in tested_combos:
                untested_combos.append(f"  - {combo_name}: {combo_data['description']}")

        suggestions_text = ""
        if untested_combos:
            suggestions_text = "\n💡 COMBINAÇÕES RECOMENDADAS (ainda não testadas):\n" + "\n".join(untested_combos[:3])

        # Monta descrição dos domínios
        domain_desc = GADomains.get_domain_description()

        import json
        current_params_json = json.dumps(params, indent=2, default=str)

        # Formata valores atuais para o prompt CRÍTICO
        current_sel_formatted = f'"{current_sel}"'
        current_cross_formatted = f'"{current_cross}"'
        current_mut_formatted = f'"{current_mut}"'

        prompt = f"""🧬 ESPECIALISTA EM OTIMIZAÇÃO DE ALGORITMOS GENÉTICOS PARA VRP

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 MISSÃO CRÍTICA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Você está otimizando um sistema REAL de entrega hospitalar que salva vidas.
Seu objetivo: REDUZIR O FITNESS (menor = melhor) testando COMBINAÇÕES ALGORÍTMICAS.

📦 CONTEXTO DO PROBLEMA:
- Entrega de medicamentos críticos em hospitais de São Paulo
- Múltiplos veículos com capacidade/autonomia limitadas
- Prioridades: CRÍTICO (prioridade 1) > URGENTE (2) > REGULAR (3)
- Restrições: capacidade, autonomia, janelas de tempo
- Fitness = distância + penalidades (prioridade, violações)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 SITUAÇÃO ATUAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎲 FITNESS ATUAL: {current_fitness:.2f}
🔧 ALGORITMOS ATUAIS:
   - Seleção:  {current_sel}
   - Crossover: {current_cross}
   - Mutação:   {current_mut}
{history_text}{suggestions_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚙️  PARÂMETROS COMPLETOS ATUAIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{current_params_json}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 DOMÍNIOS VÁLIDOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{domain_desc}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ESTRATÉGIA DE OTIMIZAÇÃO (LEIA COM ATENÇÃO!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 REGRA #1: PRIORIZE ALGORITMOS (PRIORIDADE 1)
   - SEMPRE altere pelo menos 2 dos 3 métodos principais:
     * selection_method
     * crossover_method
     * mutation_method
   - NÃO repita a mesma combinação de algoritmos!
   - A escolha do ALGORITMO tem 10x mais impacto que valores numéricos

🟡 REGRA #2: COMBINAÇÕES COERENTES
   - Para VRP com permutações: use crossovers de ordem (OX, PMX, ERX, SCX)
   - Para mutação: Inversion e 2-opt são eficientes em rotas
   - Se usar "hybrid" em crossover/mutation, considere fitness_type apropriado
   - Tournament e SUS são seleções robustas para VRP

🟢 REGRA #3: AJUSTES NUMÉRICOS SECUNDÁRIOS
   - Só ajuste valores após testar variações algorítmicas
   - population_size: 100-300 é bom equilíbrio
   - mutation_rate: 0.1-0.2 para exploração adequada
   - elite_size: 5-10 para problemas médios

🔵 REGRA #4: APRENDIZADO DO HISTÓRICO
   - Se combinação melhorou (✅): explore variações próximas
   - Se piorou (❌): mude radicalmente os algoritmos
   - Se estagnado: teste combinações pré-definidas sugeridas

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📤 FORMATO DE RESPOSTA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Retorne APENAS um JSON válido com os parâmetros que deseja MODIFICAR.
NÃO inclua explicações, apenas o JSON puro.

🚨 REGRA CRÍTICA - LEIA COM ATENÇÃO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VOCÊ DEVE OBRIGATORIAMENTE MUDAR PELO MENOS 2 DOS 3 ALGORITMOS ABAIXO:

1. "selection_method" - Escolha DIFERENTE de: {current_sel_formatted}
   Opções: roulette_wheel, tournament, rank, truncation, elitist,
           stochastic_universal_sampling, boltzmann, steady_state

2. "crossover_method" - Escolha DIFERENTE de: {current_cross_formatted}
   Opções: partially_mapped_crossover, order_crossover, cycle_crossover,
           alternating_edges_crossover, edge_recombination_crossover,
           sequential_constructive_crossover, order_based_crossover,
           position_based_crossover

3. "mutation_method" - Escolha DIFERENTE de: {current_mut_formatted}
   Opções: swap, inversion, scramble, insert, displacement,
           2-opt, 3-opt, reverse_sequence

⛔ PROIBIDO ALTERAR:
- "fitness_type" (Deve manter a abordagem atual: {params.get('fitness_type', 'UNKNOWN')})


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXEMPLO DE RESPOSTA VÁLIDA (mudando 3 algoritmos):
```json
{{
  "selection_method": "stochastic_universal_sampling",
  "crossover_method": "edge_recombination_crossover",
  "mutation_method": "2-opt",
  "mutation_rate": 0.15,
  "elite_size": 8
}}
```

EXEMPLO INVÁLIDO (não muda algoritmos - NÃO FAÇA ISSO):
```json
{{
  "population_size": 150,
  "mutation_rate": 0.12,
  "elite_size": 7
}}
```

🚀 AGORA SUGIRA OS PARÂMETROS (LEMBRE: MUDE OS ALGORITMOS!):"""

        return prompt


class ChatGPTAdapter(LLMAdapter):
    """Adapter para OpenAI ChatGPT"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"
    
    def list_models(self) -> List[str]:
        """Lista modelos disponíveis na OpenAI"""
        try:
            resp = requests.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                # Filtra apenas modelos de chat
                models = [m['id'] for m in data.get('data', []) 
                         if 'gpt' in m['id'].lower()]
                return sorted(models)
        except Exception as e:
            print(f"Erro ao listar modelos ChatGPT: {e}")
        return ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]  # Fallback
    
    def suggest_params(self, context: dict) -> dict:
        """Gera sugestão via ChatGPT"""
        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": self._build_prompt(context)}],
                    "max_tokens": 200,
                    "temperature": 0.7
                },
                timeout=30
            )
            if resp.status_code == 200:
                content = resp.json()['choices'][0]['message']['content']
                return parse_llm_response(content)
        except Exception as e:
            print(f"Erro ChatGPT: {e}")
        return {}


class OllamaAdapter(LLMAdapter):
    """Adapter para Ollama (local)"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url.rstrip('/')
        self.model = model
    
    def list_models(self) -> List[str]:
        """Lista modelos instalados no Ollama"""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return [m['name'] for m in data.get('models', [])]
        except Exception as e:
            print(f"Erro ao listar modelos Ollama: {e}")
        return []
    
    def suggest_params(self, context: dict) -> dict:
        """Gera sugestão via Ollama local"""
        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": self._build_prompt(context),
                    "stream": False
                },
                timeout=60
            )
            if resp.status_code == 200:
                content = resp.json().get('response', '')
                return parse_llm_response(content)
        except Exception as e:
            print(f"Erro Ollama: {e}")
        return {}


class OpenRouterAdapter(LLMAdapter):
    """Adapter para OpenRouter (múltiplos providers)"""
    
    def __init__(self, api_key: str, model: str = "openai/gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
    
    def list_models(self) -> List[str]:
        """Lista modelos disponíveis no OpenRouter"""
        try:
            resp = requests.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                return [m['id'] for m in data.get('data', [])][:50]  # Limita
        except Exception as e:
            print(f"Erro ao listar modelos OpenRouter: {e}")
        return ["openai/gpt-4o-mini", "anthropic/claude-3-haiku"]  # Fallback
    
    def suggest_params(self, context: dict) -> dict:
        """Gera sugestão via OpenRouter"""
        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": self._build_prompt(context)}],
                    "max_tokens": 200
                },
                timeout=30
            )
            if resp.status_code == 200:
                content = resp.json()['choices'][0]['message']['content']
                return parse_llm_response(content)
        except Exception as e:
            print(f"Erro OpenRouter: {e}")
        return {}


class LlamaCppAdapter(LLMAdapter):
    """Adapter para llama.cpp server (API compatível com OpenAI)"""
    
    def __init__(self, base_url: str = "http://localhost:8080", model: str = "default"):
        self.base_url = base_url.rstrip('/')
        self.model = model
    
    def list_models(self) -> List[str]:
        """Lista modelos disponíveis no llama.cpp server"""
        try:
            # llama.cpp server não tem endpoint de modelos, retorna o modelo carregado
            resp = requests.get(f"{self.base_url}/health", timeout=5)
            if resp.status_code == 200:
                return ["default (modelo carregado)"]
        except Exception as e:
            print(f"Erro ao conectar llama.cpp: {e}")
        return ["default"]
    
    def suggest_params(self, context: dict) -> dict:
        """Gera sugestão via llama.cpp server (API OpenAI-compatible)"""
        try:
            resp = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "messages": [{"role": "user", "content": self._build_prompt(context)}],
                    "max_tokens": 200,
                    "temperature": 0.7
                },
                timeout=60
            )
            if resp.status_code == 200:
                content = resp.json()['choices'][0]['message']['content']
                return parse_llm_response(content)
        except Exception as e:
            print(f"Erro llama.cpp: {e}")
        return {}


class ChatMockAdapter(LLMAdapter):
    """Adapter para ChatMock (API compatível com OpenAI para GPT-5/Codex)"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000", model: str = "gpt-5.1-codex-max"):
        self.base_url = base_url.rstrip('/')
        self.model = model
    
    def list_models(self) -> List[str]:
        """Lista modelos disponíveis no ChatMock"""
        # ChatMock expõe endpoint /api/tags (Ollama-compatible)
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return [m.get('name') or m.get('model') for m in data.get('models', [])]
        except:
            pass
        # Fallback: modelos padrão do ChatMock
        return [
            "gpt-5", "gpt-5.1", "gpt-5.2", 
            "gpt-5-codex", "gpt-5.1-codex", "gpt-5.2-codex",
            "gpt-5.1-codex-max", "gpt-5.1-codex-mini", "codex-mini"
        ]
    
    def suggest_params(self, context: dict) -> dict:
        """Gera sugestão via ChatMock (OpenAI-compatible)"""
        try:
            resp = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers={
                    "Authorization": "Bearer key",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": self._build_prompt(context)}],
                    "max_tokens": 300,
                    "temperature": 0.7
                },
                timeout=120
            )
            if resp.status_code == 200:
                content = resp.json()['choices'][0]['message']['content']
                return parse_llm_response(content)
        except Exception as e:
            print(f"Erro ChatMock: {e}")
        return {}


def get_adapter(provider: str, **kwargs) -> LLMAdapter:
    """Factory para criar adapter baseado no provider"""
    adapters = {
        "chatgpt": ChatGPTAdapter,
        "ollama": OllamaAdapter,
        "openrouter": OpenRouterAdapter,
        "llamacpp": LlamaCppAdapter,
        "chatmock": ChatMockAdapter
    }
    adapter_class = adapters.get(provider.lower())
    if not adapter_class:
        raise ValueError(f"Provider desconhecido: {provider}")
    return adapter_class(**kwargs)

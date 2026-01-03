"""
Testes para os adaptadores LLM (ChatGPT, Ollama, OpenRouter)
"""
import pytest
from unittest.mock import patch, MagicMock
import json


class TestChatGPTAdapter:
    """Testes para o adaptador ChatGPT"""
    
    def test_list_models_returns_list(self):
        """Deve retornar lista de modelos disponíveis"""
        from src.llm.adapters import ChatGPTAdapter
        
        adapter = ChatGPTAdapter(api_key="test_key")
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                "data": [
                    {"id": "gpt-4o-mini"},
                    {"id": "gpt-4o"},
                    {"id": "gpt-3.5-turbo"}
                ]
            }
            mock_get.return_value.status_code = 200
            
            models = adapter.list_models()
            
            assert isinstance(models, list)
            assert "gpt-4o-mini" in models
    
    def test_suggest_params_returns_valid_json(self):
        """Deve retornar parâmetros válidos em JSON"""
        from src.llm.adapters import ChatGPTAdapter
        
        adapter = ChatGPTAdapter(api_key="test_key", model="gpt-4o-mini")
        
        context = {
            "fitness": 6441.75,
            "params": {"population_size": 50, "mutation_rate": 0.1}
        }
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = {
                "choices": [{
                    "message": {
                        "content": '{"population_size": 100, "mutation_rate": 0.15}'
                    }
                }]
            }
            mock_post.return_value.status_code = 200
            
            result = adapter.suggest_params(context)
            
            assert isinstance(result, dict)
            assert "population_size" in result


class TestOllamaAdapter:
    """Testes para o adaptador Ollama (local)"""
    
    def test_list_models_local(self):
        """Deve listar modelos instalados no Ollama local"""
        from src.llm.adapters import OllamaAdapter
        
        adapter = OllamaAdapter(base_url="http://localhost:11434")
        
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                "models": [
                    {"name": "llama2"},
                    {"name": "mistral"},
                    {"name": "codellama"}
                ]
            }
            mock_get.return_value.status_code = 200
            
            models = adapter.list_models()
            
            assert isinstance(models, list)
            assert "llama2" in models
    
    def test_suggest_params_ollama(self):
        """Deve gerar sugestões via Ollama local"""
        from src.llm.adapters import OllamaAdapter
        
        adapter = OllamaAdapter(base_url="http://localhost:11434", model="llama2")
        
        context = {"fitness": 5000.0, "params": {}}
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = {
                "response": '{"population_size": 80}'
            }
            mock_post.return_value.status_code = 200
            
            result = adapter.suggest_params(context)
            
            assert isinstance(result, dict)


class TestOpenRouterAdapter:
    """Testes para o adaptador OpenRouter"""
    
    def test_list_models_openrouter(self):
        """Deve listar modelos do OpenRouter"""
        from src.llm.adapters import OpenRouterAdapter
        
        adapter = OpenRouterAdapter(api_key="test_key")
        
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                "data": [
                    {"id": "openai/gpt-4o"},
                    {"id": "anthropic/claude-3-sonnet"}
                ]
            }
            mock_get.return_value.status_code = 200
            
            models = adapter.list_models()
            
            assert isinstance(models, list)
            assert "openai/gpt-4o" in models


class TestLLMResponseParsing:
    """Testes para parsing de respostas do LLM"""
    
    def test_parse_json_from_response(self):
        """Deve extrair JSON válido da resposta do LLM"""
        from src.llm.adapters import parse_llm_response
        
        response = '''Aqui está minha sugestão:
        ```json
        {"population_size": 100, "mutation_rate": 0.2}
        ```
        '''
        
        result = parse_llm_response(response)
        
        assert result["population_size"] == 100
        assert result["mutation_rate"] == 0.2
    
    def test_parse_plain_json(self):
        """Deve funcionar com JSON puro"""
        from src.llm.adapters import parse_llm_response
        
        response = '{"crossover_rate": 0.8}'
        
        result = parse_llm_response(response)
        
        assert result["crossover_rate"] == 0.8
    
    def test_parse_invalid_json_returns_empty(self):
        """Deve retornar dict vazio se JSON inválido"""
        from src.llm.adapters import parse_llm_response
        
        response = "Texto sem JSON válido"
        
        result = parse_llm_response(response)
        
        assert result == {}

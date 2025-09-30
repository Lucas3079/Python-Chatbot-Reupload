"""Testes para a API."""
import pytest
import requests
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.api import app
from fastapi.testclient import TestClient

class TestAPI:
    """Testes para a API FastAPI."""
    
    @pytest.fixture
    def client(self):
        """Cliente de teste para a API."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_rag_system(self):
        """Mock do sistema RAG."""
        with patch('app.api.rag_system') as mock:
            yield mock
    
    @pytest.fixture
    def mock_llm_service(self):
        """Mock do serviço LLM."""
        with patch('app.api.llm_service') as mock:
            yield mock
    
    def test_root_endpoint(self, client):
        """Testa endpoint raiz."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Chatbot RAG - Folha de Pagamento"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
    
    def test_health_check(self, client):
        """Testa verificação de saúde."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "services" in data
    
    def test_chat_endpoint_payroll_query(self, client, mock_rag_system, mock_llm_service):
        """Testa endpoint de chat com consulta de folha."""
        # Mock da resposta do processador de consultas
        mock_evidence = [{
            "employee_id": "E001",
            "competency": "2025-05",
            "record_data": {
                "name": "Ana Souza",
                "net_pay": 8418.75
            },
            "source_line": 5
        }]
        
        with patch('app.api.query_processor') as mock_processor:
            mock_processor.process_query.return_value = (
                "O salário líquido de Ana Souza em 2025-05 foi R$ 8.418,75.",
                mock_evidence
            )
            
            # Mock do LLM
            mock_llm_service.is_payroll_query.return_value = True
            mock_llm_service.generate_response.return_value = "O salário líquido de Ana Souza em maio/2025 foi R$ 8.418,75. Fonte: E001, 2025-05"
            
            response = client.post(
                "/chat",
                json={
                    "message": "Quanto recebi em maio/2025? (Ana Souza)"
                }
            )
            
            assert response.status_code == 200
            
            data = response.json()
            assert "message" in data
            assert "timestamp" in data
            assert "sources" in data
            assert data["sources"] == ["E001, 2025-05"]
    
    def test_chat_endpoint_general_query(self, client, mock_llm_service):
        """Testa endpoint de chat com consulta geral."""
        # Mock do LLM
        mock_llm_service.is_payroll_query.return_value = False
        mock_llm_service.generate_response.return_value = "Olá! Como posso ajudá-lo hoje?"
        
        response = client.post(
            "/chat",
            json={
                "message": "Olá, como você está?"
            }
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert data["message"] == "Olá! Como posso ajudá-lo hoje?"
    
    def test_list_employees(self, client, mock_rag_system):
        """Testa listagem de funcionários."""
        # Mock do DataFrame
        mock_df = MagicMock()
        mock_df.__getitem__.return_value.unique.return_value.tolist.return_value = ["Ana Souza", "Bruno Lima"]
        mock_rag_system.df = mock_df
        
        response = client.get("/employees")
        assert response.status_code == 200
        
        data = response.json()
        assert "employees" in data
        assert "total" in data
        assert data["employees"] == ["Ana Souza", "Bruno Lima"]
        assert data["total"] == 2
    
    def test_get_employee_competencies(self, client, mock_rag_system):
        """Testa obtenção de competências de funcionário."""
        # Mock do sistema RAG
        mock_records = [
            MagicMock(competency="2025-01"),
            MagicMock(competency="2025-05")
        ]
        mock_rag_system.search_employee.return_value = mock_records
        
        response = client.get("/employee/Ana%20Souza/competencies")
        assert response.status_code == 200
        
        data = response.json()
        assert data["employee"] == "Ana Souza"
        assert "competencies" in data
    
    def test_get_employee_competencies_not_found(self, client, mock_rag_system):
        """Testa obtenção de competências para funcionário inexistente."""
        # Mock do sistema RAG
        mock_rag_system.search_employee.return_value = []
        
        response = client.get("/employee/João%20Silva/competencies")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "não encontrado" in data["detail"]
    
    def test_get_payroll_data(self, client, mock_rag_system):
        """Testa obtenção de dados de folha."""
        # Mock do sistema RAG
        mock_record = MagicMock()
        mock_record.dict.return_value = {
            "employee_id": "E001",
            "name": "Ana Souza",
            "competency": "2025-05",
            "net_pay": 8418.75
        }
        mock_rag_system.search_employee_competency.return_value = [mock_record]
        
        response = client.get("/payroll/Ana%20Souza/2025-05")
        assert response.status_code == 200
        
        data = response.json()
        assert data["employee"] == "Ana Souza"
        assert data["competency"] == "2025-05"
        assert "data" in data
    
    def test_chat_endpoint_error(self, client, mock_llm_service):
        """Testa endpoint de chat com erro."""
        # Mock do LLM para gerar erro
        mock_llm_service.is_payroll_query.side_effect = Exception("Erro de teste")
        
        response = client.post(
            "/chat",
            json={
                "message": "Teste de erro"
            }
        )
        
        assert response.status_code == 500
        
        data = response.json()
        assert "detail" in data
        assert "Erro interno" in data["detail"]


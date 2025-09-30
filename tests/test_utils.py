"""Testes para utilitários."""
import pytest
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.utils import (
    format_currency_br, 
    parse_date_br, 
    parse_competency,
    extract_employee_name_from_query,
    extract_competency_from_query
)

class TestUtils:
    """Testes para funções utilitárias."""
    
    def test_format_currency_br(self):
        """Testa formatação de moeda brasileira."""
        assert format_currency_br(8418.75) == "R$ 8.418,75"
        assert format_currency_br(1000.0) == "R$ 1.000,00"
        assert format_currency_br(0.0) == "R$ 0,00"
        assert format_currency_br(123456.78) == "R$ 123.456,78"
    
    def test_parse_date_br(self):
        """Testa conversão de data para formato brasileiro."""
        assert parse_date_br("2025-05-28") == "28/05/2025"
        assert parse_date_br("2025-01-01") == "01/01/2025"
        assert parse_date_br("2025-12-31") == "31/12/2025"
    
    def test_parse_competency(self):
        """Testa parsing de competência."""
        # Formato YYYY-MM
        assert parse_competency("2025-05") == "2025-05"
        assert parse_competency("2025-01") == "2025-01"
        
        # Formato YYYY/MM
        assert parse_competency("2025/05") == "2025-05"
        assert parse_competency("2025/01") == "2025-01"
        
        # Formato MM/YYYY
        assert parse_competency("05/2025") == "2025-05"
        assert parse_competency("01/2025") == "2025-01"
        
        # Formato mês/ano
        assert parse_competency("maio/2025") == "2025-05"
        assert parse_competency("mai/2025") == "2025-05"
        assert parse_competency("janeiro/2025") == "2025-01"
        assert parse_competency("jan/2025") == "2025-01"
        
        # Formato ano mês
        assert parse_competency("2025 maio") == "2025-05"
        assert parse_competency("2025 janeiro") == "2025-01"
        
        # Casos inválidos
        assert parse_competency("") is None
        assert parse_competency("invalido") is None
        assert parse_competency("13/2025") is None
    
    def test_extract_employee_name_from_query(self):
        """Testa extração de nome de funcionário da consulta."""
        # Nome entre parênteses
        assert extract_employee_name_from_query("Quanto recebi em maio? (Ana Souza)") == "Ana Souza"
        assert extract_employee_name_from_query("Salário do (Bruno Lima)") == "Bruno Lima"
        
        # Nome após "do"
        assert extract_employee_name_from_query("Salário do Ana Souza") == "Ana Souza"
        assert extract_employee_name_from_query("Bônus do Bruno Lima") == "Bruno Lima"
        
        # Nome após "da"
        assert extract_employee_name_from_query("Folha da Ana Souza") == "Ana Souza"
        
        # Nome após "funcionário"
        assert extract_employee_name_from_query("Dados do funcionário Ana Souza") == "Ana Souza"
        
        # Casos sem nome
        assert extract_employee_name_from_query("Quanto recebi?") is None
        assert extract_employee_name_from_query("Salário de maio") is None
    
    def test_extract_competency_from_query(self):
        """Testa extração de competência da consulta."""
        # Formato mês/ano
        assert extract_competency_from_query("Salário de maio/2025") == "maio/2025"
        assert extract_competency_from_query("Bônus de jan/2025") == "jan/2025"
        
        # Formato YYYY-MM
        assert extract_competency_from_query("Folha de 2025-05") == "2025-05"
        assert extract_competency_from_query("Pagamento 2025-01") == "2025-01"
        
        # Formato MM/YYYY
        assert extract_competency_from_query("Salário de 05/2025") == "05/2025"
        assert extract_competency_from_query("Bônus 01/2025") == "01/2025"
        
        # Formato YYYY/MM
        assert extract_competency_from_query("Folha de 2025/05") == "2025/05"
        
        # Formato ano mês
        assert extract_competency_from_query("Salário de 2025 maio") == "2025 maio"
        
        # Casos sem competência
        assert extract_competency_from_query("Quanto recebi?") is None
        assert extract_competency_from_query("Salário do Ana") is None


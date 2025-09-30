"""Testes para o sistema RAG."""
import pytest
import pandas as pd
import os
import sys
from unittest.mock import patch

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.rag_system import PayrollRAG
from app.models import PayrollRecord

class TestPayrollRAG:
    """Testes para a classe PayrollRAG."""
    
    @pytest.fixture
    def sample_data(self):
        """Dados de exemplo para testes."""
        return pd.DataFrame({
            'employee_id': ['E001', 'E001', 'E002', 'E002'],
            'name': ['Ana Souza', 'Ana Souza', 'Bruno Lima', 'Bruno Lima'],
            'competency': ['2025-01', '2025-05', '2025-01', '2025-06'],
            'base_salary': [8000, 8000, 6000, 6000],
            'bonus': [500, 1200, 500, 300],
            'benefits_vt_vr': [600, 650, 600, 650],
            'other_earnings': [0, 0, 0, 0],
            'deductions_inss': [880.0, 880.0, 660.0, 660.0],
            'deductions_irrf': [495.0, 551.25, 345.0, 333.75],
            'other_deductions': [0, 0, 0, 0],
            'net_pay': [7725.0, 8418.75, 6095.0, 5956.25],
            'payment_date': ['2025-01-28', '2025-05-28', '2025-01-28', '2025-06-28']
        })
    
    @pytest.fixture
    def rag_system(self, sample_data, tmp_path):
        """Sistema RAG para testes."""
        # Cria arquivo temporário com dados de exemplo
        csv_path = tmp_path / "test_payroll.csv"
        sample_data.to_csv(csv_path, index=False)
        
        return PayrollRAG(str(csv_path))
    
    def test_load_data(self, rag_system):
        """Testa carregamento de dados."""
        assert len(rag_system.df) == 4
        assert 'employee_id' in rag_system.df.columns
        assert 'name' in rag_system.df.columns
    
    def test_search_employee_exact(self, rag_system):
        """Testa busca exata de funcionário."""
        employees = rag_system.search_employee("Ana Souza")
        assert len(employees) == 2
        assert all(emp.name == "Ana Souza" for emp in employees)
    
    def test_search_employee_partial(self, rag_system):
        """Testa busca parcial de funcionário."""
        employees = rag_system.search_employee("Ana")
        assert len(employees) == 2
        assert all("Ana" in emp.name for emp in employees)
    
    def test_search_employee_not_found(self, rag_system):
        """Testa busca de funcionário inexistente."""
        employees = rag_system.search_employee("João Silva")
        assert len(employees) == 0
    
    def test_search_by_competency(self, rag_system):
        """Testa busca por competência."""
        records = rag_system.search_by_competency("2025-01")
        assert len(records) == 2
        assert all(emp.competency == "2025-01" for emp in records)
    
    def test_search_employee_competency(self, rag_system):
        """Testa busca de funcionário em competência específica."""
        records = rag_system.search_employee_competency("Ana Souza", "2025-05")
        assert len(records) == 1
        assert records[0].name == "Ana Souza"
        assert records[0].competency == "2025-05"
    
    def test_get_net_pay(self, rag_system):
        """Testa obtenção de salário líquido."""
        result = rag_system.get_net_pay("Ana Souza", "2025-05")
        assert result is not None
        
        net_pay, evidence = result
        assert net_pay == 8418.75
        assert evidence.employee_id == "E001"
        assert evidence.competency == "2025-05"
    
    def test_get_net_pay_not_found(self, rag_system):
        """Testa obtenção de salário líquido para funcionário inexistente."""
        result = rag_system.get_net_pay("João Silva", "2025-01")
        assert result is None
    
    def test_get_total_period(self, rag_system):
        """Testa cálculo de total de período."""
        result = rag_system.get_total_period("Ana Souza", "2025-01", "2025-05")
        assert result is not None
        
        total, evidence_list = result
        assert total == 7725.0 + 8418.75  # 2025-01 + 2025-05
        assert len(evidence_list) == 2
    
    def test_get_deduction(self, rag_system):
        """Testa obtenção de desconto."""
        result = rag_system.get_deduction("Bruno Lima", "2025-06", "inss")
        assert result is not None
        
        deduction, evidence = result
        assert deduction == 660.0
        assert evidence.employee_id == "E002"
    
    def test_get_payment_date(self, rag_system):
        """Testa obtenção de data de pagamento."""
        result = rag_system.get_payment_date("Ana Souza", "2025-05")
        assert result is not None
        
        payment_date, evidence = result
        assert "28/05/2025" in payment_date
        assert evidence.employee_id == "E001"
    
    def test_get_max_bonus(self, rag_system):
        """Testa obtenção de maior bônus."""
        result = rag_system.get_max_bonus("Ana Souza")
        assert result is not None
        
        max_bonus, competency, evidence = result
        assert max_bonus == 1200.0
        assert competency == "2025-05"
        assert evidence.employee_id == "E001"


"""Configuração de testes."""
import pytest
import os
import sys
from unittest.mock import patch

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture(autouse=True)
def mock_config():
    """Mock das configurações para testes."""
    with patch('app.config.Config') as mock_config:
        mock_config.OPENAI_API_KEY = "test_key"
        mock_config.OPENAI_MODEL = "gpt-3.5-turbo"
        mock_config.PAYROLL_DATA_PATH = os.path.join(os.path.dirname(__file__), "test_data.csv")
        mock_config.WEB_SEARCH_ENABLED = False
        mock_config.validate.return_value = None
        yield mock_config

@pytest.fixture
def sample_csv_data():
    """Dados CSV de exemplo para testes."""
    return """employee_id,name,competency,base_salary,bonus,benefits_vt_vr,other_earnings,deductions_inss,deductions_irrf,other_deductions,net_pay,payment_date
E001,Ana Souza,2025-01,8000,500,600,0,880.0,495.0,0,7725.0,2025-01-28
E001,Ana Souza,2025-05,8000,1200,650,0,880.0,551.25,0,8418.75,2025-05-28
E002,Bruno Lima,2025-01,6000,500,600,0,660.0,345.0,0,6095.0,2025-01-28
E002,Bruno Lima,2025-06,6000,300,650,0,660.0,333.75,0,5956.25,2025-06-28"""

@pytest.fixture
def temp_csv_file(tmp_path, sample_csv_data):
    """Arquivo CSV temporário para testes."""
    csv_file = tmp_path / "test_payroll.csv"
    csv_file.write_text(sample_csv_data)
    return str(csv_file)


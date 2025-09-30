"""Utilitários para formatação e parsing."""
import re
from datetime import datetime
from typing import Optional

def format_currency_br(value: float) -> str:
    """Formata valor monetário em reais brasileiros."""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def parse_date_br(date_str: str) -> str:
    """Converte data para formato brasileiro (dd/mm/aaaa)."""
    try:
        if isinstance(date_str, str):
            # Se já está no formato YYYY-MM-DD
            if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                return date_obj.strftime('%d/%m/%Y')
            # Se está no formato datetime
            elif 'T' in date_str:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return date_obj.strftime('%d/%m/%Y')
        return str(date_str)
    except:
        return str(date_str)

def parse_competency(competency: str) -> Optional[str]:
    """Parse competência em vários formatos para YYYY-MM."""
    if not competency:
        return None
    
    competency = competency.strip()
    
    # Mapeamento de meses
    month_map = {
        'jan': '01', 'janeiro': '01',
        'fev': '02', 'fevereiro': '02',
        'mar': '03', 'março': '03',
        'abr': '04', 'abril': '04',
        'mai': '05', 'maio': '05',
        'jun': '06', 'junho': '06',
        'jul': '07', 'julho': '07',
        'ago': '08', 'agosto': '08',
        'set': '09', 'setembro': '09',
        'out': '10', 'outubro': '10',
        'nov': '11', 'novembro': '11',
        'dez': '12', 'dezembro': '12'
    }
    
    # Formato YYYY-MM
    if re.match(r'^\d{4}-\d{2}$', competency):
        return competency
    
    # Formato YYYY/MM
    if re.match(r'^\d{4}/\d{2}$', competency):
        return competency.replace('/', '-')
    
    # Formato MM/YYYY
    if re.match(r'^\d{2}/\d{4}$', competency):
        parts = competency.split('/')
        return f"{parts[1]}-{parts[0]}"
    
    # Formato mês/ano (ex: maio/2025, mai/25)
    month_year_match = re.match(r'^(\w+)/(\d{2,4})$', competency.lower())
    if month_year_match:
        month_str, year_str = month_year_match.groups()
        if month_str in month_map:
            year = year_str if len(year_str) == 4 else f"20{year_str}"
            return f"{year}-{month_map[month_str]}"
    
    # Formato ano mês (ex: 2025 maio)
    year_month_match = re.match(r'^(\d{4})\s+(\w+)$', competency.lower())
    if year_month_match:
        year, month_str = year_month_match.groups()
        if month_str in month_map:
            return f"{year}-{month_map[month_str]}"
    
    return None

def extract_employee_name_from_query(query: str) -> Optional[str]:
    """Extrai nome do funcionário de uma consulta."""
    # Primeiro, tenta encontrar nomes conhecidos diretamente
    known_names = ['Ana Souza', 'Bruno Lima']
    query_lower = query.lower()
    for name in known_names:
        if name.lower() in query_lower:
            return name
    
    # Tenta encontrar apenas o primeiro nome se for conhecido
    first_names = ['ana', 'bruno']
    for first_name in first_names:
        if first_name in query_lower:
            if first_name == 'ana':
                return 'Ana Souza'
            elif first_name == 'bruno':
                return 'Bruno Lima'
    
    # Padrões comuns para extrair nomes (apenas se não encontrou acima)
    patterns = [
        r'\(([A-Z][a-z]+\s+[A-Z][a-z]+)\)',  # Nome completo entre parênteses
        r'do\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',  # "do Nome Sobrenome"
        r'da\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',  # "da Nome Sobrenome"
        r'funcionário\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',  # "funcionário Nome Sobrenome"
        r'([A-Z][a-z]+\s+[A-Z][a-z]+)',  # Nome Sobrenome (genérico)
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query)
        if match:
            name = match.group(1).strip()
            # Verifica se é um nome válido (não uma palavra como "líquido")
            if name.lower() in ['ana souza', 'bruno lima']:
                return name
    
    return None

def extract_competency_from_query(query: str) -> Optional[str]:
    """Extrai competência de uma consulta."""
    # Padrões para competência
    patterns = [
        r'(\w+/\d{2,4})',  # maio/2025, mai/25
        r'(\d{4}-\d{2})',  # 2025-05
        r'(\d{2}/\d{4})',  # 05/2025
        r'(\d{4}/\d{2})',  # 2025/05
        r'(\w+\s+\d{4})',  # maio 2025
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query)
        if match:
            return match.group(1).strip()
    
    return None

def clean_query(query: str) -> str:
    """Limpa e normaliza uma consulta."""
    # Remove caracteres especiais excessivos
    query = re.sub(r'[^\w\s\?\!\.\,\/\-\(\)]', ' ', query)
    # Remove espaços múltiplos
    query = re.sub(r'\s+', ' ', query)
    return query.strip()

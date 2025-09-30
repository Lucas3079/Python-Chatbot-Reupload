"""Processador de consultas para o chatbot."""
import re
from typing import Optional, Tuple, List
from app.models import Evidence, PayrollQuery
from app.rag_system import PayrollRAG
from app.utils import extract_employee_name_from_query, extract_competency_from_query, parse_competency

class QueryProcessor:
    """Processa e interpreta consultas do usuário."""
    
    def __init__(self, rag_system: PayrollRAG):
        """Inicializa o processador."""
        self.rag = rag_system
    
    def process_query(self, query: str) -> Tuple[Optional[str], Optional[List[Evidence]]]:
        """Processa uma consulta e retorna resposta com evidências."""
        
        # Identifica o tipo de consulta
        query_type = self._identify_query_type(query)
        
        if query_type == "net_pay":
            return self._process_net_pay_query(query)
        elif query_type == "total_period":
            return self._process_total_period_query(query)
        elif query_type == "deduction":
            return self._process_deduction_query(query)
        elif query_type == "payment_date":
            return self._process_payment_date_query(query)
        elif query_type == "max_bonus":
            return self._process_max_bonus_query(query)
        else:
            return None, None
    
    def _identify_query_type(self, query: str) -> str:
        """Identifica o tipo de consulta."""
        # Normaliza a string removendo caracteres especiais
        query_normalized = query.replace('\u00ad', '').replace('\u2011', '').replace('\u2013', '').replace('\u2014', '')
        query_lower = query_normalized.lower()
        
        # Salário líquido
        if any(word in query_lower for word in ['líquido', 'liquido', 'lquido', 'l\u00adquido', 'recebi', 'recebeu', 'quanto']):
            if any(word in query_lower for word in ['trimestre', 'período', 'periodo', 'total', '1º', 'primeiro']):
                return "total_period"
            return "net_pay"
        
        # Total líquido (caso específico)
        if 'total' in query_lower and ('líquido' in query_lower or 'liquido' in query_lower or 'lquido' in query_lower or 'l\u00adquido' in query_lower):
            if any(word in query_lower for word in ['trimestre', 'período', 'periodo', '1º', 'primeiro']):
                return "total_period"
        
        # Caso específico para "total líquido" com caracteres especiais
        if 'total' in query_lower and 'l' in query_lower and 'quido' in query_lower:
            if any(word in query_lower for word in ['trimestre', 'período', 'periodo', '1º', 'primeiro']):
                return "total_period"
        
        # Descontos
        if any(word in query_lower for word in ['inss', 'irrf', 'desconto']):
            return "deduction"
        
        # Data de pagamento
        if any(word in query_lower for word in ['quando', 'data', 'pago']):
            return "payment_date"
        
        # Maior bônus
        if any(word in query_lower for word in ['maior', 'máximo', 'maximo', 'bônus', 'bonus']):
            return "max_bonus"
        
        return "unknown"
    
    def _process_net_pay_query(self, query: str) -> Tuple[Optional[str], Optional[List[Evidence]]]:
        """Processa consulta de salário líquido."""
        employee_name = extract_employee_name_from_query(query)
        competency = extract_competency_from_query(query)
        
        if not employee_name or not competency:
            return "Preciso do nome do funcionário e da competência para consultar o salário líquido.", None
        
        result = self.rag.get_net_pay(employee_name, competency)
        if not result:
            return f"Não encontrei dados para {employee_name} na competência {competency}.", None
        
        net_pay, evidence = result
        from app.utils import format_currency_br
        
        response = f"O salário líquido de {employee_name} em {competency} foi {format_currency_br(net_pay)}."
        return response, [evidence]
    
    def _process_total_period_query(self, query: str) -> Tuple[Optional[str], Optional[List[Evidence]]]:
        """Processa consulta de total de período."""
        employee_name = extract_employee_name_from_query(query)
        
        if not employee_name:
            return "Preciso do nome do funcionário para calcular o total do período.", None
        
        # Extrai período da consulta
        period = self._extract_period_from_query(query)
        if not period:
            return "Preciso especificar o período (ex: 1º trimestre, janeiro a março, etc.).", None
        
        start_comp, end_comp = period
        result = self.rag.get_total_period(employee_name, start_comp, end_comp)
        
        if not result:
            return f"Não encontrei dados para {employee_name} no período especificado.", None
        
        total, evidence_list = result
        from app.utils import format_currency_br
        
        response = f"O total líquido de {employee_name} no período de {start_comp} a {end_comp} foi {format_currency_br(total)}."
        return response, evidence_list
    
    def _process_deduction_query(self, query: str) -> Tuple[Optional[str], Optional[List[Evidence]]]:
        """Processa consulta de desconto."""
        employee_name = extract_employee_name_from_query(query)
        competency = extract_competency_from_query(query)
        
        if not employee_name or not competency:
            return "Preciso do nome do funcionário e da competência para consultar os descontos.", None
        
        # Identifica tipo de desconto
        deduction_type = "inss"  # padrão
        if "irrf" in query.lower():
            deduction_type = "irrf"
        
        result = self.rag.get_deduction(employee_name, competency, deduction_type)
        if not result:
            return f"Não encontrei dados para {employee_name} na competência {competency}.", None
        
        deduction_value, evidence = result
        from app.utils import format_currency_br
        
        response = f"O desconto de {deduction_type.upper()} de {employee_name} em {competency} foi {format_currency_br(deduction_value)}."
        return response, [evidence]
    
    def _process_payment_date_query(self, query: str) -> Tuple[Optional[str], Optional[List[Evidence]]]:
        """Processa consulta de data de pagamento."""
        employee_name = extract_employee_name_from_query(query)
        competency = extract_competency_from_query(query)
        
        if not employee_name or not competency:
            return "Preciso do nome do funcionário e da competência para consultar a data de pagamento.", None
        
        result = self.rag.get_payment_date(employee_name, competency)
        if not result:
            return f"Não encontrei dados para {employee_name} na competência {competency}.", None
        
        payment_date, evidence = result
        net_pay = evidence.record_data['net_pay']
        from app.utils import format_currency_br
        
        response = f"O pagamento de {employee_name} em {competency} foi realizado em {payment_date} no valor de {format_currency_br(net_pay)}."
        return response, [evidence]
    
    def _process_max_bonus_query(self, query: str) -> Tuple[Optional[str], Optional[List[Evidence]]]:
        """Processa consulta de maior bônus."""
        employee_name = extract_employee_name_from_query(query)
        
        if not employee_name:
            return "Preciso do nome do funcionário para consultar o maior bônus.", None
        
        result = self.rag.get_max_bonus(employee_name)
        if not result:
            return f"Não encontrei dados para {employee_name}.", None
        
        max_bonus, competency, evidence = result
        from app.utils import format_currency_br
        
        response = f"O maior bônus de {employee_name} foi {format_currency_br(max_bonus)} em {competency}."
        return response, [evidence]
    
    def _extract_period_from_query(self, query: str) -> Optional[Tuple[str, str]]:
        """Extrai período da consulta."""
        # Normaliza a string removendo caracteres especiais
        query_normalized = query.replace('\u00ad', '').replace('\u2011', '').replace('\u2013', '').replace('\u2014', '')
        query_lower = query_normalized.lower()
        
        # 1º trimestre
        if "1º trimestre" in query_lower or "primeiro trimestre" in query_lower or "1 trimestre" in query_lower or "1" in query_lower and "trimestre" in query_lower:
            return ("2025-01", "2025-03")
        
        # 2º trimestre
        if "2º trimestre" in query_lower or "segundo trimestre" in query_lower:
            return ("2025-04", "2025-06")
        
        # Janeiro a março
        if "janeiro" in query_lower and "março" in query_lower:
            return ("2025-01", "2025-03")
        
        # Janeiro a março (com março)
        if "janeiro" in query_lower and "marco" in query_lower:
            return ("2025-01", "2025-03")
        
        return None


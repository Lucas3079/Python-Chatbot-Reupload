"""Sistema RAG para consulta de folha de pagamento."""
import pandas as pd
import re
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from app.models import PayrollRecord, Evidence, PayrollQuery
from app.utils import format_currency_br, parse_date_br, parse_competency

class PayrollRAG:
    """Sistema RAG para consultas de folha de pagamento."""
    
    def __init__(self, data_path: str):
        """Inicializa o sistema RAG."""
        self.data_path = data_path
        self.df = self._load_data()
        self._preprocess_data()
    
    def _load_data(self) -> pd.DataFrame:
        """Carrega os dados de folha de pagamento."""
        try:
            df = pd.read_csv(self.data_path)
            return df
        except Exception as e:
            raise Exception(f"Erro ao carregar dados: {e}")
    
    def _preprocess_data(self):
        """Pré-processa os dados para melhor busca."""
        # Converte datas para datetime
        self.df['payment_date'] = pd.to_datetime(self.df['payment_date'])
        
        # Cria coluna de competência formatada
        self.df['competency_formatted'] = self.df['competency'].apply(
            lambda x: f"{x[:4]}-{x[5:7]}"
        )
        
        # Normaliza nomes para busca
        self.df['name_normalized'] = self.df['name'].str.lower().str.strip()
        
        # Adiciona índice para referência
        self.df['source_line'] = self.df.index + 2  # +2 porque pandas indexa de 0 e CSV tem header
    
    def search_employee(self, name: str) -> List[PayrollRecord]:
        """Busca funcionário por nome (tolerante a variações)."""
        name_clean = re.sub(r'[^\w\s]', '', name.lower().strip())
        
        # Busca exata
        exact_matches = self.df[self.df['name_normalized'] == name_clean]
        if not exact_matches.empty:
            return self._df_to_records(exact_matches)
        
        # Busca parcial
        partial_matches = self.df[
            self.df['name_normalized'].str.contains(name_clean, case=False, na=False)
        ]
        if not partial_matches.empty:
            return self._df_to_records(partial_matches)
        
        # Busca por palavras-chave
        name_words = name_clean.split()
        for word in name_words:
            if len(word) > 2:  # Ignora palavras muito curtas
                word_matches = self.df[
                    self.df['name_normalized'].str.contains(word, case=False, na=False)
                ]
                if not word_matches.empty:
                    return self._df_to_records(word_matches)
        
        return []
    
    def search_by_competency(self, competency: str) -> List[PayrollRecord]:
        """Busca por competência (aceita vários formatos)."""
        parsed_comp = parse_competency(competency)
        if not parsed_comp:
            return []
        
        matches = self.df[self.df['competency'] == parsed_comp]
        return self._df_to_records(matches)
    
    def search_employee_competency(self, name: str, competency: str) -> List[PayrollRecord]:
        """Busca funcionário em competência específica."""
        employees = self.search_employee(name)
        if not employees:
            return []
        
        parsed_comp = parse_competency(competency)
        if not parsed_comp:
            return []
        
        # Filtra por competência
        filtered = [emp for emp in employees if emp.competency == parsed_comp]
        return filtered
    
    def get_net_pay(self, name: str, competency: str) -> Optional[Tuple[float, Evidence]]:
        """Obtém salário líquido de um funcionário em uma competência."""
        records = self.search_employee_competency(name, competency)
        if not records:
            return None
        
        record = records[0]
        evidence = Evidence(
            employee_id=record.employee_id,
            competency=record.competency,
            record_data=record.dict(),
            source_line=self._get_source_line(record.employee_id, record.competency)
        )
        
        return record.net_pay, evidence
    
    def get_total_period(self, name: str, start_comp: str, end_comp: str) -> Optional[Tuple[float, List[Evidence]]]:
        """Calcula total de um período para um funcionário."""
        employees = self.search_employee(name)
        if not employees:
            return None
        
        start_parsed = parse_competency(start_comp)
        end_parsed = parse_competency(end_comp)
        
        if not start_parsed or not end_parsed:
            return None
        
        # Filtra registros do período
        period_records = []
        for emp in employees:
            if start_parsed <= emp.competency <= end_parsed:
                period_records.append(emp)
        
        if not period_records:
            return None
        
        total = sum(emp.net_pay for emp in period_records)
        evidence_list = []
        
        for record in period_records:
            evidence = Evidence(
                employee_id=record.employee_id,
                competency=record.competency,
                record_data=record.dict(),
                source_line=self._get_source_line(record.employee_id, record.competency)
            )
            evidence_list.append(evidence)
        
        return total, evidence_list
    
    def get_deduction(self, name: str, competency: str, deduction_type: str) -> Optional[Tuple[float, Evidence]]:
        """Obtém desconto específico (INSS, IRRF, etc.)."""
        records = self.search_employee_competency(name, competency)
        if not records:
            return None
        
        record = records[0]
        deduction_value = getattr(record, f"deductions_{deduction_type.lower()}", 0)
        
        evidence = Evidence(
            employee_id=record.employee_id,
            competency=record.competency,
            record_data=record.dict(),
            source_line=self._get_source_line(record.employee_id, record.competency)
        )
        
        return deduction_value, evidence
    
    def get_payment_date(self, name: str, competency: str) -> Optional[Tuple[str, Evidence]]:
        """Obtém data de pagamento."""
        records = self.search_employee_competency(name, competency)
        if not records:
            return None
        
        record = records[0]
        payment_date = parse_date_br(record.payment_date)
        
        evidence = Evidence(
            employee_id=record.employee_id,
            competency=record.competency,
            record_data=record.dict(),
            source_line=self._get_source_line(record.employee_id, record.competency)
        )
        
        return payment_date, evidence
    
    def get_max_bonus(self, name: str) -> Optional[Tuple[float, str, Evidence]]:
        """Obtém maior bônus de um funcionário."""
        employees = self.search_employee(name)
        if not employees:
            return None
        
        max_bonus = 0
        max_record = None
        
        for emp in employees:
            if emp.bonus > max_bonus:
                max_bonus = emp.bonus
                max_record = emp
        
        if not max_record:
            return None
        
        evidence = Evidence(
            employee_id=max_record.employee_id,
            competency=max_record.competency,
            record_data=max_record.dict(),
            source_line=self._get_source_line(max_record.employee_id, max_record.competency)
        )
        
        return max_bonus, max_record.competency, evidence
    
    def _df_to_records(self, df: pd.DataFrame) -> List[PayrollRecord]:
        """Converte DataFrame para lista de PayrollRecord."""
        records = []
        for _, row in df.iterrows():
            record = PayrollRecord(
                employee_id=row['employee_id'],
                name=row['name'],
                competency=row['competency'],
                base_salary=float(row['base_salary']),
                bonus=float(row['bonus']),
                benefits_vt_vr=float(row['benefits_vt_vr']),
                other_earnings=float(row['other_earnings']),
                deductions_inss=float(row['deductions_inss']),
                deductions_irrf=float(row['deductions_irrf']),
                other_deductions=float(row['other_deductions']),
                net_pay=float(row['net_pay']),
                payment_date=str(row['payment_date'])
            )
            records.append(record)
        return records
    
    def _get_source_line(self, employee_id: str, competency: str) -> int:
        """Obtém número da linha fonte no CSV."""
        mask = (self.df['employee_id'] == employee_id) & (self.df['competency'] == competency)
        matches = self.df[mask]
        if not matches.empty:
            return int(matches.iloc[0]['source_line'])
        return 0


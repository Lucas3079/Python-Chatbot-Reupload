"""Modelos de dados para o chatbot."""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class PayrollRecord(BaseModel):
    """Registro de folha de pagamento."""
    employee_id: str
    name: str
    competency: str
    base_salary: float
    bonus: float
    benefits_vt_vr: float
    other_earnings: float
    deductions_inss: float
    deductions_irrf: float
    other_deductions: float
    net_pay: float
    payment_date: str

class Evidence(BaseModel):
    """Evidência de uma consulta RAG."""
    employee_id: str
    competency: str
    record_data: Dict[str, Any]
    source_line: int

class ChatMessage(BaseModel):
    """Mensagem do chat."""
    role: str  # "user" ou "assistant"
    content: str
    timestamp: Optional[datetime] = None
    evidence: Optional[List[Evidence]] = None

class ChatRequest(BaseModel):
    """Requisição de chat."""
    message: str
    conversation_history: Optional[List[ChatMessage]] = None

class ChatResponse(BaseModel):
    """Resposta do chat."""
    message: str
    evidence: Optional[List[Evidence]] = None
    sources: Optional[List[str]] = None
    timestamp: datetime

class PayrollQuery(BaseModel):
    """Consulta específica de folha de pagamento."""
    employee_name: Optional[str] = None
    employee_id: Optional[str] = None
    competency: Optional[str] = None
    query_type: str  # "net_pay", "bonus", "inss", "irrf", "payment_date", "total_period"
    period_start: Optional[str] = None
    period_end: Optional[str] = None


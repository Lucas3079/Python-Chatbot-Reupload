"""Serviço de integração com LLM."""
import openai
import requests
from typing import List, Optional, Dict, Any
from app.config import Config
from app.models import ChatMessage, Evidence
from app.utils import format_currency_br, parse_date_br

class LLMService:
    """Serviço para integração com LLM."""
    
    def __init__(self):
        """Inicializa o serviço LLM."""
        if Config.OPENAI_API_KEY and Config.OPENAI_API_KEY != "your_openai_api_key_here":
            self.openai_client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        else:
            self.openai_client = None
        self.model = Config.OPENAI_MODEL
        self.groq_api_key = Config.GROQ_API_KEY
    
    def generate_response(
        self, 
        user_message: str, 
        conversation_history: Optional[List[ChatMessage]] = None,
        evidence: Optional[List[Evidence]] = None
    ) -> str:
        """Gera resposta do LLM."""
        
        # Modo demo se não houver chaves
        if (not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == "your_openai_api_key_here" or
            Config.OPENAI_API_KEY == "demo_mode") and not Config.GROQ_API_KEY:
            return self._demo_response(user_message, evidence)
        
        # Tenta Groq primeiro (gratuito e rápido)
        if Config.GROQ_API_KEY and Config.GROQ_API_KEY != "your_groq_api_key_here":
            try:
                return self._groq_response(user_message, conversation_history, evidence)
            except Exception as e:
                print(f"Erro no Groq: {e}")
                # Se Groq falhar, tenta OpenAI ou vai para demo
                if Config.OPENAI_API_KEY and Config.OPENAI_API_KEY != "your_openai_api_key_here":
                    try:
                        return self._openai_response(user_message, conversation_history, evidence)
                    except Exception as e2:
                        print(f"Erro no OpenAI: {e2}")
                        return self._demo_response(user_message, evidence)
                else:
                    return self._demo_response(user_message, evidence)
        
        # Fallback para OpenAI
        if Config.OPENAI_API_KEY and Config.OPENAI_API_KEY != "your_openai_api_key_here":
            try:
                return self._openai_response(user_message, conversation_history, evidence)
            except Exception as e:
                if "quota" in str(e).lower() or "429" in str(e):
                    return self._demo_response(user_message, evidence)
                return f"Desculpe, ocorreu um erro ao processar sua mensagem: {str(e)}"
        
        return self._demo_response(user_message, evidence)
    
    def _groq_response(self, user_message: str, conversation_history: Optional[List[ChatMessage]] = None, evidence: Optional[List[Evidence]] = None) -> str:
        """Resposta usando Groq API."""
        messages = self._build_conversation_context(user_message, conversation_history, evidence)
        
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": messages,
            "model": "llama-3.1-8b-instant",  # Modelo atual do Groq
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def _openai_response(self, user_message: str, conversation_history: Optional[List[ChatMessage]] = None, evidence: Optional[List[Evidence]] = None) -> str:
        """Resposta usando OpenAI API."""
        if not self.openai_client:
            raise Exception("Cliente OpenAI não inicializado")
        
        messages = self._build_conversation_context(user_message, conversation_history, evidence)
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    def _build_conversation_context(
        self, 
        user_message: str, 
        conversation_history: Optional[List[ChatMessage]] = None,
        evidence: Optional[List[Evidence]] = None
    ) -> List[Dict[str, str]]:
        """Constrói o contexto da conversa para o LLM."""
        
        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt()
            }
        ]
        
        # Adiciona histórico da conversa
        if conversation_history:
            for msg in conversation_history[-5:]:  # Últimas 5 mensagens
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Adiciona evidências se disponíveis
        if evidence:
            evidence_text = self._format_evidence(evidence)
            user_message = f"{user_message}\n\nDados relevantes:\n{evidence_text}"
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    def _get_system_prompt(self) -> str:
        """Retorna o prompt do sistema."""
        return """Você é a CapBot, uma inteligência artificial da Capgemini criada para fazer análises financeiras. Suas responsabilidades incluem:

1. **Identidade**: Você é a CapBot, uma IA especializada em análises financeiras da Capgemini.
2. **Consultas de Folha de Pagamento**: Responder perguntas sobre salários, descontos, bônus, datas de pagamento, etc.
3. **Formatação Brasileira**: Sempre formate valores monetários em reais (R$ X.XXX,XX) e datas no formato brasileiro (dd/mm/aaaa).
4. **Citação de Fontes**: Sempre cite as fontes dos dados quando disponíveis (ex: "Fonte: E001, 2025-05").
5. **Conversa Geral**: Também pode conversar sobre outros tópicos de forma natural e útil.

**REGRA FUNDAMENTAL:**
- **SEMPRE use os dados fornecidos para responder**
- **NUNCA diga que não tem acesso ou não conhece funcionários se os dados foram fornecidos**
- **SEMPRE responda com base nos dados fornecidos quando disponíveis**

**Regras importantes:**
- Sempre se apresente como CapBot da Capgemini
- Use sempre formatação brasileira para moeda e datas
- Cite as fontes dos dados quando disponíveis
- Seja preciso com os valores e datas
- Mantenha um tom profissional mas amigável
- Para consultas de folha, use os dados fornecidos para responder

**Exemplos de formatação:**
- Valores: R$ 8.418,75
- Datas: 28/05/2025
- Fontes: Fonte: E001, 2025-05"""
    
    def _format_evidence(self, evidence: List[Evidence]) -> str:
        """Formata evidências para o LLM."""
        if not evidence:
            return ""
        
        formatted_evidence = []
        for ev in evidence:
            record = ev.record_data
            formatted_evidence.append(
                f"Funcionário: {record['name']} (ID: {ev.employee_id})\n"
                f"Competência: {ev.competency}\n"
                f"Salário Base: {format_currency_br(record['base_salary'])}\n"
                f"Bônus: {format_currency_br(record['bonus'])}\n"
                f"Desconto INSS: {format_currency_br(record['deductions_inss'])}\n"
                f"Desconto IRRF: {format_currency_br(record['deductions_irrf'])}\n"
                f"Salário Líquido: {format_currency_br(record['net_pay'])}\n"
                f"Data de Pagamento: {parse_date_br(record['payment_date'])}\n"
                f"Fonte: {ev.employee_id}, {ev.competency}"
            )
        
        return "\n\n".join(formatted_evidence)
    
    def _demo_response(self, user_message: str, evidence: Optional[List[Evidence]] = None) -> str:
        """Resposta demo quando não há chave da OpenAI ou quota esgotada."""
        message_lower = user_message.lower()
        
        # Respostas para consultas de folha
        if evidence:
            if "líquido" in message_lower or "liquido" in message_lower:
                return f"Com base nos dados encontrados, o salário líquido foi processado. {self._format_evidence(evidence)}"
            elif "inss" in message_lower:
                return f"O desconto de INSS foi calculado conforme os dados. {self._format_evidence(evidence)}"
            elif "bônus" in message_lower or "bonus" in message_lower:
                return f"O bônus foi processado conforme os registros. {self._format_evidence(evidence)}"
            else:
                return f"Consulta processada com sucesso. {self._format_evidence(evidence)}"
        
        # Respostas gerais
        if "olá" in message_lower or "oi" in message_lower:
            return "Olá! Sou o assistente de folha de pagamento. Como posso ajudá-lo hoje? (Modo Demo - sem OpenAI)"
        elif "como você está" in message_lower:
            return "Estou funcionando perfeitamente! Estou aqui para ajudar com consultas de folha de pagamento. (Modo Demo)"
        elif "selic" in message_lower:
            return "A taxa Selic atual é de aproximadamente 10,50% ao ano. (Modo Demo - dados simulados)"
        else:
            return f"Recebi sua mensagem: '{user_message}'. Estou funcionando em modo demo. Para funcionalidade completa, configure uma chave válida da OpenAI. (Modo Demo)"
    
    def is_payroll_query(self, message: str) -> bool:
        """Verifica se a mensagem é uma consulta de folha de pagamento."""
        payroll_keywords = [
            'salário', 'salario', 'pagamento', 'líquido', 'liquido',
            'bônus', 'bonus', 'inss', 'irrf', 'desconto', 'descontos',
            'folha', 'competência', 'competencia', 'recebi', 'recebeu',
            'quanto', 'valor', 'data', 'quando', 'funcionário', 'funcionario',
            'maior', 'máximo', 'maximo', 'total', 'trimestre', 'período', 'periodo'
        ]
        
        # Normaliza a string removendo caracteres especiais
        message_normalized = message.replace('\u00ad', '').replace('\u2011', '').replace('\u2013', '').replace('\u2014', '')
        message_lower = message_normalized.lower()
        return any(keyword in message_lower for keyword in payroll_keywords)

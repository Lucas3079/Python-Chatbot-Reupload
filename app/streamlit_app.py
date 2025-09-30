"""Interface Streamlit para o chatbot."""
import streamlit as st
import requests
import json
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="CapBot - Análise Financeira",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    .user-message {
        background-color: #1976d2;
        border-left-color: #0d47a1;
        color: white;
        font-weight: 500;
    }
    .assistant-message {
        background-color: #e8f5e8;
        border-left-color: #4caf50;
        color: #2e7d32;
    }
    .evidence-box {
        background-color: #fff3e0;
        border: 1px solid #ff9800;
        border-radius: 5px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .source-link {
        color: #1976d2;
        text-decoration: none;
        font-weight: bold;
    }
    .capbot-header {
        background: linear-gradient(90deg, #1976d2, #42a5f5);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
    }
    .capbot-title {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .capbot-description {
        font-size: 0.9rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# Configuração da API
API_BASE_URL = "http://localhost:8000"

def initialize_session_state():
    """Inicializa o estado da sessão."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

def send_message(message: str) -> Dict[str, Any]:
    """Envia mensagem para a API."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "message": message,
                "conversation_history": st.session_state.conversation_history
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar com a API: {e}")
        return None

def format_evidence(evidence: List[Dict[str, Any]]) -> str:
    """Formata evidências para exibição."""
    if not evidence:
        return ""
    
    formatted = "**📊 Evidências:**\n\n"
    for i, ev in enumerate(evidence, 1):
        record = ev.get("record_data", {})
        formatted += f"**{i}. Funcionário:** {record.get('name', 'N/A')} (ID: {ev.get('employee_id', 'N/A')})\n"
        formatted += f"   **Competência:** {ev.get('competency', 'N/A')}\n"
        formatted += f"   **Salário Líquido:** R$ {record.get('net_pay', 0):,.2f}\n"
        formatted += f"   **Fonte:** Linha {ev.get('source_line', 'N/A')} do dataset\n\n"
    
    return formatted

def display_message(role: str, content: str, evidence: List[Dict[str, Any]] = None, sources: List[str] = None):
    """Exibe uma mensagem no chat."""
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 Você:</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>🤖 Assistente:</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
        
        # Exibe evidências se disponíveis
        if evidence:
            st.markdown(format_evidence(evidence))
        
        # Exibe fontes se disponíveis
        if sources:
            st.markdown("**🔗 Fontes:**")
            for source in sources:
                st.markdown(f"- {source}")

def main():
    """Função principal da aplicação."""
    initialize_session_state()
    
    # Cabeçalho
    st.markdown('<h1 class="main-header">💰 Chatbot RAG - Folha de Pagamento</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Informações")
        
        # Status da API
        try:
            health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if health_response.status_code == 200:
                st.success("✅ API Conectada")
            else:
                st.error("❌ API com problemas")
        except:
            st.error("❌ API Desconectada")
        
        st.markdown("---")
        
        # Lista de funcionários
        st.subheader("👥 Funcionários Disponíveis")
        try:
            employees_response = requests.get(f"{API_BASE_URL}/employees", timeout=5)
            if employees_response.status_code == 200:
                employees_data = employees_response.json()
                for employee in employees_data.get("employees", []):
                    st.write(f"• {employee}")
            else:
                st.write("Não foi possível carregar a lista de funcionários")
        except:
            st.write("Erro ao conectar com a API")
        
        st.markdown("---")
        
        # Exemplos de consultas
        st.subheader("💡 Exemplos de Consultas")
        example_queries = [
            "Quanto recebi em maio/2025? (Ana Souza)",
            "Qual o total líquido de Ana Souza no 1º trimestre de 2025?",
            "Qual foi o desconto de INSS do Bruno em jun/2025?",
            "Quando foi pago o salário de abril/2025 do Bruno?",
            "Qual foi o maior bônus do Bruno?",
            "Traga a taxa Selic atual"
        ]
        
        for query in example_queries:
            if st.button(f"📝 {query}", key=f"example_{hash(query)}"):
                # Define a query de exemplo
                st.session_state.example_query = query
                st.rerun()
        
        st.markdown("---")
        
        # Botão para limpar chat
        if st.button("🗑️ Limpar Chat"):
            st.session_state.messages = []
            st.session_state.conversation_history = []
            st.rerun()
    
    # Header do CapBot
    st.markdown("""
    <div class="capbot-header">
        <div class="capbot-title">🤖 CapBot</div>
        <div class="capbot-description">Eu sou a CapBot, uma inteligência artificial da Capgemini criada para fazer análises financeiras</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Área principal do chat
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("💬 Chat")
        
        # Exibe histórico de mensagens
        for message in st.session_state.messages:
            display_message(
                message["role"],
                message["content"],
                message.get("evidence"),
                message.get("sources")
            )
        
        # Inicializa variável para query de exemplo
        if "example_query" not in st.session_state:
            st.session_state.example_query = None
        
        # Processa query de exemplo se houver
        if st.session_state.example_query:
            query = st.session_state.example_query
            st.session_state.example_query = None  # Limpa a query
            
            # Adiciona mensagem do usuário
            st.session_state.messages.append({
                "role": "user",
                "content": query,
                "timestamp": datetime.now()
            })
            
            st.session_state.conversation_history.append({
                "role": "user",
                "content": query,
                "timestamp": datetime.now().isoformat()
            })
            
            # Envia para a API
            with st.spinner("Processando..."):
                response = send_message(query)
            
            if response:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["message"],
                    "evidence": response.get("evidence"),
                    "sources": response.get("sources"),
                    "timestamp": datetime.now()
                })
                
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": response["message"],
                    "timestamp": response["timestamp"]
                })
            
            st.rerun()
        
        # Input do usuário
        input_key = f"user_input_{st.session_state.get('input_counter', 0)}"
        user_input = st.text_input(
            "Digite sua mensagem:",
            value="",
            key=input_key,
            placeholder="Ex: Quanto recebi em maio/2025? (Ana Souza)"
        )
        
        # Botão de envio
        if st.button("Enviar", type="primary"):
            if user_input:
                # Adiciona mensagem do usuário
                st.session_state.messages.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now()
                })
                
                # Adiciona ao histórico da conversa
                st.session_state.conversation_history.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Envia para a API
                with st.spinner("Processando..."):
                    response = send_message(user_input)
                
                if response:
                    # Adiciona resposta do assistente
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["message"],
                        "evidence": response.get("evidence"),
                        "sources": response.get("sources"),
                        "timestamp": datetime.now()
                    })
                    
                    # Adiciona ao histórico da conversa
                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": response["message"],
                        "timestamp": response["timestamp"]
                    })
                
                # Limpa o input usando uma chave dinâmica
                st.session_state.input_counter = st.session_state.get("input_counter", 0) + 1
                st.rerun()
    
    with col2:
        st.subheader("📊 Estatísticas")
        
        # Estatísticas do chat
        total_messages = len(st.session_state.messages)
        user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
        assistant_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
        
        st.metric("Total de Mensagens", total_messages)
        st.metric("Suas Mensagens", user_messages)
        st.metric("Respostas do Assistente", assistant_messages)
        
        # Botão para limpar conversa
        st.markdown("---")
        if st.button("🗑️ Limpar Conversa", type="secondary"):
            st.session_state.messages = []
            st.session_state.conversation_history = []
        
        # Download do histórico
        if st.session_state.messages:
            st.markdown("---")
            st.subheader("💾 Exportar")
            
            # Converte para JSON (serializa datetime)
            def serialize_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")
            
            chat_data = {
                "timestamp": datetime.now().isoformat(),
                "messages": st.session_state.messages,
                "conversation_history": st.session_state.conversation_history
            }
            
            json_data = json.dumps(chat_data, indent=2, ensure_ascii=False, default=serialize_datetime)
            
            st.download_button(
                label="📥 Baixar Histórico (JSON)",
                data=json_data,
                file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()

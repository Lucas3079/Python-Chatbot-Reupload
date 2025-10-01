"""API FastAPI para o chatbot."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Optional
import logging
from datetime import datetime
import os

from app.config import Config
from app.models import ChatRequest, ChatResponse, ChatMessage, Evidence
from app.rag_system import PayrollRAG
from app.llm_service import LLMService
from app.query_processor import QueryProcessor
from app.web_search import WebSearchService

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicialização da aplicação
app = FastAPI(
    title="Chatbot RAG - Folha de Pagamento",
    description="Chatbot com RAG para consultas de folha de pagamento",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialização dos serviços
try:
    Config.validate()
    rag_system = PayrollRAG(Config.PAYROLL_DATA_PATH)
    llm_service = LLMService()
    query_processor = QueryProcessor(rag_system)
    web_search_service = WebSearchService() if Config.WEB_SEARCH_ENABLED else None
    
    logger.info("Serviços inicializados com sucesso")
except Exception as e:
    logger.error(f"Erro na inicialização: {e}")
    raise

# Servir arquivos estáticos do frontend
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
    
    # Servir arquivos específicos do frontend
    @app.get("/{file_path:path}")
    async def serve_frontend(file_path: str):
        """Serve arquivos do frontend."""
        if file_path in ["style.css", "script.js", "capgemini-logo.png.png", "capgemini-icon.png.png"]:
            file_location = f"frontend/{file_path}"
            if os.path.exists(file_location):
                return FileResponse(file_location)
        return FileResponse("frontend/index.html")

@app.get("/")
async def root():
    """Endpoint raiz - serve o frontend."""
    try:
        if os.path.exists("frontend/index.html"):
            return FileResponse("frontend/index.html")
    except Exception as e:
        logger.warning(f"Erro ao servir frontend: {e}")
    
    return {
        "message": "CapBot - Chatbot de Análise Financeira",
        "version": "1.0.0",
        "status": "running",
        "health": "ok"
    }

@app.get("/health")
async def health_check():
    """Verificação de saúde da API."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "rag_system": "active",
            "llm_service": "active",
            "web_search": "active" if web_search_service else "disabled"
        }
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Endpoint principal do chat."""
    try:
        logger.info(f"Processando mensagem: {request.message[:100]}...")
        
        # Verifica se é uma consulta de folha de pagamento
        if llm_service.is_payroll_query(request.message):
            # Processa consulta RAG
            rag_response, evidence = query_processor.process_query(request.message)
            
            if rag_response:
                # Usa LLM para formatar a resposta com evidências
                formatted_response = llm_service.generate_response(
                    user_message=request.message,
                    conversation_history=request.conversation_history,
                    evidence=evidence
                )
                
                # Extrai fontes das evidências
                sources = []
                if evidence:
                    sources = [f"{ev.employee_id}, {ev.competency}" for ev in evidence]
                
                return ChatResponse(
                    message=formatted_response,
                    evidence=evidence,
                    sources=sources,
                    timestamp=datetime.now()
                )
        
        # Busca na web se habilitada e se a consulta parece ser sobre informações externas
        logger.info(f"Verificando busca na web - web_search_service: {web_search_service is not None}, is_web_query: {_is_web_search_query(request.message)}")
        if web_search_service and _is_web_search_query(request.message):
            logger.info(f"Tentando busca na web para: {request.message[:50]}...")
            web_results = web_search_service.search(request.message)
            logger.info(f"Resultado da busca web: {web_results}")
            if web_results:
                logger.info(f"Resultado da busca web encontrado: {web_results.get('source', 'N/A')}")
                web_response = llm_service.generate_response(
                    user_message=f"{request.message}\n\nInformações encontradas na web:\n{web_results}",
                    conversation_history=request.conversation_history
                )
                
                return ChatResponse(
                    message=web_response,
                    sources=[web_results.get("source", "Web Search")],
                    timestamp=datetime.now()
                )
            else:
                logger.info("Nenhum resultado encontrado na busca web")
        else:
            logger.info("Busca na web não executada - condições não atendidas")
        
        # Chat geral com LLM
        response = llm_service.generate_response(
            user_message=request.message,
            conversation_history=request.conversation_history
        )
        
        return ChatResponse(
            message=response,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Erro no chat: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/employees")
async def list_employees():
    """Lista todos os funcionários disponíveis."""
    try:
        employees = rag_system.df['name'].unique().tolist()
        return {
            "employees": employees,
            "total": len(employees)
        }
    except Exception as e:
        logger.error(f"Erro ao listar funcionários: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/employee/{employee_name}/competencies")
async def get_employee_competencies(employee_name: str):
    """Lista competências disponíveis para um funcionário."""
    try:
        records = rag_system.search_employee(employee_name)
        if not records:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")
        
        competencies = list(set([record.competency for record in records]))
        competencies.sort()
        
        return {
            "employee": employee_name,
            "competencies": competencies
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar competências: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/payroll/{employee_name}/{competency}")
async def get_payroll_data(employee_name: str, competency: str):
    """Obtém dados de folha de pagamento específicos."""
    try:
        records = rag_system.search_employee_competency(employee_name, competency)
        if not records:
            raise HTTPException(status_code=404, detail="Dados não encontrados")
        
        record = records[0]
        return {
            "employee": employee_name,
            "competency": competency,
            "data": record.dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar dados de folha: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

def _is_web_search_query(message: str) -> bool:
    """Verifica se a mensagem parece ser uma consulta para busca na web."""
    web_keywords = [
        'taxa selic', 'selic', 'inflação', 'inflacao', 'ibovespa', 'dólar', 'dolar',
        'euro', 'bitcoin', 'crypto', 'economia', 'mercado', 'bolsa', 'notícias',
        'noticias', 'atual', 'hoje', 'agora', 'tempo', 'clima', 'temperatura',
        'fórmula 1', 'formula 1', 'f1', 'gp', 'grand prix', 'corrida', 'piloto',
        'azerbaijan', 'baku', 'vencedor', 'venceu', 'resultado', 'classificação'
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in web_keywords)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.APP_HOST, port=Config.APP_PORT)


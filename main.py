"""Arquivo principal para executar a aplicação."""
import os
import uvicorn
from app.config import Config
from app.api import app

if __name__ == "__main__":
    try:
        Config.validate()
        
        # Configurações para produção
        port = int(os.environ.get("PORT", Config.APP_PORT))
        host = "0.0.0.0" if os.environ.get("RAILWAY_ENVIRONMENT") else Config.APP_HOST
        debug = not os.environ.get("RAILWAY_ENVIRONMENT")
        
        print(f"Iniciando servidor na porta {port}")
        print(f"Dados de folha: {Config.PAYROLL_DATA_PATH}")
        print(f"Modelo LLM: {Config.OPENAI_MODEL}")
        print(f"Acesso: http://{host}:{port}")
        
        uvicorn.run(
            "app.api:app",
            host=host,
            port=port,
            reload=debug
        )
    except Exception as e:
        print(f"Erro ao iniciar aplicacao: {e}")
        exit(1)

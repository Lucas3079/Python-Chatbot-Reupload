"""Configurações da aplicação."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configurações da aplicação."""
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Alternative LLM Providers
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # Application
    APP_HOST = os.getenv("APP_HOST", "localhost")
    APP_PORT = int(os.getenv("APP_PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Data
    PAYROLL_DATA_PATH = os.getenv("PAYROLL_DATA_PATH", "./data/payroll.csv")
    
    # Web Search
    WEB_SEARCH_ENABLED = os.getenv("WEB_SEARCH_ENABLED", "True").lower() == "true"
    SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
    
    # Production settings
    ENVIRONMENT = os.getenv("RAILWAY_ENVIRONMENT", "development")
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    @classmethod
    def validate(cls):
        """Valida se as configurações obrigatórias estão presentes."""
        # Verifica se pelo menos uma chave de LLM está configurada
        has_openai = cls.OPENAI_API_KEY and cls.OPENAI_API_KEY != "your_openai_api_key_here"
        has_groq = cls.GROQ_API_KEY and cls.GROQ_API_KEY != "your_groq_api_key_here"
        has_anthropic = cls.ANTHROPIC_API_KEY and cls.ANTHROPIC_API_KEY != "your_anthropic_api_key_here"

        if not (has_openai or has_groq or has_anthropic):
            raise ValueError("Pelo menos uma chave de LLM é obrigatória (OPENAI_API_KEY, GROQ_API_KEY ou ANTHROPIC_API_KEY)")

        if not os.path.exists(cls.PAYROLL_DATA_PATH):
            raise FileNotFoundError(f"Arquivo de dados não encontrado: {cls.PAYROLL_DATA_PATH}")


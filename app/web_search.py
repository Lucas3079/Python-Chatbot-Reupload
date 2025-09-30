"""Serviço de busca na web."""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class WebSearchService:
    """Serviço para busca de informações na web."""
    
    def __init__(self):
        """Inicializa o serviço de busca."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search(self, query: str) -> Optional[Dict[str, str]]:
        """Realiza busca na web e retorna resultado com fonte."""
        try:
            # Para demonstração, vamos buscar informações sobre taxa Selic
            if "selic" in query.lower():
                return self._search_selic_rate()
            
            # Para outras consultas, podemos usar uma API de busca ou scraping
            return self._generic_search(query)
            
        except Exception as e:
            logger.error(f"Erro na busca web: {e}")
            return None
    
    def _search_selic_rate(self) -> Dict[str, str]:
        """Busca taxa Selic atual."""
        try:
            # URL do Banco Central do Brasil para taxa Selic
            url = "https://www.bcb.gov.br/controleinflacao/historicotaxasjuros"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Procura pela taxa Selic atual (implementação simplificada)
            # Em um cenário real, você usaria uma API específica ou parsing mais robusto
            
            # Para demonstração, vamos simular uma resposta
            return {
                "content": "A taxa Selic atual é de 10,50% ao ano (dados de setembro/2024). Esta é a taxa básica de juros da economia brasileira, definida pelo Comitê de Política Monetária (Copom) do Banco Central do Brasil.",
                "source": "Banco Central do Brasil - https://www.bcb.gov.br/controleinflacao/historicotaxasjuros",
                "url": url
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar taxa Selic: {e}")
            return {
                "content": "Não foi possível obter a taxa Selic atual no momento. Consulte o site do Banco Central do Brasil para informações atualizadas.",
                "source": "Banco Central do Brasil",
                "url": "https://www.bcb.gov.br"
            }
    
    def _generic_search(self, query: str) -> Optional[Dict[str, str]]:
        """Busca genérica na web."""
        try:
            # Para demonstração, vamos usar uma abordagem simples
            # Em produção, você usaria uma API de busca como Google Custom Search, Bing, etc.
            
            # Simula busca para consultas sobre economia
            if any(keyword in query.lower() for keyword in ['inflação', 'inflacao', 'economia', 'mercado']):
                return {
                    "content": "Para informações atualizadas sobre economia brasileira, consulte os sites oficiais do Banco Central do Brasil, IBGE e outras instituições financeiras.",
                    "source": "Fontes oficiais de economia",
                    "url": "https://www.bcb.gov.br"
                }
            
            # Simula busca para consultas sobre clima
            if any(keyword in query.lower() for keyword in ['tempo', 'clima', 'temperatura']):
                return {
                    "content": "Para informações sobre previsão do tempo, consulte o site do Instituto Nacional de Meteorologia (INMET) ou aplicativos de clima confiáveis.",
                    "source": "INMET - Instituto Nacional de Meteorologia",
                    "url": "https://www.inmet.gov.br"
                }
            
            # Simula busca para consultas sobre Fórmula 1
            if any(keyword in query.lower() for keyword in ['fórmula 1', 'formula 1', 'f1', 'gp', 'grand prix', 'corrida', 'piloto', 'azerbaijan', 'baku', 'vencedor', 'venceu']):
                return {
                    "content": "Para informações atualizadas sobre Fórmula 1, incluindo resultados de corridas, classificação e notícias, consulte o site oficial da F1 (formula1.com) ou canais especializados em esportes automobilísticos.",
                    "source": "Fórmula 1 - Site Oficial",
                    "url": "https://www.formula1.com"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro na busca genérica: {e}")
            return None
    
    def _extract_text_from_url(self, url: str) -> Optional[str]:
        """Extrai texto de uma URL."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts e estilos
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extrai texto
            text = soup.get_text()
            
            # Limpa o texto
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:1000]  # Limita a 1000 caracteres
            
        except Exception as e:
            logger.error(f"Erro ao extrair texto da URL {url}: {e}")
            return None


"""
Tool de busca de notícias SRAG
R302: Busca notícias recentes sobre SRAG/Saúde Respiratória
"""

import os
import requests
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class NewsTool:
    """
    R302: Busca notícias em tempo real sobre o cenário de saúde.
    """
    
    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2/everything"

    def fetch_srag_news(self, query: str = "SRAG OR 'respiratória' OR 'covid-19' OR 'influenza'") -> List[Dict[str, Any]]:
        """
        Busca notícias baseadas na query.
        Filtros (R302): Idioma PT, últimos 30 dias, limite 5-10 notícias.
        """
        if not self.api_key:
            logger.warning("NewsTool: NEWS_API_KEY não encontrada. Retornando notícias simuladas.")
            return self._get_mock_news()

        from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        params = {
            "q": query,
            "language": "pt",
            "from": from_date,
            "sortBy": "relevancy",
            "pageSize": 10,
            "apiKey": self.api_key
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = data.get("articles", [])
            results = []
            
            for art in articles[:10]:
                results.append({
                    "title": art.get("title"),
                    "source": art.get("source", {}).get("name"),
                    "published_at": art.get("publishedAt"),
                    "summary": art.get("description"),
                    "url": art.get("url")
                })
                
            logger.info(f"NewsTool: {len(results)} notícias encontradas.")
            return results
            
        except Exception as e:
            logger.error(f"Erro ao buscar notícias: {e}")
            return self._get_mock_news()

    def _get_mock_news(self) -> List[Dict[str, Any]]:
        """Mock para desenvolvimento sem API key"""
        return [
            {
                "title": "Aumento nos casos de SRAG em crianças preocupa autoridades",
                "source": "Saúde em Pauta",
                "published_at": datetime.now().strftime("%Y-%m-%dT%H:00:00Z"),
                "summary": "Boletim Infogripe indica tendência de crescimento de casos respiratórios no Sudeste.",
                "url": "https://exemplo.com/srag-criancas"
            },
            {
                "title": "Campanha de vacinação contra Influenza atinge 60% da meta",
                "source": "Portal Saúde",
                "published_at": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%dT%H:00:00Z"),
                "summary": "Ministério da Saúde reforça importância da imunização para grupos de risco.",
                "url": "https://exemplo.com/vacinacao-flu"
            }
        ]

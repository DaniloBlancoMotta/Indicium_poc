"""
Ferramenta de Busca Web Híbrida (R302)
Combina Tavily Search para notícias gerais e scraping direto 
de portais oficiais (Gov.br, SP Gov) conforme a regra @[/engineer].
"""

import logging
import requests
import os
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from tavily import TavilyClient

logger = logging.getLogger(__name__)

class WebSearchTool:
    """
    Ferramenta de busca web que agrega:
    1. Busca via Tavily (Notícias Gerais) - Substitui DuckDuckGo
    2. Scraping direto do portal Gov.br (Ministério da Saúde)
    3. Scraping direto da Secretaria de Saúde SP
    """
    
    def __init__(self, max_results: int = 5):
        # Correção Agressiva para SSL/TLS
        # 1. Limpar variáveis conflitantes
        keys_to_remove = []
        for key in os.environ.keys():
            if key.upper() in ['REQUESTS_CA_BUNDLE', 'SSL_CERT_FILE', 'CURL_CA_BUNDLE']:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            val = os.environ[key]
            logger.warning(f"Removendo variável conflitante: {key}={val}")
            del os.environ[key]

        # 2. Forçar uso do Certifi
        try:
            import certifi
            cert_path = certifi.where()
            os.environ['REQUESTS_CA_BUNDLE'] = cert_path
            os.environ['SSL_CERT_FILE'] = cert_path
            logger.info(f"SSL forçado para: {cert_path}")
        except ImportError:
            logger.warning("Certifi não encontrado. SSL dependerá do sistema.")
        
        self.max_results = max_results
        self.tavily_client = None
        
        # 1. Configuração Tavily
        api_key = os.getenv("TAVILY_API_KEY")
        if api_key:
            try:
                self.tavily_client = TavilyClient(api_key=api_key)
            except Exception as e:
                logger.error(f"Erro ao inicializar Tavily: {e}")
        else:
            logger.warning("TAVILY_API_KEY não configurada. Busca geral indisponível.")
            
        # Headers para requests (evitar bloqueio básico nos scrapers)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _scrape_gov_br(self, query: str = "SRAG") -> List[Dict]:
        """
        Busca em https://www.gov.br/saude/pt-br/search
        Mantido para redundância e foco em fonte oficial.
        """
        base_url = "https://www.gov.br/saude/pt-br/search"
        params = {
            'origem': 'form',
            'SearchableText': query
        }
        
        logger.info(f"Scraping Gov.br para '{query}'...")
        results = []
        
        try:
            response = requests.get(base_url, params=params, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Seletores típicos do Plone/Gov.br (searchResults)
                items = soup.find_all('dt', class_='contenttype-news-item')
                # Fallback se não for news item
                if not items:
                    items = soup.find_all('dt') 
                
                for item in items[:3]: # Top 3
                    try:
                        link_tag = item.find('a')
                        if link_tag:
                            title = link_tag.get_text(strip=True)
                            link = link_tag['href']
                            
                            # Tentar pegar descrição (dd tag logo após dt)
                            desc = ""
                            dd = item.find_next_sibling('dd')
                            if dd:
                                desc = dd.get_text(strip=True)
                            
                            results.append({
                                "title": title,
                                "source": "Ministério da Saúde (Gov.br)",
                                "published_at": "", # Difícil extrair sem parsing complexo
                                "summary": desc[:200] + "..." if len(desc) > 200 else desc,
                                "url": link
                            })
                    except Exception as loop_e:
                        continue
                        
            return results
        except Exception as e:
            logger.warning(f"Falha ao acessar Gov.br: {e}")
            return []

    def _scrape_sp_saude(self) -> List[Dict]:
        """
        Busca em https://www.saude.sp.gov.br/ses/perfil/profissional-da-saude/
        Focando em boletins ou notícias recentes.
        Nota: SP Gov muitas vezes é estático/lista de links.
        """
        url = "https://www.saude.sp.gov.br/ses/perfil/profissional-da-saude/"
        logger.info(f"Scraping Saúde SP...")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Buscar links que mencionem SRAG ou Influenza
                results = []
                links = soup.find_all('a', href=True)
                
                for link in links:
                    text = link.get_text(strip=True).lower()
                    if 'srag' in text or 'influenza' in text or 'respiratória' in text:
                        title = link.get_text(strip=True)
                        href = link['href']
                        if not href.startswith('http'):
                            href = f"https://www.saude.sp.gov.br{href}"
                            
                        results.append({
                            "title": title,
                            "source": "Secretaria Saúde SP",
                            "published_at": "",
                            "summary": "Boletim Oficial / Destaque do Portal",
                            "url": href
                        })
                        
                        if len(results) >= 2: break
                return results
                
            return []
        except Exception as e:
            logger.warning(f"Falha ao acessar Saúde SP: {e}")
            return []

    def fetch_srag_news(self) -> List[Dict]:
        """
        Agrega resultados de múltiplas fontes.
        Retorna lista de dicts com: title, source, published_at, summary, url
        """
        all_news = []
        
        # 1. Busca Oficial Gov.br
        gov_news = self._scrape_gov_br("SRAG 2026")
        all_news.extend(gov_news)
        
        # 2. Busca Saúde SP
        sp_news = self._scrape_sp_saude()
        all_news.extend(sp_news)
        
        # 3. Tavily (Notícias Gerais/Imprensa)
        if self.tavily_client:
            try:
                # Queries combinadas
                q = "aumento casos srag brasil influenza surto 2026"
                logger.info(f"Buscando notícias via Tavily: {q}")
                
                response = self.tavily_client.search(
                    query=q,
                    search_depth="advanced",
                    include_answer=False,
                    include_raw_content=False,
                    max_results=5,
                    topic="news" # Otimizado para notícias
                )
                
                results = response.get("results", [])
                
                for item in results:
                    all_news.append({
                        "title": item.get('title', 'Notícia Relacionada'),
                        "source": "Imprensa (Tavily)",
                        "published_at": item.get('published_date', ''),
                        "summary": item.get('content', '')[:300] + "...",
                        "url": item.get('url', '#')
                    })
                    
            except Exception as e:
                logger.error(f"Erro Tavily: {e}")
                import traceback
                logger.error(traceback.format_exc())
                
        return all_news

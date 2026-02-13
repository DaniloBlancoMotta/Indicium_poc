"""
Ferramenta de Busca Web Híbrida (R302)
Combina DuckDuckGo Search para notícias gerais e scraping direto 
de portais oficiais (Gov.br, SP Gov) conforme a regra @[/engineer].
"""

import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class WebSearchTool:
    """
    Ferramenta de busca web que agrega:
    1. Busca via DuckDuckGo (Notícias Gerais)
    2. Scraping direto do portal Gov.br (Ministério da Saúde)
    3. Scraping direto da Secretaria de Saúde SP
    """
    
    def __init__(self, max_results: int = 5):
        # Correção para ambientes Windows com variáveis SSL mal configuradas
        import os
        for env_var in ['REQUESTS_CA_BUNDLE', 'SSL_CERT_FILE']:
            val = os.environ.get(env_var)
            if val and not os.path.exists(val):
                logger.warning(f"Removendo variável SSL inválida: {env_var}={val}")
                del os.environ[env_var]
        
        self.max_results = max_results
        
        # 1. Configuração DuckDuckGo
        try:
            self.wrapper = DuckDuckGoSearchAPIWrapper(
                region="br-pt",
                time="y",  # 'd' (day), 'w' (week), 'm' (month), 'y' (year)
                max_results=max_results
            )
            self.search = DuckDuckGoSearchResults(
                api_wrapper=self.wrapper,
                backend="news"
            )
        except Exception as e:
            logger.error(f"Erro ao inicializar DuckDuckGo: {e}")
            self.search = None
            
        # Headers para requests (evitar bloqueio básico)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _scrape_gov_br(self, query: str = "SRAG") -> List[Dict]:
        """
        Busca em https://www.gov.br/saude/pt-br/search
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
                            
                            # Tentar pegar data (span.documentByLine)
                            date_str = ""
                            
                            results.append({
                                "title": title,
                                "source": "Ministério da Saúde (Gov.br)",
                                "published_at": date_str,
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
        
        # 3. DuckDuckGo (Notícias Gerais/Imprensa)
        if self.wrapper:
            try:
                # Queries combinadas
                q = "aumento casos srag brasil influenza surto 2026"
                # Usar .results() do wrapper para obter lista de dicts estruturada
                ddg_results = self.wrapper.results(q, max_results=5)
                
                for item in ddg_results:
                    all_news.append({
                        "title": item.get('title', 'Notícia Relacionada'),
                        "source": "Imprensa (DuckDuckGo)",
                        "published_at": "", # DDG wrapper nem sempre retorna data
                        "summary": item.get('snippet', ''),
                        "url": item.get('link', '#')
                    })
                    
            except Exception as e:
                logger.error(f"Erro DuckDuckGo: {e}")
                
        return all_news

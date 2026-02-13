"""
Módulo do Agente SRAG
R300: LangChain framework com Claude (via Groq)
R304: Orquestração Tools -> Relatório
"""

import os
import logging
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

from .tools.database_tool import DatabaseTool
from .tools.web_search_tool import WebSearchTool
from . import config

load_dotenv()
logger = logging.getLogger(__name__)

class SRAGAgent:
    """
    Agente que orquestra a análise de dados e notícias (R300).
    Suporta múltiplas chaves de API para fallback.
    """
    
    def __init__(self):
        # Carrega chaves de API (Principal e Fallback)
        self.api_keys: List[str] = []
        
        primary_key = os.getenv("GROQ_API_KEY")
        if primary_key:
            self.api_keys.append(primary_key)
            
        fallback_key = os.getenv("GROQ_API_KEY_FALLBACK")
        if fallback_key and fallback_key != primary_key:
            self.api_keys.append(fallback_key)
            
        if not self.api_keys:
            logger.warning("Agent: Nenhuma chave GROQ_API_KEY configurada. Insights serão simulados.")
            
        self.db_tool = DatabaseTool()
        self.news_tool = WebSearchTool(max_results=5)

    def _get_system_prompt(self) -> str:
        """R303: Definição do papel do agente"""
        return (
            "Você é um analista de dados de saúde especializado em SRAG (Síndrome Respiratória Aguda Grave).\n"
            "Sua função é gerar relatórios completos usando dados do banco e contexto de notícias recentes.\n"
            "Seja objetivo, preciso e forneça insights acionáveis.\n"
            "Analise as métricas fornecidas e as correlacione com o contexto das notícias.\n"
            "Identifique tendências de crescimento, riscos de mortalidade ou gargalos na vacinação."
        )

    def _create_llm(self, api_key: str):
        """Cria uma instância do ChatGroq com a chave fornecida."""
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            groq_api_key=api_key
        )

    def _generate_insights(self, metrics_data: Any, news_data: Any) -> tuple[str, str]:
        """
        Gera insights usando LLM com mecanismo de fallback de chaves de API.
        Retorna (insights_dados, insights_noticias).
        """
        if not self.api_keys:
            msg = (
                "ANÁLISE AUTOMÁTICA INDISPONÍVEL (MODO OFFLINE)\n"
                "Configure o arquivo .env com uma chave válida."
            )
            return msg, msg

        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("user", (
                "Aqui estão os dados atuais de SRAG:\n"
                "Métricas: {metrics}\n\n"
                "Notícias Recentes: {news}\n\n"
                "Gere duas análises distintas separadas exatamente pela string '===SEPARADOR===':\n"
                "1. ANÁLISE DE DADOS: Focada estritamente nos números, tendências estatísticas e gráficos.\n"
                "2. ANÁLISE DE NOTÍCIAS: Focada no contexto externo, o que a mídia está reportando e correlação qualitativa.\n"
                "Estruture esta seção em tópicos profissionais (bullet points), seja direto e utilize dados relevantes extraídos das notícias.\n"
                "\nImportante: Use '===SEPARADOR===' entre as duas seções."
            ))
        ])

        last_error = None
        
        for i, key in enumerate(self.api_keys):
            try:
                masked_key = f"{key[:4]}...{key[-4:]}"
                logger.info(f"Tentando gerar insights com a chave {i+1}/{len(self.api_keys)} ({masked_key})...")
                
                llm = self._create_llm(key)
                chain = prompt | llm
                
                response = chain.invoke({
                    "metrics": str(metrics_data),
                    "news": str(news_data)
                })
                
                full_text = response.content
                if "===SEPARADOR===" in full_text:
                    parts = full_text.split("===SEPARADOR===")
                    return parts[0].strip(), parts[1].strip()
                else:
                    return full_text, "Não foi possível separar a análise de notícias."
                    
            except Exception as e:
                logger.warning(f"Erro com a chave {i+1}: {e}")
                last_error = e
                continue
        
        # Se chegou aqui, todas as chaves falharam
        logger.error(f"Todas as chaves de API falharam. Último erro: {last_error}")
        return "Erro ao gerar insights de dados.", "Erro ao gerar insights de notícias."

    def analyze_status(self) -> Dict[str, Any]:
        """
        Orquestração (R304):
        1. Busca métricas no banco
        2. Busca notícias recentes
        3. Sintetiza com LLM (com retry/fallback)
        """
        logger.info("Agente iniciando análise...")
        
        # 1. Database Tool (R301)
        metrics_data = self.db_tool.get_all_metrics()
        
        # 1.5. Generate Charts
        charts_paths = self.db_tool.generate_charts(output_dir=config.OUTPUTS / "assets")
        
        # 2. News Tool (R302)
        news_data = self.news_tool.fetch_srag_news()
        
        # 3. LLM Synthesis (R304)
        insights_data, insights_news = self._generate_insights(metrics_data, news_data)
        
        return {
            "metrics": metrics_data,
            "news": news_data,
            "insights": insights_data + "\n\n" + insights_news,
            "insights_data": insights_data,
            "insights_news": insights_news,
            "charts": charts_paths
        }

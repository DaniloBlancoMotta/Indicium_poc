"""
Módulo do Agente SRAG
R300: LangChain framework com Claude
R304: Orquestração Tools -> Relatório
"""

import os
import logging
from typing import Dict, Any
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
    """
    
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if self.api_key:
            try:
                self.llm = ChatGroq(
                    model="llama-3.3-70b-versatile",
                    temperature=0,
                    groq_api_key=self.api_key
                )
            except Exception as e:
                logger.warning(f"Erro ao inicializar Groq: {e}")
                self.llm = None
        else:
            logger.warning("Agent: GROQ_API_KEY não configurada. Insights serão simulados.")
            self.llm = None
            
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

    def analyze_status(self) -> Dict[str, Any]:
        """
        Orquestração (R304):
        1. Busca métricas no banco
        2. Busca notícias recentes
        3. Sintetiza com LLM
        """
        logger.info("Agente iniciando análise...")
        
        # 1. Database Tool (R301)
        metrics_data = self.db_tool.get_all_metrics()
        
        # 1.5. Generate Charts
        charts_paths = self.db_tool.generate_charts(output_dir=config.OUTPUTS / "assets")
        
        
        # 2. News Tool (R302)
        news_data = self.news_tool.fetch_srag_news()
        
        if self.llm:
            try:
                # 3. LLM Synthesis (R304)
                # 3. LLM Synthesis (R304)
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
                
                chain = prompt | self.llm
                
                logger.info("Gerando insights com Llama 3 (Groq)...")
                response = chain.invoke({
                    "metrics": str(metrics_data),
                    "news": str(news_data)
                })
                
                full_text = response.content
                if "===SEPARADOR===" in full_text:
                    parts = full_text.split("===SEPARADOR===")
                    insights_data = parts[0].strip()
                    insights_news = parts[1].strip()
                else:
                    insights_data = full_text
                    insights_news = "Não foi possível separar a análise de notícias."

            except Exception as e:
                logger.error(f"Erro na geração de insights: {e}")
                insights_data = "Erro ao gerar insights de dados."
                insights_news = "Erro ao gerar insights de notícias."
        else:
            insights_data = (
                "ANÁLISE AUTOMÁTICA INDISPONÍVEL (MODO OFFLINE)\n"
                "Configure o arquivo .env com uma chave válida."
            )
            insights_news = insights_data
        
        return {
            "metrics": metrics_data,
            "news": news_data,
            "insights": insights_data + "\n\n" + insights_news, # Mantendo compatibilidade com código antigo se necessário
            "insights_data": insights_data,
            "insights_news": insights_news,
            "charts": charts_paths
        }

"""
Script Principal de Execução (R500)
Orquestra a preparação de dados, análise do agente e geração de relatório.
"""

import sys
import logging
import os
from pathlib import Path

# Fix SSL issues on Windows (PostgreSQL path bug) - MUST BE BEFORE OTHER IMPORTS
for env_var in ['REQUESTS_CA_BUNDLE', 'SSL_CERT_FILE']:
    val = os.environ.get(env_var)
    if val and not os.path.exists(val):
        print(f"Ambiente: Removendo variável SSL inválida para evitar erros: {env_var}='{val}'")
        del os.environ[env_var]

from agent import loader, agent, report_generator, config

# R501: Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/agent.log", encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Iniciando Sistema de Monitoramento SRAG (PoC)")
    
    try:
        # 1. Preparação de Dados (Fase 1)
        if not config.DATABASE_PATH.exists():
            logger.info("Banco de dados não detectado. Iniciando pipeline de preparação...")
            df_raw = loader.load_from_csv(max_chunks=5) # 250k registros para PoC
            df_clean = loader.clean_data(df_raw)
            loader.ingest_to_sqlite(df_clean)
        else:
            logger.info("Banco de dados existente detectado.")

        # 2. Execução do Agente (Fase 3)
        srag_agent = agent.SRAGAgent()
        analysis_result = srag_agent.analyze_status()

        # 3. Geração do Relatório (Fase 4)
        reporter = report_generator.ReportGenerator()
        generated_files = reporter.generate_reports(
            data=analysis_result
        )
        
        logger.info(f"Execução concluída com sucesso!")
        for fpath in generated_files:
            logger.info(f"Relatório gerado: {fpath}")

    except Exception as e:
        logger.error(f"Erro crítico na execução: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

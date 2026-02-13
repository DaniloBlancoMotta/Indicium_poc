"""
Tool de interface com o banco de dados SRAG
R301: Implementa busca de métricas e dados para gráficos
"""

import sqlite3
import pandas as pd
from typing import Dict, Any, List
import logging
from pathlib import Path
from .. import config, metrics, loader, charts

logger = logging.getLogger(__name__)

class DatabaseTool:
    """
    R301: Fornece métodos estruturados para o agente acessar o banco.
    """
    
    def __init__(self, db_path: str = str(config.DATABASE_PATH)):
        self.db_path = db_path

    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Calcula as 4 métricas obrigatórias a partir do banco.
        """
        logger.info("DatabaseTool: Calculando métricas gerais...")
        df = loader.load_from_sqlite()
        if df.empty:
            return {"error": "Banco de dados vazio ou não encontrado"}
        
        return metrics.calculate_all_metrics(df)

    def get_chart_data_daily(self, last_n_days: int = 30) -> Dict[str, Any]:
        """
        Retorna dados estruturados para o gráfico diário.
        """
        logger.info(f"DatabaseTool: Buscando dados diários ({last_n_days} dias)...")
        df = loader.load_from_sqlite()
        if df.empty:
            return {"error": "Dados insuficientes"}
        
        # Filtro simplificado para retorno estruturado
        df['dt_notificacao'] = pd.to_datetime(df['dt_notificacao'])
        max_date = df['dt_notificacao'].max()
        df_filtered = df[df['dt_notificacao'] > (max_date - pd.Timedelta(days=last_n_days))]
        
        daily_counts = df_filtered.groupby(df_filtered['dt_notificacao'].dt.date).size()
        
        return {
            "dates": [str(d) for d in daily_counts.index],
            "counts": [int(c) for c in daily_counts.values],
            "total": int(daily_counts.sum())
        }

    def get_chart_data_monthly(self, last_n_months: int = 12) -> Dict[str, Any]:
        """
        Retorna dados estruturados para o gráfico mensal.
        """
        logger.info(f"DatabaseTool: Buscando dados mensais ({last_n_months} meses)...")
        df = loader.load_from_sqlite()
        if df.empty:
            return {"error": "Dados insuficientes"}
        
        df['dt_notificacao'] = pd.to_datetime(df['dt_notificacao'])
        df['month'] = df['dt_notificacao'].dt.to_period('M')
        monthly_counts = df.groupby('month').size().iloc[-last_n_months:]
        
        return {
            "months": [str(m) for m in monthly_counts.index],
            "counts": [int(c) for c in monthly_counts.values],
            "total": int(monthly_counts.sum())
        }

    def generate_charts(self, output_dir: Path) -> Dict[str, str]:
        """
        Gera os arquivos de gráfico físicos e retorna seus caminhos.
        """
        logger.info(f"DatabaseTool: Gerando gráficos em {output_dir}...")
        df = loader.load_from_sqlite()
        
        if df.empty:
            logger.warning("DatabaseTool: DataFrame vazio, gráficos não serão gerados.")
            return {}

        # Criar diretório se não existir
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Caminhos dos arquivos
        daily_chart_path = output_dir / "cases_daily.png"
        monthly_chart_path = output_dir / "cases_monthly.png"
        
        # Gerar Gráfico Diário
        charts.plot_daily_cases(
            df, 
            save_path=str(daily_chart_path)
        )
        
        # Gerar Gráfico Mensal
        charts.plot_monthly_cases(
            df,
            save_path=str(monthly_chart_path)
        )
        
        return {
            "daily_chart": str(daily_chart_path),
            "monthly_chart": str(monthly_chart_path)
        }

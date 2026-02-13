"""
Módulo de cálculo de métricas SRAG
R200: Implementa EXATAMENTE 4 métricas (R201, R202, R203, R204)
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from . import config

logger = logging.getLogger(__name__)


def get_effective_end_date(df: pd.DataFrame, date_column: str) -> pd.Timestamp:
    """
    Determina a data final efetiva ignorando outliers no futuro ou erros de digitação.
    Usa o Percentil 99.5 das datas como corte.
    """
    try:
        # Converter para timestamp (int64) para estatística
        valid_dates = df[df[date_column].notna()][date_column]
        if valid_dates.empty:
            return pd.Timestamp.now()
            
        timestamps = valid_dates.astype('int64')
        p99_5 = np.percentile(timestamps, 99.5)
        
        effective_date = pd.to_datetime(p99_5)
        
        # Validar se não dropou "demais" (Ex: mais de 60 dias do max real)
        # Se for um dataset histórico "limpo", o max real deve ser usado se a densidade for alta
        # Mas para garantir robustez:
        max_real = valid_dates.max()
        if (max_real - effective_date).days > 365:
            # Se o P99.5 está a mais de um ano do fim, algo está estranho, 
            # mas vamos confiar no P99.5 para evitar aquele 2021 isolado
            logger.warning(f"Data efetiva (P99.5) {effective_date.date()} muito distante do MAX {max_real.date()}. Usando P99.5.")
            
        return effective_date
    except Exception as e:
        logger.warning(f"Erro ao calcular data efetiva: {e}. Usando MAX.")
        return df[date_column].max()

def calculate_case_growth_rate(
    df: pd.DataFrame,
    date_column: str = 'dt_notificacao'
) -> Dict[str, float]:
    """
    R201: Taxa de Aumento de Casos
    Compara últimos 30 dias vs 30 dias anteriores.
    Fórmula: ((casos_30d - casos_30d_ant) / casos_30d_ant) * 100
    """
    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
    df = df[df[date_column].notna()]
    
    if df.empty:
        return {'growth_rate': 0.0, 'current_period_cases': 0, 'previous_period_cases': 0, 'growth_absolute': 0}
    
    # Usar data efetiva (P99.5) para ignorar outliers de 2021 isolados
    max_date = get_effective_end_date(df, date_column)
    logger.info(f"Data de referência para métricas (P99.5): {max_date.date()}")
    
    # Período atual (últimos 30 dias a partir da data efetiva)
    date_start_current = max_date - timedelta(days=30)
    casos_30d = len(df[df[date_column] > date_start_current])
    
    # Período anterior (30 dias anteriores)
    date_start_prev = date_start_current - timedelta(days=30)
    casos_30d_ant = len(df[(df[date_column] > date_start_prev) & (df[date_column] <= date_start_current)])
    
    # Cálculo (R201)
    growth_absolute = casos_30d - casos_30d_ant
    growth_rate = ((casos_30d - casos_30d_ant) / casos_30d_ant * 100) if casos_30d_ant > 0 else 0.0
    
    return {
        'current_period_cases': int(casos_30d),
        'previous_period_cases': int(casos_30d_ant),
        'growth_rate': round(growth_rate, 2),
        'growth_absolute': int(growth_absolute)
    }

def calculate_mortality_rate(
    df: pd.DataFrame,
    outcome_column: str = 'teve_obito',
    death_value: bool = True
) -> Dict[str, float]:
    """
    R202: Taxa de Mortalidade
    Fórmula: (total_óbitos / total_casos) * 100
    """
    # Filtrar apenas casos com evolução definida (R202)
    # teve_obito is boolean or None (NaN)
    df_valid = df[df[outcome_column].notna()].copy()
    
    total_cases = len(df_valid)
    deaths = (df_valid[outcome_column] == death_value).sum()
    
    mortality_rate = (deaths / total_cases * 100) if total_cases > 0 else 0.0
    
    return {
        'total_cases': int(total_cases),
        'deaths': int(deaths),
        'mortality_rate': round(mortality_rate, 2)
    }

def calculate_icu_occupancy_rate(
    df: pd.DataFrame,
    icu_column: str = 'teve_uti',
    icu_yes_value: bool = True
) -> Dict[str, float]:
    """
    R203: Taxa de Ocupação de UTI
    Fórmula: (casos_uti / total_casos) * 100
    """
    # Filtrar registros com informação de UTI (R203)
    df_valid = df[df[icu_column].notna()].copy()
    
    total_cases = len(df_valid)
    icu_cases = (df_valid[icu_column] == icu_yes_value).sum()
    
    icu_rate = (icu_cases / total_cases * 100) if total_cases > 0 else 0.0
    
    return {
        'total_cases': int(total_cases),
        'icu_cases': int(icu_cases),
        'icu_rate': round(icu_rate, 2)
    }

def calculate_vaccination_rate(
    df: pd.DataFrame,
    vaccine_column: str = 'esta_vacinado',
    vaccinated_value: bool = True
) -> Dict[str, float]:
    """
    R204: Taxa de Vacinação
    Fórmula: (casos_vacinados / total_casos) * 100
    """
    # Tratar valores ausentes adequadamente (R204)
    # Data workflow says: esta_vacinado Boolean
    df_valid = df[df[vaccine_column].notna()].copy()
    
    total_cases = len(df_valid)
    vaccinated = (df_valid[vaccine_column] == vaccinated_value).sum()
    
    vaccination_rate = (vaccinated / total_cases * 100) if total_cases > 0 else 0.0
    
    return {
        'total_cases': int(total_cases),
        'vaccinated': int(vaccinated),
        'vaccination_rate': round(vaccination_rate, 2)
    }

def calculate_all_metrics(df: pd.DataFrame) -> Dict[str, Dict]:
    """
    Calcula todas as 4 métricas-chave obrigatórias.
    """
    logger.info("=" * 80)
    logger.info("CÁLCULO DE MÉTRICAS OBRIGATÓRIAS (ENGENHARIA)")
    logger.info("=" * 80)
    
    metrics = {
        'growth': calculate_case_growth_rate(df),
        'mortality': calculate_mortality_rate(df),
        'icu': calculate_icu_occupancy_rate(df),
        'vaccination': calculate_vaccination_rate(df)
    }
    
    logger.info(f"✓ Crescimento (30d): {metrics['growth']['growth_rate']:+.2f}%")
    logger.info(f"✓ Mortalidade: {metrics['mortality']['mortality_rate']:.2f}%")
    logger.info(f"✓ Ocupação UTI: {metrics['icu']['icu_rate']:.2f}%")
    logger.info(f"✓ Vacinação: {metrics['vaccination']['vaccination_rate']:.2f}%")
    logger.info("=" * 80)
    
    return metrics

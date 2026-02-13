"""
Módulo de geração de gráficos SRAG
Implementa as visualizações obrigatórias (diária e mensal)
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import timedelta
from typing import Tuple, Optional
import logging
from . import config
from .metrics import get_effective_end_date

logger = logging.getLogger(__name__)

# Configurar estilo
plt.style.use(config.PLOT_STYLE)

def plot_daily_cases(
    df: pd.DataFrame,
    date_column: str = 'dt_notificacao',
    last_n_days: int = 30,
    figsize: Tuple[int, int] = (14, 6),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plota casos diários (últimos 30 dias).
    R211: Gráfico de linha, labels nos eixos, salva como PNG.
    """
    # Preparar dados
    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
    df = df[df[date_column].notna()]
    
    # Filtrar últimos N dias
    # Filtrar últimos N dias
    # Usar get_effective_end_date para consistência com métricas (ignorar outliers 2021)
    max_date = get_effective_end_date(df, date_column)
    min_date = max_date - timedelta(days=last_n_days)
    df_filtered = df[df[date_column] >= min_date]
    # Filtrar também limite superior para não aparecer o outlier se plotar além
    df_filtered = df_filtered[df_filtered[date_column] <= max_date]
    
    # Contar casos por dia
    daily_cases = df_filtered.groupby(df_filtered[date_column].dt.date).size()
    daily_cases.index = pd.to_datetime(daily_cases.index)
    
    # Criar figura
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot
    ax.plot(daily_cases.index, daily_cases.values, 
            marker='o', linewidth=2, markersize=6, 
            color=config.METRIC_COLORS['crescimento'], label='Casos Diários')
    
    # Adicionar média móvel de 7 dias
    if len(daily_cases) >= 7:
        ma_7 = daily_cases.rolling(window=7, center=True).mean()
        ax.plot(ma_7.index, ma_7.values, 
                linewidth=2.5, color='#F18F01', 
                linestyle='--', label='Média Móvel (7 dias)')
    
    # Formatação (R211)
    ax.set_title(f'Casos Diários de SRAG - Últimos {last_n_days} Dias', 
                fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Data (DD/MM)', fontsize=12)
    ax.set_ylabel('Número de Casos', fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper left', fontsize=10)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=config.DPI, bbox_inches='tight')
        logger.info(f"💾 Gráfico diário salvo em: {save_path}")
    
    return fig

def plot_monthly_cases(
    df: pd.DataFrame,
    date_column: str = 'dt_notificacao',
    last_n_months: int = 12,
    figsize: Tuple[int, int] = (14, 6),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plota casos mensais (últimos 12 meses).
    R212: Gráfico de barras, labels nos eixos, salva como PNG.
    """
    # Preparar dados
    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
    df = df[df[date_column].notna()]

    # Filtrar até data efetiva para tirar o mês vazio de 2021
    max_date = get_effective_end_date(df, date_column)
    df = df[df[date_column] <= max_date]
    
    # Agrupar por mês
    df['month'] = df[date_column].dt.to_period('M')
    monthly_cases = df.groupby('month').size().sort_index()
    
    # Filtrar últimos N meses
    if len(monthly_cases) > last_n_months:
        monthly_cases = monthly_cases.iloc[-last_n_months:]
    
    # Converter índice para datetime para plotagem
    monthly_cases.index = monthly_cases.index.to_timestamp()
    
    # Criar figura
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot de barras (R212)
    bars = ax.bar(monthly_cases.index, monthly_cases.values, 
                  width=20, color=config.METRIC_COLORS['mortalidade'], alpha=0.7, 
                  edgecolor='black', linewidth=1.2)
    
    # Formatação
    ax.set_title(f'Casos Mensais de SRAG - Últimos {last_n_months} Meses', 
                fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Mês/Ano (MM/YYYY)', fontsize=12)
    ax.set_ylabel('Número de Casos', fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    plt.xticks(rotation=45, ha='right')
    
    # Adicionar valores nas barras
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=config.DPI, bbox_inches='tight')
        logger.info(f"💾 Gráfico mensal salvo em: {save_path}")
    
    return fig

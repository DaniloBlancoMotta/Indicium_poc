
import streamlit as st
from datetime import datetime
from agent.agent import SRAGAgent, config
from agent import metrics, loader
from datetime import timedelta
import pandas as pd
from agent.metrics import get_effective_end_date

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_metrics_data():
    """
    Loads raw data and calculates metrics for the dashboard.
    Using caching to improve performance (Review: P4).
    """
    try:
        # Load raw data from SQLite
        df = loader.load_from_sqlite()
        
        if df.empty:
            return None, None
            
        # Standardize date column
        date_column = 'dt_notificacao'
        if date_column not in df.columns and 'DT_NOTIFIC' in df.columns:
            df.rename(columns={'DT_NOTIFIC': date_column}, inplace=True)
            
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        
        # Calculate key metrics using existing logic
        all_metrics = metrics.calculate_all_metrics(df)
        
        # Determine trends (simple logic for demo, could be more complex)
        # R201 already provides growth rate
        
        return all_metrics, df
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

@st.cache_data(ttl=3600)
def get_chart_data(df):
    """
    Prepares data for Plotly charts.
    """
    if df is None or df.empty:
        return {}
        
    date_column = 'dt_notificacao'
    
    # --- Daily Data (Last 30 Days) ---
    max_date = get_effective_end_date(df, date_column)
    current_min_date = max_date - timedelta(days=30)
    
    daily_df = df[(df[date_column] >= current_min_date) & 
                  (df[date_column] <= max_date)].copy()
    
    daily_counts = daily_df.groupby(daily_df[date_column].dt.date).size()
    daily_counts.index = pd.to_datetime(daily_counts.index)
    
    # Calculate 7-day moving average
    moving_avg = daily_counts.rolling(window=7, center=True).mean()
    
    # Trend calculation (Linear Regression Slope could be better, using simple diff)
    if len(daily_counts) > 1:
        trend = ((daily_counts.iloc[-1] - daily_counts.iloc[0]) / daily_counts.iloc[0]) * 100 if daily_counts.iloc[0] > 0 else 0
    else:
        trend = 0
        
    daily_data = {
        'dates': daily_counts.index,
        'cases': daily_counts.values,
        'moving_avg_7d': moving_avg.values,
        'peak_date': daily_counts.idxmax().strftime('%d/%m') if not daily_counts.empty else '-',
        'peak_value': int(daily_counts.max()) if not daily_counts.empty else 0,
        'avg': daily_counts.mean() if not daily_counts.empty else 0,
        'trend': trend
    }
    
    # --- Monthly Data (Last 12 Months) ---
    # Using existing logic logic from charts.py adapted
    df['month'] = df[date_column].dt.to_period('M')
    # Filter up to effective date
    monthly_df = df[df[date_column] <= max_date].copy()
    monthly_counts = monthly_df.groupby('month').size().sort_index().tail(12)
    
    monthly_data = {
        'months': [d.strftime('%m/%Y') for d in monthly_counts.index],
        'cases': monthly_counts.values,
        'avg': monthly_counts.mean() if not monthly_counts.empty else 0,
        'highest_month': monthly_counts.idxmax().strftime('%m/%Y') if not monthly_counts.empty else '-',
        'highest_value': int(monthly_counts.max()) if not monthly_counts.empty else 0,
        'lowest_month': monthly_counts.idxmin().strftime('%m/%Y') if not monthly_counts.empty else '-',
        'lowest_value': int(monthly_counts.min()) if not monthly_counts.empty else 0
    }
    
    # --- Geographic Data ---
    geo_counts = df['uf_sigla'].value_counts().reset_index()
    geo_counts.columns = ['state', 'cases']
    
    geographic_data = geo_counts
    
    return {
        'daily': daily_data,
        'monthly': monthly_data,
        'geographic': geographic_data
    }

def fetch_agent_analysis():
    """Calls the LangChain agent for new analysis."""
    agent = SRAGAgent()
    return agent.analyze_status()

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path
import logging

# PAGE CONFIG (Must be first Streamlit command)
st.set_page_config(
    page_title="SRAG Analytics Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from components.header import render_header
from components.metrics_cards import render_metrics
from components.charts import render_charts
from components.news_feed import render_news_feed
from components.sidebar import render_sidebar
from utils.data_loader import load_metrics_data, get_chart_data, fetch_agent_analysis

# Configuração de Logging para o Streamlit
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# CUSTOM CSS
try:
    with open('styles/custom.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("Custom CSS not found. Using defaults.")

# SIDEBAR (Returns config dict if needed)
config_settings = render_sidebar()

# Force refresh if sidebar button clicked
if config_settings.get("refresh"):
    # Clear cache
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()

# MAIN CONTENT
render_header()

# METRICS SECTION
st.markdown("---")
# Loading data with spinner
with st.spinner("Conectando ao banco de dados SRAG..."):
    metrics, df = load_metrics_data()
    
    if metrics:
        render_metrics(metrics)
    else:
        st.error("Falha ao carregar métricas. Verifique a conexão com o banco de dados.")

# CHARTS SECTION
st.markdown("---")
st.subheader("📊 Tendências Epidemiológicas")
if df is not None:
    chart_data = get_chart_data(df)
    render_charts(chart_data)

# INSIGHTS SECTION
st.markdown("---")
st.subheader("🤖 Análise Inteligente (IA)")

# Button to trigger AI Analysis (Expensive operation)
col_ai, col_space = st.columns([1, 4])
with col_ai:
    trigger_ai = st.button("Gerar Relatório Executivo", type="primary", use_container_width=True)

# Container for AI results
if 'ai_report' not in st.session_state:
    st.session_state['ai_report'] = None

if trigger_ai:
    with st.spinner("Agente Llama 3 (Groq) analisando dados e notícias..."):
        try:
            report = fetch_agent_analysis()
            st.session_state['ai_report'] = report
        except Exception as e:
            st.error(f"Erro na execução do agente: {e}")

# Display AI Report if available
if st.session_state['ai_report']:
    report = st.session_state['ai_report']
    
    # Insights Box
    st.success("Análise gerada com sucesso")
    st.markdown(f"""
    <div style="background-color: #f0fdf4; padding: 20px; border-radius: 8px; border-left: 5px solid #22c55e;">
        <h4 style="margin-top:0; color: #15803d;">Insights do Especialista</h4>
        {report.get('insights', 'Insights indisponíveis')}
    </div>
    """, unsafe_allow_html=True)
    
    # News Context
    render_news_feed(report.get('news', []))
else:
    st.info("Clique no botão acima para gerar uma análise detalhada com IA e contexto de notícias recentes.")

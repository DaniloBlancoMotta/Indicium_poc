
import streamlit as st

def render_sidebar():
    """Renders dashboard sidebar configurations"""
    
    st.header("⚙️ Configurações")
    
    st.markdown("---")
    
    st.subheader("Data Range")
    
    # Date Range Selector
    # For now, simplistic controls as the backend is fixed to historical data
    date_range = st.date_input(
        "Selecione o período de análise",
        value=(datetime(2020, 1, 1), datetime(2021, 12, 31)),
        disabled=True, 
        help="O filtro de data está fixado para o dataset de demonstração (2020/2021)."
    )
    
    st.markdown("---")
    
    st.subheader("Ações")
    
    refresh = st.button("🔄 Atualizar Dados", use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("### Sobre")
    st.info(
        "**SRAG Analytics Agent** v1.0\n\n"
        "Sistema de monitoramento epidemiológico desenvolvido como PoC.\n\n"
        "© 2026 Indicium Health"
    )
    
    return {
        "refresh": refresh,
        "date_range": date_range
    }

from datetime import datetime

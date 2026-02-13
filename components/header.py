
import streamlit as st
from datetime import datetime

def render_header():
    """Renders professional header with branding"""
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("🏥 SRAG Analytics Dashboard")
        st.markdown(
            "<p style='font-size: 18px; color: #666;'>"
            "Real-time epidemiological intelligence powered by AI"
            "</p>",
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div style='text-align: right; padding-top: 20px;'>
                <p style='color: #999; font-size: 14px;'>
                    Last Updated<br/>
                    <strong>{datetime.now().strftime('%d/%m/%Y %H:%M')}</strong>
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Subtitle with data source
    st.caption("📊 Data Source: DATASUS OpenData | 🔍 News: Real-time web search")

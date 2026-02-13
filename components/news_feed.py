
import streamlit as st

def render_news_feed(news_data: list):
    """
    Renders news cards context.
    
    Args:
        news_data: List of dicts with 'title', 'source', 'published_at', 'summary', 'url'
    """
    st.subheader("📰 Contexto de Notícias Recentes")
    
    if not news_data:
        st.info("Nenhuma notícia recente disponível no momento.")
        return

    # Use columns to create a grid or list layout
    for item in news_data[:5]:
        st.markdown(
            f"""
            <div class="news-card">
                <h4>{item.get('title', 'Sem Título')}</h4>
                <div class="news-meta">
                    {item.get('source', 'Imprensa (DuckDuckGo)')} | {item.get('published_at', '')}
                </div>
                <div class="news-summary">
                    {item.get('summary', '')}
                </div>
                <div style="margin-top: 10px;">
                    <a href="{item.get('url', '#')}" target="_blank" style="text-decoration: none; color: #1f77b4; font-weight: 500;">Ler na íntegra &rarr;</a>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )

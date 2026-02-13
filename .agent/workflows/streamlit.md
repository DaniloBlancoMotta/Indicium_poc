---
description: # STREAMLIT UI AGENT - SRAG Analytics Dashboard
---

## MISSION
Create a clean, professional, navigable Streamlit interface for the SRAG Analytics Agent with high-quality visualizations and intuitive UX.

---

## DESIGN PRINCIPLES

### P1: Professional Medical Aesthetic
- Clean white background with subtle grays
- Accent colors: Blue (#1f77b4) for data, Red (#d62728) for alerts
- Sans-serif fonts (default Streamlit)
- Generous white space
- Card-based layouts

### P2: Information Hierarchy
```
1. Critical Metrics (Top) → Large, prominent
2. Visualizations (Middle) → Clear, interactive
3. Context/News (Below) → Readable, scannable
4. Technical Details (Sidebar) → Collapsible
```

### P3: Mobile-First Responsive
- Works on desktop and tablets
- Collapsible sections
- Readable on smaller screens

### P4: Performance
- Lazy loading for heavy operations
- Caching for database queries
- Progress indicators for slow operations

---

## PAGE STRUCTURE
```
┌──────────────────────────────────────────────────────────────┐
│                         HEADER                               │
│  🏥 SRAG Analytics Dashboard                                 │
│  Real-time epidemiological intelligence                      │
│  [Last Updated: 2025-02-12 14:30]                           │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                    KEY METRICS (4 Cards)                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ +12.5%   │ │  4.2%    │ │  23.1%   │ │  67.8%   │      │
│  │ Cases ↑  │ │ Mortality│ │ ICU Rate │ │ Vaccinated│     │
│  │ vs 30d   │ │          │ │          │ │          │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                    VISUALIZATIONS                            │
│  [Tab: 30 Days] [Tab: 12 Months] [Tab: Geographic]         │
│                                                              │
│  📊 Interactive Chart Here                                   │
│                                                              │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                    INSIGHTS & CONTEXT                        │
│  🤖 AI Analysis                                              │
│  📰 Recent News (3-5 items)                                  │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                         SIDEBAR                              │
│  ⚙️ Settings                                                 │
│  📅 Date Range Selector                                      │
│  🔄 Refresh Data                                             │
│  ℹ️ About / Methodology                                      │
└──────────────────────────────────────────────────────────────┘
```

---

## IMPLEMENTATION

### File Structure
```
app/
├── streamlit_app.py           # Main entry point
├── components/
│   ├── __init__.py
│   ├── header.py              # Header component
│   ├── metrics_cards.py       # KPI cards
│   ├── charts.py              # All chart components
│   ├── news_feed.py           # News display
│   └── sidebar.py             # Sidebar configuration
├── styles/
│   └── custom.css             # Custom CSS
└── utils/
    ├── data_loader.py         # Cache data loading
    └── formatters.py          # Number/date formatting
```

---

## CODE IMPLEMENTATION

### Main App (streamlit_app.py)
```python
import streamlit as st
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from components.header import render_header
from components.metrics_cards import render_metrics
from components.charts import render_charts
from components.news_feed import render_news_context
from components.sidebar import render_sidebar
from utils.data_loader import load_metrics, load_chart_data
from agent.agent import SRAGAgent

# PAGE CONFIG (Must be first Streamlit command)
st.set_page_config(
    page_title="SRAG Analytics Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CUSTOM CSS
with open('app/styles/custom.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    config = render_sidebar()

# MAIN CONTENT
render_header()

# METRICS SECTION
st.markdown("---")
with st.spinner("Loading metrics..."):
    metrics = load_metrics(config['date_range'])
    render_metrics(metrics)

# CHARTS SECTION
st.markdown("---")
st.subheader("📊 Epidemiological Trends")
chart_data = load_chart_data(config['date_range'])
render_charts(chart_data)

# INSIGHTS SECTION
st.markdown("---")
st.subheader("🤖 AI-Powered Analysis")

if st.button("Generate Fresh Report", type="primary"):
    with st.spinner("Agent analyzing data and news..."):
        agent = SRAGAgent()
        report = agent.generate_report()
        
        # Display insights
        st.markdown(report['analysis'])
        
        # Display news
        render_news_context(report['news'])
```

---

### Header Component (components/header.py)
```python
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
```

---

### Metrics Cards (components/metrics_cards.py)
```python
import streamlit as st

def render_metrics(metrics: dict):
    """
    Renders 4 KPI cards in a row
    
    Args:
        metrics: Dict with keys: case_growth, mortality, icu, vaccination
    """
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Card 1: Case Growth Rate
    with col1:
        delta_color = "inverse" if metrics['case_growth']['value'] > 0 else "normal"
        st.metric(
            label="📈 Case Growth Rate",
            value=f"{metrics['case_growth']['value']:+.1f}%",
            delta=f"{metrics['case_growth']['vs_previous']:+.1f}% vs previous period",
            delta_color=delta_color
        )
        st.caption(f"Last 30 days: {metrics['case_growth']['absolute']:,} cases")
    
    # Card 2: Mortality Rate
    with col2:
        st.metric(
            label="💀 Mortality Rate",
            value=f"{metrics['mortality']['rate']:.1f}%",
            delta=f"{metrics['mortality']['change']:+.1f}% vs previous",
            delta_color="inverse"
        )
        st.caption(f"Deaths: {metrics['mortality']['deaths']:,}")
    
    # Card 3: ICU Occupancy
    with col3:
        st.metric(
            label="🏥 ICU Occupancy",
            value=f"{metrics['icu']['rate']:.1f}%",
            delta=f"{metrics['icu']['change']:+.1f}% vs previous",
            delta_color="inverse" if metrics['icu']['change'] > 0 else "normal"
        )
        st.caption(f"ICU cases: {metrics['icu']['total']:,}")
    
    # Card 4: Vaccination Rate
    with col4:
        st.metric(
            label="💉 Vaccination Coverage",
            value=f"{metrics['vaccination']['rate']:.1f}%",
            delta=f"{metrics['vaccination']['change']:+.1f}% vs previous",
            delta_color="normal"
        )
        st.caption(f"Vaccinated: {metrics['vaccination']['total']:,}")

def _get_trend_icon(value: float) -> str:
    """Returns emoji for trend"""
    if value > 5:
        return "📈"
    elif value < -5:
        return "📉"
    else:
        return "➡️"
```

---

### Charts Component (components/charts.py)
```python
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

def render_charts(chart_data: dict):
    """Renders tabbed chart interface"""
    
    tab1, tab2, tab3 = st.tabs([
        "📅 Last 30 Days", 
        "📆 Last 12 Months",
        "🗺️ Geographic Distribution"
    ])
    
    with tab1:
        render_daily_chart(chart_data['daily'])
    
    with tab2:
        render_monthly_chart(chart_data['monthly'])
    
    with tab3:
        render_geographic_chart(chart_data['geographic'])

def render_daily_chart(data):
    """Line chart: Daily cases (30 days)"""
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['dates'],
        y=data['cases'],
        mode='lines+markers',
        name='Daily Cases',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(31, 119, 180, 0.1)'
    ))
    
    # Add 7-day moving average
    fig.add_trace(go.Scatter(
        x=data['dates'],
        y=data['moving_avg_7d'],
        mode='lines',
        name='7-day Average',
        line=dict(color='#ff7f0e', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title="Daily SRAG Cases - Last 30 Days",
        xaxis_title="Date",
        yaxis_title="Number of Cases",
        hovermode='x unified',
        height=500,
        template='plotly_white',
        font=dict(size=12),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary stats below chart
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Peak Day", data['peak_date'], f"{data['peak_value']:,} cases")
    with col2:
        st.metric("Average", f"{data['avg']:.0f}", "cases/day")
    with col3:
        trend = "↗️ Increasing" if data['trend'] > 0 else "↘️ Decreasing"
        st.metric("Trend", trend, f"{abs(data['trend']):.1f}%")

def render_monthly_chart(data):
    """Bar chart: Monthly cases (12 months)"""
    
    fig = go.Figure()
    
    # Color bars based on trend
    colors = ['#d62728' if c > data['avg'] else '#1f77b4' 
              for c in data['cases']]
    
    fig.add_trace(go.Bar(
        x=data['months'],
        y=data['cases'],
        marker_color=colors,
        text=data['cases'],
        texttemplate='%{text:,}',
        textposition='outside',
        name='Monthly Cases'
    ))
    
    # Add average line
    fig.add_hline(
        y=data['avg'],
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Average: {data['avg']:,.0f}",
        annotation_position="right"
    )
    
    fig.update_layout(
        title="Monthly SRAG Cases - Last 12 Months",
        xaxis_title="Month",
        yaxis_title="Number of Cases",
        height=500,
        template='plotly_white',
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Seasonal analysis
    st.info(
        f"📊 **Seasonal Pattern:** "
        f"Highest month: {data['highest_month']} ({data['highest_value']:,} cases). "
        f"Lowest month: {data['lowest_month']} ({data['lowest_value']:,} cases)."
    )

def render_geographic_chart(data):
    """Choropleth map: Cases by state"""
    
    fig = px.choropleth(
        data,
        loc

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd

def render_charts(chart_data: dict):
    """Renders tabbed chart interface"""
    if not chart_data:
        st.warning("No data available for charts")
        return
    
    # Check if we have the necessary data
    if 'daily' not in chart_data or 'monthly' not in chart_data:
         st.error("Invalid chart data structure")
         return

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
        if 'geographic' in chart_data:
            render_geographic_chart(chart_data['geographic'])
        else:
            st.info("Geographic data unavailable")

def render_daily_chart(data):
    """Line chart: Daily cases (30 days)"""
    
    fig = go.Figure()
    
    # Raw Data
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
    if len(data['moving_avg_7d']) > 0:
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
        st.metric("Peak Day", str(data['peak_date']), f"{data['peak_value']:,} cases")
    with col2:
        st.metric("Average", f"{data['avg']:.0f}", "cases/day")
    with col3:
        trend_label = "↗️ Increasing" if data['trend'] > 0 else "↘️ Decreasing"
        st.metric("Trend", trend_label, f"{abs(data['trend']):.1f}%")

def render_monthly_chart(data):
    """Bar chart: Monthly cases (12 months)"""
    
    fig = go.Figure()
    
    if len(data.get('cases', [])) == 0:
        st.write("No monthly data available.")
        return

    # Color bars based on trend vs average
    avg_val = data.get('avg', 0)
    colors = ['#d62728' if c > avg_val else '#1f77b4' 
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
        y=avg_val,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Average: {avg_val:,.0f}",
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
        f"Highest month: {data.get('highest_month', '-')} ({data.get('highest_value', 0):,} cases). "
        f"Lowest month: {data.get('lowest_month', '-')} ({data.get('lowest_value', 0):,} cases)."
    )

def render_geographic_chart(data):
    """Choropleth map: Cases by state"""
    
    if data is None or data.empty:
        st.write("No geographic data available.")
        return
        
    # Using Plotly built-in support for Brazil states if available, or simple bar chart if GeoJSON not loaded
    # Since we don't have GeoJSON handy in this context, let's use a nice Bar Chart for States
    
    fig = px.bar(
        data, 
        x='state', 
        y='cases',
        title="Cases by State (UF)",
        labels={'cases': 'Total Cases', 'state': 'State'},
        color='cases',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        xaxis={'categoryorder':'total descending'},
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)

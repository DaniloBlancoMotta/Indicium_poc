
import streamlit as st

def render_metrics(metrics: dict):
    """
    Renders 4 KPI cards in a row
    
    Args:
        metrics: Dict returned by calculate_all_metrics including:
                 growth, mortality, icu, vaccination
    """
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Growth Rate
    with col1:
        growth = metrics.get('growth', {})
        st.metric(
            label="📈 Case Growth Rate",
            value=f"+{growth.get('growth_rate'):.1f}%",
            delta=f"{growth.get('growth_absolute'):+,} cases vs prior period",
            delta_color="off" # Simple trend color logic
        )
        st.caption(f"Last 30 days: {growth.get('current_period_cases', 0):,} cases")
        
    # Mortality Rate
    with col2:
        mortality = metrics.get('mortality', {})
        st.metric(
            label="💀 Mortality Rate",
            value=f"{mortality.get('mortality_rate'):.1f}%",
            delta=None
        )
        st.caption(f"Deaths: {mortality.get('deaths', 0):,}")
        
    # ICU Occupancy
    with col3:
        icu = metrics.get('icu', {})
        st.metric(
            label="🏥 ICU Occupancy",
            value=f"{icu.get('icu_rate'):.1f}%",
            delta=None
        )
        st.caption(f"ICU Cases: {icu.get('icu_cases', 0):,}")
    
    # Vaccination Rate
    with col4:
        vaccination = metrics.get('vaccination', {})
        st.metric(
            label="💉 Vaccination Coverage",
            value=f"{vaccination.get('vaccination_rate'):.1f}%",
            delta=None
        )
        st.caption(f"Vaccinated Cases: {vaccination.get('vaccinated', 0):,}")

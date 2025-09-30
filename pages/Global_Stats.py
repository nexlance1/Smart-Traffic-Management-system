
import streamlit as st
from utils import plot_metrics_image, aggregate_stats, read_state, compute_co2_savings
st.set_page_config(page_title='Global Stats', layout='wide')

# CSS for KPI cards
st.markdown("""
<style>
.kpi {background:linear-gradient(180deg,#0b2b3a,#091218);padding:12px;border-radius:10px;color:#e6eef8}
.big{font-size:20px;font-weight:700}
.small{color:#9fb4d6}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="kpi"><div style="display:flex;justify-content:space-between;align-items:center"><div><div class="big">Global Statistics</div><div class="small">Aggregated analytics across cameras</div></div></div></div>', unsafe_allow_html=True)

state = read_state()
st.markdown('---')
col1, col2, col3 = st.columns(3)
agg = aggregate_stats()
total_vehicles = int(agg['total_vehicles'].sum()) if agg is not None else 0
total_accidents = int(agg['accidents'].sum()) if agg is not None else 0
total_ambulances = int(agg['ambulances'].sum()) if agg is not None else 0

co2, liters, saved_seconds = compute_co2_savings(total_vehicles, per_vehicle_saved_seconds=20)
time_saved_hours = round(saved_seconds/3600,3)

col1.metric('Total vehicles (logged)', total_vehicles, delta=None)
col2.metric('Total accidents (logged)', total_accidents, delta=None)
col3.metric('Total ambulances (logged)', total_ambulances, delta=None)
st.markdown('---')
st.markdown(f"**Estimated CO2 saved (kg):** {co2}") 
st.markdown(f"**Estimated fuel saved (L):** {liters}")
st.markdown(f"**Estimated time saved (hrs):** {time_saved_hours}")
st.markdown('---')
st.markdown(f"**Signal switch count:** {state.get('switch_count',0)}")
st.markdown(f"**Current signal state:** N={state.get('N')} E={state.get('E')} S={state.get('S')} W={state.get('W')}")

img = plot_metrics_image()
if img is None:
    st.info('No metrics logged yet. Run camera pages to generate sample data.')
else:
    st.image(img, width='stretch')

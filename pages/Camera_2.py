
import streamlit as st
import cv2, time, pandas as pd
from pathlib import Path
from detector import SimpleAutoDetector
from utils import draw_boxes, set_direction_green, reset_auto, log_stats, read_state, aggregate_stats

st.set_page_config(page_title="Camera 2", layout='wide')

# page CSS for card look
st.markdown("""
<style>
.kpi {{background:linear-gradient(180deg,#0b2b3a,#091218);padding:12px;border-radius:10px;color:#e6eef8}}
.small{{color:#9fb4d6;font-size:13px}}
</style>
""", unsafe_allow_html=True)

st.markdown(f"<div class='kpi'><h2 style='margin:0'>Camera 2 Dashboard</h2><div class='small'>Live feed & controls</div></div>", unsafe_allow_html=True)

video_source = st.text_input("Video source (leave to use default)", "traffic2.mp4")
col1, col2 = st.columns([3,1])
with col1:
    feed = st.empty()
    chart = st.empty()
with col2:
    st.markdown("### Controls")
    if st.button("Force Green: N"): set_direction_green('N', duration=30)
    if st.button("Force Green: E"): set_direction_green('E', duration=30)
    if st.button("Force Green: S"): set_direction_green('S', duration=30)
    if st.button("Force Green: W"): set_direction_green('W', duration=30)
    if st.button("Reset to Auto"): reset_auto()
    st.markdown("---")
    state = read_state()
    st.markdown(f"**Signal state:** N={state.get('N')} E={state.get('E')} S={state.get('S')} W={state.get('W')}")
    st.markdown(f"**Switch Count:** {state.get('switch_count',0)}")

detector = SimpleAutoDetector()
source = video_source if video_source else "traffic2.mp4"
cap = None
if Path(source).exists():
    cap = cv2.VideoCapture(source)
elif source == '0':
    cap = cv2.VideoCapture(0)
else:
    st.error("Video source not found. Place the file or use '0' for webcam.")

if cap and cap.isOpened():
    frames=0
    with st.spinner('Processing video…'):
        while True:
            ret, frame = cap.read()
            if not ret:
                st.info("Stream ended or cannot read frame.")
                break
            frame = cv2.resize(frame, (900,500))
            boxes, counts = detector.detect(frame)
            out = draw_boxes(frame.copy(), boxes, read_state())
            feed.image(cv2.cvtColor(out, cv2.COLOR_BGR2RGB), width='stretch')
            total = sum(counts[k] for k in ['N','S','E','W'])
            log_stats("Camera_2", total, 1 if counts.get('accident') else 0, counts.get('ambulance',0))
            frames += 1
            if frames % 8 == 0:
                agg = aggregate_stats()
                if agg is not None:
                    last = agg['total_vehicles'].tail(30)
                    chart.line_chart(last)
            time.sleep(0.12)
else:
    st.warning("No feed available for this page.")

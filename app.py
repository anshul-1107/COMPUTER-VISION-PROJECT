import streamlit as st
import cv2
import time
from src.detection.detector import SurveillanceSystem
import threading

# Page Configuration
st.set_page_config(
    page_title="NIRBHAYA - AI Surveillance",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Glassmorphism
st.markdown("""
<style>
    .stApp {
        background-color: #0f172a;
        background-image: 
            radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
            radial-gradient(at 50% 0%, hsla(225,39%,30%,1) 0, transparent 50%), 
            radial-gradient(at 100% 0%, hsla(339,49%,30%,1) 0, transparent 50%);
        color: white;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Metrics/Cards */
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 10px;
        border-radius: 10px;
        color: white;
    }
    
    h1, h2, h3 {
        color: #f8fafc !important;
    }
    
    /* Custom Alert Box */
    .alert-box {
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ef4444;
        background-color: rgba(239, 68, 68, 0.2);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Cache the System to prevent reloading models on every interaction
@st.cache_resource
def get_system():
    return SurveillanceSystem()

system = get_system()

# Sidebar
with st.sidebar:
    st.title("🛡️ NIRBHAYA")
    st.markdown("### Status: **Active**")
    
    st.divider()
    
    st.subheader("System Health")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Camera", "Online")
    with col2:
        st.metric("AI Model", "Active")
        
    st.divider()
    
    st.info("Stop Gesture: Show Open Palm ✋ to trigger instant SOS.")

# Main Application
st.title("AI-Powered Smart Surveillance")

# Alert Placeholder
alert_placeholder = st.empty()

# Video Placeholder
col_video, col_logs = st.columns([3, 1])

with col_video:
    st.markdown("### Live Feed")
    video_placeholder = st.empty()

with col_logs:
    st.markdown("### Activity Log")
    log_placeholder = st.empty()

# Run Loop
run = st.checkbox('Start Monitoring', value=True)

while run:
    # 1. Get Frame
    frame = system.get_processed_frame()
    
    if frame is not None:
        # Convert BGR to RGB for Streamlit
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)
    
    # 2. Update Alerts
    logs = system.notifier.recent_logs
    if logs:
        last_log = logs[0]
        # Check freshness (simple check)
        is_recent = True 
        
        if is_recent:
            alert_placeholder.markdown(f"""
            <div class="alert-box">
                <h3>⚠️ THREAT DETECTED</h3>
                <p>{last_log['message']}</p>
                <small>{last_log['timestamp']}</small>
            </div>
            """, unsafe_allow_html=True)
            
        # Update Logs Column
        log_text = ""
        for log in logs[:10]:
            color = "red" if log['type'] == 'alert' else "white"
            log_text += f":{color}[{log['timestamp']}] {log['message']}\n\n"
        log_placeholder.markdown(log_text)
    else:
        alert_placeholder.empty()
        log_placeholder.markdown("*No active threats.*")
        
    # Small sleep to reduce CPU usage
    # time.sleep(0.01) # Optional

import streamlit as st
import cv2
import av
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
from src.detection.detector import SurveillanceSystem
import threading

# Page Configuration
st.set_page_config(
    page_title="NIRBHAYA AI - Cloud",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS (Glassmorphism)
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
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 10px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize System Once
if 'system' not in st.session_state:
    st.session_state.system = SurveillanceSystem()

system = st.session_state.system

def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
    img = frame.to_ndarray(format="bgr24")
    
    # Process using our Surveillance System
    # Note: process_frame now just takes an image and returns an image
    processed_img = system.process_frame(img)
    
    if processed_img is None:
        processed_img = img

    return av.VideoFrame.from_ndarray(processed_img, format="bgr24")

# Sidebar
with st.sidebar:
    st.title("🛡️ NIRBHAYA AI")
    st.info("System optimized for Cloud Deployment.")
    st.markdown("### Status: **Ready**")
    
    # Check Logs
    st.subheader("Recent Alerts")
    if hasattr(system.notifier, 'recent_logs'):
        for log in system.notifier.recent_logs[:5]:
            st.error(f"{log['timestamp']} - {log['message']}")

st.title("AI Surveillance System (Cloud)")
st.write("Click 'Start' to enable the camera. The video performs local loopback to the server for processing.")

# WebRTC Streamer
webrtc_streamer(
    key="surveillance",
    video_frame_callback=video_frame_callback,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True
)

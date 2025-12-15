# NIRBHAYA AI - Women's Safety Surveillance System

**NIRBHAYA AI** is an advanced computer vision project designed to enhance women's safety using real-time surveillance. It integrates:
- **Emotion Detection** (focusing on Fear/Distress)
- **Gender Recognition** (Verified "Woman Only" filtering)
- **Gesture Recognition** (Silent "Open Palm" SOS trigger)
- **Instant Alerts** via Twilio (SMS/Call) to authorities and guardians.

## Features
- 🚀 **Real-time Monitoring** via Premium Streamlit Dashboard.
- 👁️ **Smart AI** that filters false positives by checking for Gender + Emotion context.
- ✋ **Silent SOS** using MediaPipe Hand Gesture recognition.
- 📱 **cloud-native alerts** using Twilio API.

## Installation
1. Clone the repo.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your `.env` file with Twilio credentials.
4. Run the app:
   ```bash
   streamlit run app.py
   ```

## Tech Stack
- Python 3.12
- OpenCV, DeepFace, MediaPipe
- Streamlit
- Twilio

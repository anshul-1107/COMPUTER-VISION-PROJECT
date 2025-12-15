import cv2
import threading
from deepface import DeepFace
from src.alert.notifier import Notifier
from src.detection.gesture import GestureDetector
from src.detection.motion import MotionDetector
import numpy as np

class SurveillanceSystem:
    def __init__(self):
        # Camera is now handled by WebRTC in the frontend
        # We just initialize detectors and state
             
        self.notifier = Notifier()
        self.gesture_detector = GestureDetector()
        self.motion_detector = MotionDetector()
        self.lock = threading.Lock()
        
        # Detection State
        self.frame_count = 0
        self.skip_frames = 5 # Process AI every 5 frames
        self.last_emotions = [] # Cache results
        
        # Threat emotions - User requested ONLY 'fear' context
        self.threat_emotions = ['fear'] 

    def process_frame(self, frame):
        """
        Process a single frame from any source (WebRTC or Local)
        """
        self.frame_count += 1
        
        # 1. Gesture Detection (Fast - Every Frame)
        frame, gesture = self.gesture_detector.detect_gesture(frame)
        if gesture:
            self.notifier.alert(gesture, alert_type="GESTURE (SOS)")
            cv2.putText(frame, f"SOS TRIGGER: {gesture}", (50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

        # 2. Motion/Running Detection (Fast - Every Frame)
        motion_status, landmarks = self.motion_detector.detect_distress(frame)
        if motion_status:
            color = (0, 0, 255)
            cv2.putText(frame, f"ALERT: {motion_status}", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 3)
            self.notifier.alert("Target Fleeing (High Speed Run)", alert_type="MOTION")

        # 3. Emotion Analysis (Slow - Every Nth Frame)
        if self.frame_count % self.skip_frames == 0:
            try:
                # Run DeepFace on small resize for speed
                small_frame = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
                
                # Added 'gender' to actions to filter for women's safety as requested
                self.last_emotions = DeepFace.analyze(small_frame, 
                                        actions = ['emotion', 'gender'],
                                        enforce_detection=False,
                                        silent=True)
            except Exception:
                self.last_emotions = []

        # Draw Cached Emotions (Maintain boxes even on skipped frames)
        for obj in self.last_emotions:
            # Scale coordinates back up (since we detected on 0.5x)
            scale = 2 
            x = int(obj['region']['x'] * scale)
            y = int(obj['region']['y'] * scale)
            w = int(obj['region']['w'] * scale)
            h = int(obj['region']['h'] * scale)
            
            dominant_emotion = obj['dominant_emotion']
            gender = obj['dominant_gender'] # 'Man' or 'Woman'
            
            color = (0, 255, 0) # Green (Safe)
            
            # Logic: Alert ONLY if Fear is detected on a Woman
            if dominant_emotion in self.threat_emotions and gender == 'Woman':
                threat_label = f"{dominant_emotion.upper()} (Woman Targeted)"
                color = (0, 0, 255) # Red (Threat)
                self.notifier.alert(threat_label, alert_type="THREAT")
            
            # Visuals
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            
            # Display Emotion and Gender
            label = f"{dominant_emotion} ({gender})"
            cv2.putText(frame, label, (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        return frame

    def __del__(self):
        if self.camera.isOpened():
            self.camera.release()

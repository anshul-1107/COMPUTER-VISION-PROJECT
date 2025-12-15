import cv2
import threading
from deepface import DeepFace
from src.alert.notifier import Notifier
from src.detection.gesture import GestureDetector
import numpy as np

class SurveillanceSystem:
    def __init__(self):
        # Open camera (try 0, then 1 if 0 fails)
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
             self.camera = cv2.VideoCapture(1)
             
        self.notifier = Notifier()
        self.gesture_detector = GestureDetector()
        self.lock = threading.Lock()
        
        # Threat emotions - User requested ONLY 'fear' context
        self.threat_emotions = ['fear'] 
        
    def get_processed_frame(self):
        success, frame = self.camera.read()
        if not success:
            return None
        
        # 1. Gesture Detection (Fast, MediaPipe)
        frame, gesture = self.gesture_detector.detect_gesture(frame)
        if gesture:
            self.notifier.alert(gesture, alert_type="GESTURE (SOS)")
            cv2.putText(frame, f"SOS TRIGGER: {gesture}", (50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

        # 2. Emotion Analysis (Slower, DeepFace)
        try:
            # Added 'gender' to actions to filter for women's safety as requested
            objs = DeepFace.analyze(frame, 
                                    actions = ['emotion', 'gender'],
                                    enforce_detection=False,
                                    silent=True)
            
            for obj in objs:
                x = obj['region']['x']
                y = obj['region']['y']
                w = obj['region']['w']
                h = obj['region']['h']
                
                dominant_emotion = obj['dominant_emotion']
                gender = obj['dominant_gender'] # 'Man' or 'Woman'
                
                color = (0, 255, 0) # Green (Safe)
                
                # Logic: Alert ONLY if Fear is detected on a Woman
                # Strict mode enabled as per user request
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
                            
        except Exception as e:
            # print(f"Error in analysis: {e}")
            pass

        return frame

    def get_frame(self):
        frame = self.get_processed_frame()
        if frame is None:
            return None
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def __del__(self):
        if self.camera.isOpened():
            self.camera.release()

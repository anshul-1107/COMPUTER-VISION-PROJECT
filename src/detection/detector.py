import cv2
import threading
import time
import numpy as np
import mediapipe as mp
from deepface import DeepFace
from src.alert.notifier import Notifier
from src.detection.motion import MotionDetector

class SurveillanceSystem:
    def __init__(self):
        self.notifier = Notifier()
        self.motion_detector = MotionDetector()
        
        # MediaPipe Holistic (Face + Hands + Pose) - The "Cyberpunk" Backbone
        self.mp_holistic = mp.solutions.holistic
        self.holistic = self.mp_holistic.Holistic(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=1
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Threading State
        self.lock = threading.Lock()
        self.latest_frame = None
        self.keep_running = True
        
        # Inference Results (Shared Data)
        self.current_emotion = "Scanning..."
        self.current_gender = "Unknown"
        self.is_threat = False
        self.last_inference_time = 0
        
        # Start Background Inference Thread
        self.thread = threading.Thread(target=self._inference_loop, daemon=True)
        self.thread.start()

    def _inference_loop(self):
        """
        Daemon thread that runs DeepFace only when a new frame is available.
        Decouples AI speed from Camera speed.
        """
        while self.keep_running:
            if self.latest_frame is not None:
                with self.lock:
                    frame_copy = self.latest_frame.copy()
                    self.latest_frame = None # Consume it
                
                try:
                    # DeepFace Analysis
                    # Using 'VGG-Face' or default. Enforce_detection=False handles "No Face" gracefully
                    objs = DeepFace.analyze(
                        img_path=frame_copy, 
                        actions=['emotion', 'gender'],
                        enforce_detection=False,
                        detector_backend='opencv', # Fast backend
                        silent=True
                    )
                    
                    if objs:
                        # Take the largest face
                        obj = objs[0]
                        self.current_emotion = obj['dominant_emotion']
                        self.current_gender = obj['dominant_gender']
                        
                        # Threat Logic: Fear + Woman
                        if self.current_emotion == 'fear' and self.current_gender == 'Woman':
                            self.is_threat = True
                            self.notifier.alert("WOMAN IN DISTRESS (FEAR)", "THREAT")
                        else:
                            self.is_threat = False
                            
                except Exception as e:
                    pass
                    # print(f"Inference Error: {e}")
            
            time.sleep(0.1) # Prevent CPU spin (Max 10 FPS for Emotion is enough)

    def process_frame(self, frame):
        """
        Main Pipeline:
        1. MediaPipe Holistic (Fast, runs every frame)
        2. Motion Analysis (Fast, runs every frame)
        3. HUD Drawing
        4. Sends frame to background thread for Emotion Analysis
        """
        # 1. Update Background Thread
        with self.lock:
            self.latest_frame = frame.copy()
            
        # 2. MediaPipe Processing
        # Convert to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = self.holistic.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # 3. Motion Detection
        is_running = False
        velocity = 0.0
        if results.pose_landmarks:
            is_running, velocity, angle = self.motion_detector.detect(results.pose_landmarks.landmark)
            
            if is_running:
                # Context Check: Running + Fear = FLEEING
                context_label = "RUNNING"
                if self.is_threat: #(Fear detected)
                    context_label = "FLEEING (DANGER)"
                    self.notifier.alert("Subject Fleeing in Distress", "CRITICAL")
                
                # Draw Alert
                cv2.putText(image, f"⚠️ {context_label} (Vel: {velocity:.2f})", (50, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        # 4. Gesture Detection (SOS) via Hands
        # Check for Open Palm (Simple Logic with hand landmarks)
        if results.left_hand_landmarks or results.right_hand_landmarks:
            # We assume open palm if multiple landmarks are visible extended
            # For simplicity, if hand is raised near face or simply visible clearly
            # We can rely on the Pose context or just flag "Hand Detected"
            pass
            # (Keeping it simple to avoid clutter: Holistic handles the visual)

        # ==========================================================
        # CYBERPUNK HUD DRAWING
        # ==========================================================
        
        h, w, c = image.shape
        overlay = image.copy()
        
        # A. Draw Mesh/Skeleton (The "Iron Man" look)
        # Face Mesh
        # self.mp_drawing.draw_landmarks(
        #     image, results.face_landmarks, self.mp_holistic.FACEMESH_TESSELATION,
        #     landmark_drawing_spec=None,
        #     connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_tesselation_style())
        
        # Pose Skeleton (Green/Red based on Threat)
        skel_color = (0, 255, 0) if not self.is_threat else (0, 0, 255)
        self.mp_drawing.draw_landmarks(
            image, results.pose_landmarks, self.mp_holistic.POSE_CONNECTIONS,
            landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=skel_color, thickness=2, circle_radius=2),
            connection_drawing_spec=self.mp_drawing.DrawingSpec(color=skel_color, thickness=2))
            
        # B. Status Box (Top Right)
        # Transparent Background
        cv2.rectangle(overlay, (w-250, 0), (w, 150), (10, 10, 10), -1)
        
        # Dynamic Text
        emo_color = (0, 255, 255) # Yellow
        if self.is_threat: emo_color = (0, 0, 255) # Red
        
        cv2.putText(overlay, "STATUS: ONLINE", (w-230, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        cv2.putText(overlay, f"EMOTION: {self.current_emotion.upper()}", (w-230, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, emo_color, 2)
        cv2.putText(overlay, f"GENDER:  {self.current_gender.upper()}", (w-230, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(overlay, f"VELOCITY: {velocity:.2f}", (w-230, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        # C. Warning Banner (If Threat)
        if self.is_threat or is_running:
            cv2.rectangle(overlay, (0, h-50), (w, h), (0, 0, 255), -1)
            cv2.putText(overlay, "⚠️ THREAT DETECTED - ANALYSIS: ACTIVE", (w//2 - 200, h-15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Blend Overlay (Transparency)
        alpha = 0.6
        image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
        
        return image

    def __del__(self):
        self.keep_running = False

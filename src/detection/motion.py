import cv2
import mediapipe as mp
import math
import time

class MotionDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1, # 0=Fast, 1=Balanced, 2=Accurate
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Tracking state
        self.prev_hip_x = None
        self.prev_time = time.time()
        self.speed_threshold = 0.5 # Normalized coordinates per second (needs tuning)
        
    def detect_distress(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        
        status = None
        
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            # 1. Calculate Velocity (using Hip center)
            # Average of left (23) and right (24) hip
            current_hip_x = (landmarks[23].x + landmarks[24].x) / 2
            current_time = time.time()
            
            if self.prev_hip_x is not None:
                dt = current_time - self.prev_time
                if dt > 0:
                    dx = abs(current_hip_x - self.prev_hip_x)
                    speed = dx / dt
                    
                    # Check threshold (Simple heuristic)
                    if speed > self.speed_threshold:
                        # 2. Check Body Lean (Optional refinement)
                        # Nose (0) vs Mid-Hip
                        nose_x = landmarks[0].x
                        
                        # Forward lean detection (simple relative X check)
                        # If running fast, this usually triggers
                        status = "RUNNING (High Speed)"
            
            self.prev_hip_x = current_hip_x
            self.prev_time = current_time
            
        return status, results.pose_landmarks

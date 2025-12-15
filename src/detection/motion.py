import time
import math
import numpy as np

class MotionDetector:
    def __init__(self):
        self.prev_landmarks = None
        self.prev_time = time.time()
        # Thresholds
        self.RUNNING_THRESHOLD = 0.8 # Normalized distance per second
        self.LEAN_THRESHOLD = 60 # Degrees
        
    def detect(self, landmarks):
        """
        Input: MediaPipe Pose Landmarks
        Output: (is_running, velocity_score, lean_angle)
        """
        if not landmarks:
            return False, 0.0, 90.0
            
        current_time = time.time()
        dt = current_time - self.prev_time
        
        # Landmarks of interest (Hips)
        # 23: Left Hip, 24: Right Hip, 11: Left Shoulder, 12: Right Shoulder
        left_hip = landmarks[23]
        right_hip = landmarks[24]
        
        # Calculate Centroid of Body (Hips)
        cx = (left_hip.x + right_hip.x) / 2
        cy = (left_hip.y + right_hip.y) / 2
        
        velocity = 0.0
        
        if self.prev_landmarks and dt > 0:
            # Calculate displacement
            # We focus on Horizontal movement mainly for running across screen
            # But calculating Euclidean distance is safer
            prev_cx = self.prev_landmarks['cx']
            prev_cy = self.prev_landmarks['cy']
            
            dist = math.sqrt((cx - prev_cx)**2 + (cy - prev_cy)**2)
            velocity = dist / dt
        
        # Calculate Body Lean (Torso angle relative to vertical)
        # Mid-Shoulder
        sx = (landmarks[11].x + landmarks[12].x) / 2
        sy = (landmarks[11].y + landmarks[12].y) / 2
        
        # Vector from Hip to Shoulder
        dy = sy - cy
        dx = sx - cx
        
        # Angle in degrees (90 is upright, <60 is leaning forward)
        angle_rad = math.atan2(abs(dy), abs(dx))
        angle_deg = math.degrees(angle_rad)
        
        # Update State
        self.prev_landmarks = {'cx': cx, 'cy': cy}
        self.prev_time = current_time
        
        is_running = velocity > self.RUNNING_THRESHOLD
        
        return is_running, velocity, angle_deg

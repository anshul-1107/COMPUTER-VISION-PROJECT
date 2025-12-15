import cv2
import mediapipe as mp

class GestureDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils

    def detect_gesture(self, frame):
        """
        Detects hand gestures in the frame.
        Returns: 
            frame: with landmarks drawn
            gesture: detected gesture name (e.g., 'STOP', 'SOS') or None
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        
        detected_gesture = None

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                # Check for "Open Palm" / "Stop" gesture
                # Logic: All fingers extended
                if self._is_hand_open(hand_landmarks):
                    detected_gesture = 'STOP_SOS'
                    
        return frame, detected_gesture

    def _is_hand_open(self, landmarks):
        # MediaPipe landmark indices:
        # 0: Wrist
        # 4: Thumb tip, 8: Index tip, 12: Middle tip, 16: Ring tip, 20: Pinky tip
        # 2, 6, 10, 14, 18: PIP joints (knuckles roughly)
        
        # Simple heuristic: Tip y < PIP y (assuming hand is upright)
        # Note: Coordinates are normalized [0,1], (0,0) is top-left.
        # So "up" means lower Y value.
        
        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]
        
        extended_fingers = 0
        for tip, pip in zip(tips, pips):
            if landmarks.landmark[tip].y < landmarks.landmark[pip].y:
                extended_fingers += 1
                
        # Thumb check (x-axis for right/left hand distinction is complex, 
        # but simple check: thumb tip relative to IP joint)
        # For simplicity, if 4 out of 4 main fingers are up, we call it Open Palm/Stop
        
        return extended_fingers >= 4

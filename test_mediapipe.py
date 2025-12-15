import mediapipe as mp
import numpy as np
import cv2

print("Importing MediaPipe...")
try:
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.5)
    
    print("MediaPipe Initialized.")
    
    # Create dummy image
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    
    print("Processing Frame...")
    results = hands.process(img)
    print("Processing Complete.")
    print("MediaPipe works with current Protobuf version!")
    
except Exception as e:
    print(f"MediaPipe Failed: {e}")

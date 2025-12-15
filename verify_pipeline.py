import cv2
import numpy as np
import os
from src.detection.detector import SurveillanceSystem

# Mock camera
class MockCamera:
    def __init__(self, image_path):
        # Create a black image (synthetic)
        self.frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Draw a white rectangle to make it non-empty
        cv2.rectangle(self.frame, (100, 100), (300, 300), (255, 255, 255), -1)

    def read(self):
        return True, self.frame.copy()

    def release(self):
        pass
    
    def isOpened(self):
        return True

def test_pipeline():
    print("Initializing system...")
    try:
        system = SurveillanceSystem()
        
        # Monkeypatch camera
        print("Mocking camera with test_face.jpg...")
        system.camera.release() # Release real camera if any
        system.camera = MockCamera('test_face.jpg')
        
        print("Processing frame...")
        # First run might be slow due to model loading
        jpeg_bytes = system.get_frame()
        
        if jpeg_bytes and len(jpeg_bytes) > 0:
            print("SUCCESS: Frame processed and returned JPEG bytes.")
        else:
            print("FAILURE: No frame returned.")
            
        print("Test completed.")
        
    except Exception as e:
        print(f"FAILURE WITH ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if not os.path.exists('test_face.jpg'):
        print("Error: test_face.jpg not found.")
    else:
        test_pipeline()

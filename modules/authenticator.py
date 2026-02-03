
import cv2
import mediapipe as mp
import os
import numpy as np

class Authenticator:
    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(min_detection_confidence=0.5)
        self.reference_image_path = os.path.join(os.path.dirname(__file__), "..", "reference.jpg")
        
    def authenticate(self):
        """
        Captures an image and verifies if a face is present.
        (Simplified version: just checks for face presence. 
         Full recognition requires 'face_recognition' lib or MediaPipe embeddings)
        """
        cap = cv2.VideoCapture(0)
        authorized = False
        message = "No face detected."
        
        start_time = os.times().elapsed
        while (os.times().elapsed - start_time) < 5: # 5 second timeout
            success, image = cap.read()
            if not success:
                message = "Camera failed."
                break
                
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.face_detection.process(image_rgb)
            
            if results.detections:
                # Face Detected
                authorized = True
                message = "Face Authenticated."
                break
                
        cap.release()
        return authorized, message

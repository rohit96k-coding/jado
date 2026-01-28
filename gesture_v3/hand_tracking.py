import cv2
import mediapipe as mp
import time
import numpy as np
from config import Config

class HandDetector:
    def __init__(self, mode=False, maxHands=Config.MAX_HANDS, detectionCon=Config.DETECTION_CONFIDENCE, trackCon=Config.TRACKING_CONFIDENCE):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        
        # New Tasks API Setup
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode
        
        # Determine path to model
        model_path = 'gesture_v3/hand_landmarker.task'
        
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.VIDEO, # optimized for video stream
            num_hands=self.maxHands,
            min_hand_detection_confidence=self.detectionCon,
            min_hand_presence_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        
        self.landmarker = HandLandmarker.create_from_options(options)
        self.timestamp_ms = 0
        
        # Manual Connections for Drawing
        self.HAND_CONNECTIONS = [
            (0, 1), (1, 2), (2, 3), (3, 4),      # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),      # Index
            (5, 9), (9, 10), (10, 11), (11, 12), # Middle
            (9, 13), (13, 14), (14, 15), (15, 16), # Ring
            (13, 17), (17, 18), (18, 19), (19, 20), # Pinky
            (0, 17) # Palm Base
        ]

    def find_hands(self, img, draw=True):
        """Processes the image and detects hands."""
        # MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        
        # Increment timestamp (required for VIDEO mode)
        self.timestamp_ms += int(1000/Config.FPS) # Approx
        
        # Detect
        self.results = self.landmarker.detect_for_video(mp_image, self.timestamp_ms)
        
        if self.results.hand_landmarks:
            for handLines in self.results.hand_landmarks:
                if draw:
                    self.draw_manual_landmarks(img, handLines)
        return img
        
    def draw_manual_landmarks(self, img, landmarks):
        """Draws links and points manually."""
        h, w, c = img.shape
        # Convert Normalized Landmarks to Pixels
        points = []
        for lm in landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            points.append((cx, cy))
            
        # Draw Lines
        for p1, p2 in self.HAND_CONNECTIONS:
            cv2.line(img, points[p1], points[p2], (255, 255, 255), 2)
            
        # Draw Points
        for cx, cy in points:
             cv2.circle(img, (cx, cy), 4, (0, 0, 255), cv2.FILLED)

    def find_position(self, img, handNo=0, draw=True):
        """Returns a list of landmarks [id, x, y] for a specific hand."""
        self.lmList = []
        if self.results.hand_landmarks:
            try:
                myHand = self.results.hand_landmarks[handNo]
                h, w, c = img.shape
                for id, lm in enumerate(myHand):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    self.lmList.append([id, cx, cy])
                    if draw:
                        cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
            except:
                pass 
        return self.lmList

    # fingers_up and find_distance remain mostly the same logic-wise
    # But I need to include them here for completeness
    
    def fingers_up(self):
        fingers = []
        if len(self.lmList) == 0:
            return fingers
            
        # Tips IDs: 4, 8, 12, 16, 20
        # Thumb (Simple X check) 
        # Note: 'Right' hand in camera view (mirrored) means Thumb is to the LEFT of index base (5)?
        # Actually in mirrored view:
        # User Right Hand -> Shows on Right Side of Screen? No, Left Side if mirrored.
        # Let's stick to the relative check: Tip (4) vs Joint (3)
        
        # Assuming Right Hand (User's Right)
        if self.lmList[4][1] > self.lmList[3][1]: # X check
             fingers.append(1)
        else:
             fingers.append(0)

        # 4 Fingers (Y check)
        tips = [8, 12, 16, 20]
        for id in tips:
            if self.lmList[id][2] < self.lmList[id - 2][2]: # Up is smaller Y
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

import cv2

class Config:
    # Camera Settings
    CAM_ID = 0
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
    FPS = 30
    
    # Hand Tracking
    MAX_HANDS = 1
    DETECTION_CONFIDENCE = 0.5 # Lowered for better detection in low light
    TRACKING_CONFIDENCE = 0.5
    
    # Mouse Control
    SMOOTHING_FACTOR = 5 # Higher = smoother but more lag (3-7 is good)
    MOUSE_SENSITIVITY = 1.0 # Multiplier for cursor movement
    
    # Interaction Area (Virtual Screen on Frame)
    # Reduces the active area to allow reaching corners easily
    FRAME_REDUCTION = 100 # Pixels reduced from edges
    
    # Gesture Thresholds (Finger distance checks)
    CLICK_THRESHOLD = 30 # Distance between index and thumb for click
    SCROLL_THRESHOLD = 30 
    
    # Colors
    COLOR_MOUSE_POINTER = (255, 0, 255) # Magenta
    COLOR_CLICK = (0, 255, 0) # Green
    COLOR_NEUTRAL = (255, 0, 0) # Blue
    
    # Text
    FONT = cv2.FONT_HERSHEY_SIMPLEX

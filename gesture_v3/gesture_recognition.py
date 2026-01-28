import cv2
import time
import math
import numpy as np
from config import Config
from mouse_control import MouseController

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
except ImportError:
    pass # Mac/Linux fallback or if not installed

class GestureController:
    def __init__(self):
        self.mouse = MouseController()
        self.mode = "Cursor" # Cursor, Scroll, Volume
        self.last_click_time = 0
        self.click_cooldown = 0.5
        
        # Audio Init (Windows)
        self.volume_ctrl = None
        self.min_vol = -65.0
        self.max_vol = 0.0
        
        try:
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from comtypes import CLSCTX_ALL
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume_ctrl = interface.QueryInterface(IAudioEndpointVolume)
            self.vol_range = self.volume_ctrl.GetVolumeRange() # (-65, 0)
            self.min_vol, self.max_vol = self.vol_range[0], self.vol_range[1]
            print("Audio Control Initialized Successfully")
        except Exception as e:
            print(f"Audio Control Unavailable (Continuing without it): {e}")
            self.volume_ctrl = None

    def process_gestures(self, img, lmList):
        """
        Interprets hand landmarks for SAMi V3 Gestures.
        """
        if len(lmList) == 0:
             return img, "No Hand"

        # 1. Get Coordinates
        x1, y1 = lmList[8][1:]   # Index Tip
        x2, y2 = lmList[12][1:]  # Middle Tip
        x0, y0 = lmList[4][1:]   # Thumb Tip
        
        # 2. Check Fingers Up
        fingers = []
        # Thumb (4), Index (8), Middle (12), Ring (16), Pinky (20)
        # Using simple Y-check for non-thumb fingers, and relative X for thumb (assuming right hand usually)
        
        # Thumb Logic (Assuming Right Hand for Simplicity, can be improved)
        # Check if thumb tip is to the left/right of knuckle depending on hand
        # For robustness, let's checking if thumb is extended away from palm center could be better,
        # but stick to previous simple logic:
        # Assuming Right Hand: Thumb is 'Up'/Open if x < x_knuckle (if palm faces screen)
        # Let's use a simpler heuristic: Distance from Index Base (5)
        # Or just stick to the generic check implemented in hand_tracking which returns 0/1
        
        # We need to access fingers_up from detector, but here we only have lmList.
        # We will re-implement simple check here or pass it in. 
        # Re-implementing typical check:
        
        # Thumb (Check X diff)
        if lmList[4][1] > lmList[3][1]: # Right Hand: Tip > Joint = Open
             fingers.append(1)
        else:
             fingers.append(0)
             
        # 4 Fingers (Check Y diff)
        for id in [8, 12, 16, 20]:
            if lmList[id][2] < lmList[id-2][2]: # Up
                fingers.append(1)
            else:
                fingers.append(0)
                
        # fingers is [Thumb, Index, Middle, Ring, Pinky]
        
        gesture_name = "Neutral"
        
        # --- GESTURE: PAUSE (Fist) ---
        # All fingers down (0, 0, 0, 0, 0) or maybe thumb doesn't matter much (0, 0, 0, 0)
        if all(f == 0 for f in fingers[1:]): # Index to Pinky closed
            gesture_name = "PAUSED (Fist)"
            cv2.putText(img, "PAUSED", (200, 200), Config.FONT, 2, (0, 0, 255), 3)
            return img, gesture_name

        # --- GESTURE: MOVE CURSOR (Index Only) ---
        # Thumb can be active or not, key is Index UP, Middle DOWN
        if fingers[1] == 1 and fingers[2] == 0:
            gesture_name = "MOVE"
            cv2.rectangle(img, (Config.FRAME_REDUCTION, Config.FRAME_REDUCTION), 
                          (Config.FRAME_WIDTH - Config.FRAME_REDUCTION, Config.FRAME_HEIGHT - Config.FRAME_REDUCTION),
                          (255, 0, 255), 2)
            self.mouse.move_mouse(x1, y1, Config.FRAME_WIDTH, Config.FRAME_HEIGHT)

        # --- GESTURE: SCROLL (Index + Middle UP) ---
        elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:
            gesture_name = "SCROLL"
            # Map Y position to Scroll
            # Up (small y) -> Scroll Up, Down -> Scroll Down
            # Let's define a deadzone in middle?
            # Or simpler: Move hand UP relative to center = Scroll UP
            
            # Use relative movement?
            # Simple Scroll:
            # If y1 < Height/2 - 50 -> Scroll Up
            # If y1 > Height/2 + 50 -> Scroll Down
            
            h = Config.FRAME_HEIGHT
            if y1 < h // 3:
                self.mouse.scroll(20) # Up
                cv2.putText(img, "UP", (x1, y1-20), Config.FONT, 1, (0, 255, 0), 2)
            elif y1 > 2 * h // 3:
                self.mouse.scroll(-20) # Down
                cv2.putText(img, "DOWN", (x1, y1+20), Config.FONT, 1, (0, 255, 0), 2)

        # --- GESTURE: CLICK (Thumb + Index Pinch) ---
        # Index Logic: fingers[1] is 1... wait, for pinch, index tip is close to thumb tip.
        # They might be "down" slightly but main thing is distance.
        # Let's check distance between 4 and 8.
        dist_click = math.hypot(x1 - x0, y1 - y0)
        
        # --- GESTURE: RIGHT CLICK (Thumb + Middle Pinch) ---
        dist_right = math.hypot(x2 - x0, y2 - y0)
        
        if dist_click < 40 and fingers[2] == 0: # Index Pinch (Ensure Middle is not involved)
            gesture_name = "LEFT CLICK"
            cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
            if time.time() - self.last_click_time > self.click_cooldown:
                self.mouse.click('left')
                self.last_click_time = time.time()
                
        elif dist_right < 40: # Middle Pinch
            gesture_name = "RIGHT CLICK"
            cv2.circle(img, (x2, y2), 15, (0, 0, 255), cv2.FILLED)
            if time.time() - self.last_click_time > self.click_cooldown:
                self.mouse.click('right')
                self.last_click_time = time.time()

        return img, gesture_name

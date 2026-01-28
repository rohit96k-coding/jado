import pyautogui
import numpy as np
import time
from config import Config

class MouseController:
    def __init__(self):
        pyautogui.FAILSAFE = False # Prevent errors when touching corners
        self.screenWidth, self.screenHeight = pyautogui.size()
        self.frameR = Config.FRAME_REDUCTION
        
        # Smoothing Variables
        self.plocX, self.plocY = 0, 0 # Previous Location
        self.clocX, self.clocY = 0, 0 # Current Location
        self.smooth = Config.SMOOTHING_FACTOR

    def move_mouse(self, x_finger, y_finger, frame_width, frame_height):
        """
        Maps hand coordinates to screen coordinates with smoothing.
        x_finger, y_finger: Raw coordinates from webcam frame.
        """
        # 1. Convert Coordinates (Interpolation)
        # Map range [frameR, frameWidth-frameR] -> [0, screenWidth]
        x3 = np.interp(x_finger, (self.frameR, frame_width - self.frameR), (0, self.screenWidth))
        y3 = np.interp(y_finger, (self.frameR, frame_height - self.frameR), (0, self.screenHeight))
        
        # 2. Smooth Values
        self.clocX = self.plocX + (x3 - self.plocX) / self.smooth
        self.clocY = self.plocY + (y3 - self.plocY) / self.smooth
        
        # 3. Move Mouse
        try:
            pyautogui.moveTo(self.screenWidth - self.clocX, self.clocY) # Flip X for mirror effect
        except:
             pass # Ignore boundary errors
             
        self.plocX, self.plocY = self.clocX, self.clocY # Update Previous
        
    def click(self, button='left'):
        pyautogui.click(button=button)
        
    def double_click(self):
        pyautogui.doubleClick()
        
    def right_click(self):
        pyautogui.rightClick()
        
    def scroll(self, amount):
        pyautogui.scroll(amount)
        
    def drag_start(self):
        pyautogui.mouseDown()
        
    def drag_end(self):
        pyautogui.mouseUp()

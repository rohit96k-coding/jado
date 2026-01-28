import cv2
import time
from config import Config
from hand_tracking import HandDetector
from gesture_recognition import GestureController

def main():
    # 1. Initialize Camera
    cap = cv2.VideoCapture(Config.CAM_ID)
    cap.set(3, Config.FRAME_WIDTH)
    cap.set(4, Config.FRAME_HEIGHT)
    
    # 2. Initialize Detectors
    detector = HandDetector()
    controller = GestureController()
    
    pTime = 0
    
    print("Starting SAMi Gesture Control... Press 'q' to exit.")
    
    while True:
        # 3. Read Frame
        success, img = cap.read()
        if not success:
            print("Failed to read camera.")
            break
            
        # Flip image horizontally for mirror view (easier for user)
        img = cv2.flip(img, 1) 
        
        # 4. Detect Hands
        img = detector.find_hands(img)
        lmList = detector.find_position(img, draw=False)
        
        # 5. Process Gestures
        status = "IDLE"
        if len(lmList) != 0:
            img, status = controller.process_gestures(img, lmList)
            
        # 6. UI / HUD
        # Box for Stats
        cv2.rectangle(img, (0, 0), (250, 80), (0, 0, 0), cv2.FILLED)
        cv2.rectangle(img, (0, 0), (250, 80), (255, 0, 255), 2)
        
        # Calculate FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
        pTime = cTime
        
        # Text Info
        cv2.putText(img, f"System: SAMi V3", (10, 25), Config.FONT, 0.7, (0, 255, 255), 2)
        cv2.putText(img, f"Status: {status}", (10, 50), Config.FONT, 0.6, (0, 255, 0), 2)
        cv2.putText(img, f"FPS: {int(fps)}", (160, 25), Config.FONT, 0.7, (255, 255, 255), 2)
        
        # 7. Show Application
        cv2.imshow("SAMi Vision - Gesture Interface", img)
        
        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

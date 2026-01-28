# Hand Gesture Control System - Project Report

## 1. Project Overview
This project enables users to control their PC mouse cursor, click, scroll, and adjust volume using real-time hand gestures captured via a webcam. It uses **Computer Vision (OpenCV)** and **AI (MediaPipe)** to track hand landmarks and map them to system actions.

## 2. Technical Stack
- **Language:** Python 3.8+
- **Core Libraries:**
    - `opencv-python`: For video capture and image processing.
    - `mediapipe`: For robust, real-time hand tracking (AI).
    - `pyautogui`: For controlling the mouse and keyboard system-wide.
    - `numpy`: For mathematical operations and interpolation (smoothing).
    - `pycaw`: For Windows system volume control.

## 3. How It Works (Step-by-Step)
1.  **Capture:** The webcam captures video frames in real-time.
2.  **Detection:** MediaPipe processes each frame to find the hand and identifies **21 distinct landmarks** (joints and tips).
3.  **Logic (Gesture Recognition):**
    - The system checks which fingers are "Up" or "Down".
    - It calculates distances between specific fingers (e.g., Index and Thumb).
4.  **Action:**
    - **Move:** If only the *Index Finger* is up, the system maps the finger's position to screen coordinates.
    - **Click:** If the *Index and Middle Fingers* are up and brought close together, a "Left Click" is triggered.
    - **Volume:** If the *Thumb and Index Finger* are pinched (while others are down/neutral), the distance controls the system volume.
5.  **Smoothing:** To prevent shaky cursor movement, we interpolate between current and previous positions using a smoothing factor.

## 4. Gesture Mapping
| Gesture | Fingers Condition | Action |
| :--- | :--- | :--- |
| **Move Cursor** | Index Finger Only (Up) | Moves mouse pointer. |
| **Left Click** | Index + Middle (Up) & Tips Close (<30px) | Performs a single left click. |
| **Volume Control** | Thumb + Index (Pinch) | Adjusts Volume (Pinch Out = Up, In = Down). |
| **Neutral/Stop** | All 5 Fingers Up (Open Palm) | No action (stops cursor). |

## 5. How to Run
1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the App:**
    ```bash
    python main.py
    ```
3.  **Exit:** Press `q` to close the application.

## 6. Optimization & Features
- **FPS Optimization:** We calculate FPS (Frames Per Second) and display it. The code is optimized by processing logic only when a hand is detected.
- **Smoothing:** A `SMOOTHING_FACTOR` in `config.py` reduces jitter.
- **Robustness:** Handles missing hands gracefully and uses a "Virtual Frame" to ensure you can reach screen corners comfortably.

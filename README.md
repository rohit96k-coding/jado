# 🤖 SAMi Voice Assistant

## 🚀 How to Run

You need to run **two terminals** simultaneously:

### 1. Start the Brain (Backend)
This runs the AI, voice processing, and connects to your PC.
```powershell
cd "c:\Users\sagar\my project\jado"
python main.py
```
*Wait until you see "MOBILE CONNECTION LINK GENERATED".*

### 2. Start the Body (Mobile App)
This runs the app on your phone.
```powershell
cd "c:\Users\sagar\my project\jado\flutter_app"
flutter run
```
*Make sure your phone is connected via USB and USB Debugging is ON.*

---

## 📱 Features
- **Voice Control**: "Pause", "Volume 50%", "Close VS Code".
- **Live Screen**: View your PC desktop on your phone.
- **Waveform Avatar**: Visualizes voice activity.

## 🛠️ Troubleshooting
- **App stuck on "Connecting"?**
    - Check if your phone and PC are on the same WiFi.
    - Click the "Settings" (gear icon) on the app and ensure the IP matches the one shown in the `python main.py` terminal.

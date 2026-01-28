import warnings
import os

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import threading
import time
from modules.voice_engine import VoiceEngine
from modules.nova_engine import NovaEngine
import config
import psutil
import datetime
import io
import base64
from PIL import Image
from flask import Response, jsonify

# Flask Setup
app = Flask(__name__, template_folder="web/templates", static_folder="web/static")
# Force threading mode to avoid eventlet/gevent compatibility issues on Py3.12
socketio = SocketIO(app, async_mode='threading')

# Global instances
voice = None
nova = None
is_listening_enabled = True # Default On

@app.route('/')
def index():
    return render_template('index.html')

def gen_frames():
    import mss
    from PIL import Image
    import numpy as np
    
    with mss.mss() as sct:
        # Get monitor 1 bounds
        monitor = sct.monitors[1]
        
        while True:
            try:
                # Capture screen using mss (very fast)
                sct_img = sct.grab(monitor)
                
                # Convert to PIL Image
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                
                # Resize for performance (optional, but good for streaming)
                img = img.resize((960, 540)) 
                
                # Convert to byte stream
                frame_buffer = io.BytesIO()
                img.save(frame_buffer, format='JPEG', quality=70)
                frame_bytes = frame_buffer.getvalue()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
                time.sleep(0.04) # Limit FPS (~25 FPS)
            except Exception as e:
                print(f"Screen capture error: {e}")
                time.sleep(1)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/current_frame')
def current_frame():
    """Returns a single snapshot for the Flutter app polling."""
    import mss
    from PIL import Image
    
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            
        img = img.resize((960, 540)) # Optimize network
        frame_buffer = io.BytesIO()
        img.save(frame_buffer, format='JPEG', quality=60)
        frame_buffer.seek(0)
        return Response(frame_buffer, mimetype='image/jpeg')
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/proxy_image')
def proxy_image():
    """Proxies image requests to bypass CORS/Network issues."""
    image_url = request.args.get('url')
    if not image_url:
        print("Proxy Error: No URL provided") 
        return "No URL provided", 400
    
    print(f"Proxying Image: {image_url}")
    try:
        import requests
        # Fake a browser user agent to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        resp = requests.get(image_url, headers=headers, timeout=15)
        
        if resp.status_code != 200:
             print(f"Proxy Upstream Error: {resp.status_code}")
             return f"Upstream Error: {resp.status_code}", 502

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        resp_headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
        
        response = Response(resp.content, resp.status_code, resp_headers)
        return response
    except Exception as e:
        print(f"Proxy Exception: {e}")
        return f"Proxy Error: {e}", 500

@app.route('/analyze_image', methods=['POST'])
def analyze_image():
    """Receives an image (upload or camera) and processes it with Vision."""
    global nova
    try:
        data = request.json
        image_data = data.get('image') # Base64 string
        message = data.get('message', 'What is in this image?')
        
        if not image_data:
            return jsonify({'response': "No image received."}), 400

        # Decode base64
        if "base64," in image_data:
            image_data = image_data.split("base64,")[1]
            
        img_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(img_bytes))
        
        # Process with Nova Vision
        response = nova.process_vision(message, img)
        
        # Speak response
        threading.Thread(target=voice.speak, args=(response,)).start()
        
        return jsonify({'response': response})

    except Exception as e:
        print(f"Image Analysis Error: {e}")
        return jsonify({'error': str(e)}), 500

@socketio.on('toggle_listening')
def handle_toggle_listening(data):
    global is_listening_enabled
    # Simple toggle logic or specific action
    action = data.get('action')
    if action == 'start':
        is_listening_enabled = True
        print("Mic activated.")
        notify_ui('status', {'status': 'Listening...'})
    elif action == 'stop':
        is_listening_enabled = False
        print("Mic deactivated.")
        notify_ui('status', {'status': 'Mic Off'})
        notify_ui('mic_state', {'active': is_listening_enabled})
    elif action == 'toggle':
        is_listening_enabled = not is_listening_enabled
        status = 'Listening...' if is_listening_enabled else 'Mic Off'
        notify_ui('status', {'status': status})
        notify_ui('mic_state', {'active': is_listening_enabled})

@socketio.on('text_command')
def handle_text_command(data):
    """Handles text input from the web UI."""
    text = data.get('text')
    print(f"Text Input Received: {text}")
    
    # Process using Nova Engine (same as voice)
    # We run this in a background thread to avoid blocking the socket
    threading.Thread(target=process_text_input, args=(text,)).start()

def process_text_input(text):
    global nova, voice
    if not nova: return

    # Notify UI
    notify_ui('conversation', {'role': 'user', 'text': text})
    notify_ui('status', {'status': 'Processing Text...'})
    
    # Process
    response = nova.process(text) # Language defaults to English for text
    
    # Respond
    if response:
        if isinstance(response, dict):
            # Rich response (Text + Image)
            text_resp = response.get('text', '')
            image_url = response.get('image')
            
            # Speak text
            voice.speak(text_resp)
            
            # Send to UI with image
            notify_ui('conversation', {'role': 'sami', 'text': text_resp, 'image': image_url})
            
        else:
            # Simple text response
            voice.speak(response)
    
    notify_ui('status', {'status': 'Idle'})

def notify_ui(event_type, data):
    """Callback to send updates to the UI."""
    socketio.emit(f'{event_type}_update', data)
    time.sleep(0.01)

def emit_system_stats():
    """Background thread to emit system statistics."""
    while True:
        try:
            # Memory
            memory = psutil.virtual_memory()
            ram_usage = memory.percent
            
            # CPU
            cpu_usage = psutil.cpu_percent(interval=None)
            
            # Disk (C: drive)
            try:
                disk = psutil.disk_usage('C:\\')
                disk_usage = disk.percent
            except:
                disk_usage = 0
            
            # Time & Date
            now = datetime.datetime.now()
            current_time = now.strftime("%I:%M %p")
            current_date = now.strftime("%A, %b %d")
            
            # Weather Mock
            weather = "25°C Clear" 
            
            stats = {
                "ram": ram_usage,
                "cpu": cpu_usage,
                "disk": disk_usage,
                "time": current_time,
                "date": current_date,
                "weather": weather
            }
            
            socketio.emit('system_stats', stats)
            time.sleep(2)
        except Exception as e:
            print(f"Error fetching stats: {e}")
            time.sleep(5)

def run_voice_assistant():
    """Main voice loop running in a separate thread."""
    global voice, nova
    
    # Initialize with callback
    voice = VoiceEngine(on_update=notify_ui)
    nova = NovaEngine()

    time.sleep(1) # Allow UI to load
    voice.speak("SAMi online.")
    time.sleep(1)

    notify_ui('status', {'status': 'Waiting for Wake Word'})

    current_lang = config.DEFAULT_LANG
    is_active = False

    last_interaction_time = time.time()
    
    while True:
        try:
            # Check Mic State
            if not is_listening_enabled:
                time.sleep(0.5)
                continue

            # 1. Passive Listening (Waiting for Wake Word or Follow-up)
            if not is_active:
                print(f"Waiting for wake word '{config.WAKE_WORD}'...")
                notify_ui('status', {'status': 'Standby...'})
                
                command = voice.listen(language='en-in') 
                
                if config.WAKE_WORD in command:
                    is_active = True
                    last_interaction_time = time.time()
                    # Check if command was spoken WITH wake word
                    remaining_command = command.replace(config.WAKE_WORD, "").strip()
                    if remaining_command:
                        print(f"One-shot command detected: {remaining_command}")
                        command = remaining_command # Set as command to process
                    else:
                        voice.speak("Yes? I'm listening.", language='en')
                        continue 
                else:
                    continue 

            # 2. Active Listening (Processing Commands)
            # Check for Continuous Mode Timeout
            if is_active and config.CONTINUOUS_MODE:
                if time.time() - last_interaction_time > config.CONTINUOUS_TIMEOUT:
                    print("Continuous mode timeout. Returning to sleep.")
                    is_active = False
                    notify_ui('status', {'status': 'Standby...'})
                    continue

            if is_active and not command: 
                # Listen for command
                command = voice.listen(language=current_lang)
                if not command and config.CONTINUOUS_MODE:
                    # Silence in active mode -> check timeout next loop
                    continue
                elif not command:
                    # Silence in non-continuous mode -> sleep
                    is_active = False
                    continue
            
            # Reset command for next loop if we just processed one
            if not command: continue
            
            # Update Interaction Time
            last_interaction_time = time.time()

            # Check for exit commands
            if "exit" in command or "stop" in command or "quit" in command or "go to sleep" in command:
                voice.speak("Going to sleep.", language=current_lang)
                is_active = False
                command = None
                continue

            if command:
                # Check for Language Switching
                for lang_name, lang_code in config.LANGUAGES.items():
                    if f"speak in {lang_name}" in command or f"change language to {lang_name}" in command:
                        current_lang = lang_code
                        voice.speak(f"Okay, switching to {lang_name}.", language=lang_code)
                        command = None 
                        break

                if command:
                    # Process command via Nova Engine
                    response = nova.process(command, language=current_lang)
                    
                    # Speak response
                    if response:
                        if isinstance(response, dict):
                             # Rich response
                             text_resp = response.get('text', '')
                             image_url = response.get('image')
                             voice.speak(text_resp, language=current_lang)
                             notify_ui('conversation', {'role': 'sami', 'text': text_resp, 'image': image_url})
                        else:
                             voice.speak(response, language=current_lang)
                             # voice.speak handles the UI notification internally for text only, usually? 
                             # Wait, checking voice engine implementation... 
                             # If voice engine notifies UI, we might duplicate text log if we did it above.
                             # But for images we NEED to send the image.
                             
                        # In continuous mode, we stay active
                        last_interaction_time = time.time()
                    
                    command = None # Reset for next turn

        except KeyboardInterrupt:
            voice.speak("Shutting down manually.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            voice.speak("I encountered an error.")
            is_active = False

if __name__ == "__main__":
    import webbrowser
    
    # Start voice assistant thread
    assistant_thread = threading.Thread(target=run_voice_assistant)
    assistant_thread.daemon = True
    assistant_thread.start()

    # Start system stats thread
    stats_thread = threading.Thread(target=emit_system_stats)
    stats_thread.daemon = True
    stats_thread.start()

    # Start Web Server
    # Start Web Server
    import socket
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    local_ip = get_local_ip()
    port = 5000
    mobile_url = f"http://{local_ip}:{port}"

    print("\n" + "="*50)
    print("  MOBILE CONNECTION LINK GENERATED")
    print("="*50)
    print(f"  Type this NUMBER into your PHONE BROWSER:")
    print(f"  >>>  {mobile_url}  <<<")
    print("="*50 + "\n")
    
    webbrowser.open(mobile_url)
    socketio.run(app, debug=True, use_reloader=False, host='0.0.0.0', port=5000) 

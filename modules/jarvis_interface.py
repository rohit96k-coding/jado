import datetime
import wikipedia

import os
import webbrowser
import config
import config
from AppOpener import open as app_open
import pyautogui
from PIL import Image

class JarvisInterface:
    def __init__(self):
        pass

    def get_time(self):
        """Returns the current time."""
        now = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {now}"

    def get_date(self):
        """Returns the current date."""
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {today}"

    def search_wikipedia(self, query):
        """Searches Wikipedia for the query."""
        try:
            results = wikipedia.summary(query, sentences=2)
            return f"According to Wikipedia: {results}"
        except wikipedia.exceptions.DisambiguationError:
            return "There are multiple results for this topic. Please be more specific."
        except wikipedia.exceptions.PageError:
            return "I couldn't find any page matching that request."
        except Exception as e:
            return f"Wikipedia search failed: {e}"

    def play_youtube(self, song_name):
        """Plays the requested song/video on YouTube."""
        try:
            import pywhatkit
            pywhatkit.playonyt(song_name)
            return f"Playing {song_name} on YouTube"
        except Exception as e:
            if "Internet" in str(e):
                return "I cannot play YouTube videos while offline."
            return f"Failed to play on YouTube: {e}"

    def open_website(self, url):
        """Opens a website in the default browser."""
        if not url.startswith('http'):
            url = 'https://' + url
        webbrowser.open(url)
        return f"Opening {url}"

    def google_search(self, query):
        """Performs a Google search."""
        try:
            import pywhatkit
            pywhatkit.search(query)
            return f"Searching Google for {query}"
        except Exception as e:
            if "Internet" in str(e):
                 return "I cannot search Google while offline."
            return f"Google search failed: {e}"

    def open_app(self, app_name):
        """Opens a requested application."""
        # Custom mapping for critical apps if AppOpener fails or for precision
        if "chrome" in app_name.lower():
            try:
                os.startfile(config.CHROME_PATH)
                return "Opening Google Chrome"
            except:
                pass # Fallback
        elif "code" in app_name.lower() or "vs code" in app_name.lower():
            try:
                os.startfile(config.VS_CODE_PATH)
                return "Opening Visual Studio Code"
            except:
                pass # Fallback
        elif "notepad" in app_name.lower():
            os.system("notepad")
            return "Opening Notepad"
        
        # Fallback to AppOpener
        try:
            app_open(app_name, match_closest=True)
            return f"Opening {app_name}"
        except:
            return f"I couldn't find an app named {app_name}"

    # --- DEVICE CONTROL (ACCESS ALL FEATURES) ---
    def control_mouse(self, action, x=0, y=0):
        """Controls mouse cursor."""
        try:
            width, height = pyautogui.size()
            if action == "move":
                # Convert descriptive directions if x/y are strings
                if isinstance(x, str):
                    if "center" in x: pyautogui.moveTo(width/2, height/2)
                    elif "up" in x: pyautogui.moveRel(0, -100)
                    elif "down" in x: pyautogui.moveRel(0, 100)
                    elif "left" in x: pyautogui.moveRel(-100, 0)
                    elif "right" in x: pyautogui.moveRel(100, 0)
                else:
                    pyautogui.moveTo(x, y)
                return "Mouse moved."
            elif action == "click":
                pyautogui.click()
                return "Mouse clicked."
            elif action == "double_click":
                pyautogui.doubleClick()
                return "Double clicked."
            elif action == "right_click":
                pyautogui.rightClick()
                return "Right clicked."
            elif action == "scroll_up":
                pyautogui.scroll(500)
                return "Scrolled up."
            elif action == "scroll_down":
                pyautogui.scroll(-500)
                return "Scrolled down."
        except Exception as e:
            return f"Mouse control failed: {e}"

    def control_keyboard(self, action, text=""):
        """Controls keyboard."""
        try:
            if action == "type":
                pyautogui.write(text, interval=0.05)
                return f"Typed: {text}"
            elif action == "press":
                # Handle keys like "enter", "f11", "ctrl+c"
                if "+" in text:
                    keys = text.split("+")
                    pyautogui.hotkey(*keys)
                else:
                    pyautogui.press(text)
                return f"Pressed {text}"
        except Exception as e:
            return f"Keyboard error: {e}"

    def file_operations(self, action, path, content=""):
        """Controls file system: create_folder, create_file, delete, read."""
        import shutil
        try:
            if action == "create_folder":
                os.makedirs(path, exist_ok=True)
                return f"Created folder: {path}"
            elif action == "create_file":
                with open(path, 'w') as f: f.write(content)
                return f"Created file: {path}"
            elif action == "delete":
                if os.path.isdir(path): shutil.rmtree(path)
                else: os.remove(path)
                return f"Deleted: {path}"
            elif action == "read":
                with open(path, 'r') as f: return f.read()
        except Exception as e:
            return f"File op failed: {e}"

    def clipboard_control(self, action, text=""):
        """Controls clipboard: copy, paste, get."""
        import pyperclip
        try:
            if action == "copy":
                pyperclip.copy(text)
                return "Copied to clipboard."
            elif action == "paste":
                return pyperclip.paste()
            elif action == "get":
                return f"Clipboard: {pyperclip.paste()}"
        except Exception as e:
             return f"Clipboard failed: {e}"
        
    def brightness_control(self, level):
        """Sets screen brightness (0-100)."""
        import screen_brightness_control as sbc
        try:
            sbc.set_brightness(level)
            return f"Brightness set to {level}%"
        except Exception as e:
             return f"Brightness failed: {e}"

    def system_control(self, command):
        """Handles system commands like shutdown/restart."""
        command = command.lower()
        if "shutdown" in command:
            os.system("shutdown /s /t 5")
            return "Shutting down the system in 5 seconds."
        elif "restart" in command:
            os.system("shutdown /r /t 5")
            return "Restarting the system in 5 seconds."
        elif "lock" in command:
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "System locked."
        elif "minimize" in command:
            pyautogui.hotkey('win', 'down')
            pyautogui.hotkey('win', 'down') # Twice for sure
            return "Windows minimized."
        elif "maximize" in command:
            pyautogui.hotkey('win', 'up')
            return "Window maximized."
        elif "close window" in command or "close this" in command:
            pyautogui.hotkey('alt', 'f4')
            return "Active window closed."
        elif "enter" in command: pyautogui.press('enter'); return "Pressed Enter."
        elif "space" in command: pyautogui.press('space'); return "Pressed Space."
            
        return "System command not recognized."

    def take_screenshot(self, filename="screenshot.png"):
        """Takes a screenshot and saves it."""
        try:
            # Save to desktop or a specific folder
            save_path = os.path.join(config.DATA_DIR, filename) 
            # Check if filename is just a name or path
            if not filename.endswith(".png"):
                filename += ".png"
            
            pyautogui.screenshot(save_path)
            # Open the screenshot
            os.startfile(save_path)
            return f"Screenshot saved to {save_path}"
        except Exception as e:
            return f"Failed to take screenshot: {e}"

    def get_screen_image(self):
        """Returns the current screen as a PIL Image object (no save)."""
        try:
            return pyautogui.screenshot()
        except:
            return None

    def volume_control(self, action, amount=None):
        """Controls system volume: 'mute', 'up', 'down', 'set'. Amount is percentage."""
        try:
            import pyautogui
            
            # Default step for single command
            if amount is None:
                step_count = 5 # Default 10% (5 * 2%)
            else:
                # Calculate steps (Windows volume usually moves 2% per key press)
                steps = int(amount) / 2
                step_count = int(steps)
                
            if action == "mute":
                pyautogui.press("volumemute")
                return "Volume muted/unmuted."
            elif action == "up":
                for _ in range(step_count):
                    pyautogui.press("volumeup")
                return f"Volume increased by {amount}%." if amount else "Volume increased."
            elif action == "down":
                for _ in range(step_count):
                    pyautogui.press("volumedown")
                return f"Volume decreased by {amount}%." if amount else "Volume decreased."
            elif action == "set":
                # To set absolute volume without pycaw, we zero it out then go up
                # This is a bit hacky but works universally without dependencies
                if amount is not None:
                    # 1. Mute/Zero (safest is to just down 50 times to be 0)
                    for _ in range(50):
                         pyautogui.press("volumedown")
                    
                    # 2. Go up to desired amount
                    target_steps = int(int(amount) / 2)
                    for _ in range(target_steps):
                        pyautogui.press("volumeup")
                    return f"Volume set to {amount}%."
            return "Unknown volume command."
        except Exception as e:
            return f"Volume control failed: {e}"

    def media_control(self, action):
        """Controls media playback: 'pause', 'play', 'stop', 'next', 'previous'."""
        try:
            import pyautogui
            if action == "pause" or action == "play":
                pyautogui.press("playpause")
                return "Media paused/played."
            elif action == "stop":
                pyautogui.press("stop") # May not work on all players, playpause is safer fallback often
                return "Media stopped."
            elif action == "next":
                pyautogui.press("nexttrack")
                return "Skipping to next track."
            elif action == "previous":
                pyautogui.press("prevtrack")
                return "Going to previous track."
            return "Unknown media command."
        except Exception as e:
            return f"Media control failed: {e}"

    def close_app(self, app_name):
        """Closes a specific application."""
        app_name = app_name.lower()
        try:
            if "code" in app_name or "vs code" in app_name:
                os.system("taskkill /f /im Code.exe")
                return "Closed Visual Studio Code."
            elif "chrome" in app_name:
                os.system("taskkill /f /im chrome.exe")
                return "Closed Google Chrome."
            elif "notepad" in app_name:
                os.system("taskkill /f /im notepad.exe")
                return "Closed Notepad."
            elif "spotify" in app_name:
                os.system("taskkill /f /im spotify.exe")
                return "Closed Spotify."
            elif "calculator" in app_name:
                 os.system("taskkill /f /im calculator.exe")
                 return "Closed Calculator."
            else:
                return f"I don't have a specific kill command for {app_name} yet."
        except Exception as e:
            return f"Failed to close {app_name}: {e}"

    def execute_task(self, task_name, *args):
        """Generic entry point for Nova to trigger actions."""
        # This allows Nova to call 'execute_task("open_app", "notepad")'
        # making it a unified interface.
        if hasattr(self, task_name):
            method = getattr(self, task_name)
            if args:
                return method(*args)
            else:
                return method()
        else:
            return f"Task {task_name} not available in Jarvis capabilities."

    def create_login_page(self):
        """Generates a modern login page and opens it."""
        try:
            base_path = os.path.join(config.DATA_DIR, "generated_web", "login_page")
            os.makedirs(base_path, exist_ok=True)
            
            # HTML Content
            html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Modern Login</title>
    <link rel="stylesheet" href="style.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
</head>
<body>
    <div class="login-container">
        <form class="login-form">
            <h2>Welcome Back</h2>
            <div class="input-group">
                <input type="text" required>
                <label>Username</label>
            </div>
            <div class="input-group">
                <input type="password" required>
                <label>Password</label>
            </div>
            <button type="submit">Login</button>
            <div class="footer">
                <p>Don't have an account? <a href="#">Sign up</a></p>
            </div>
        </form>
    </div>
    <script src="script.js"></script>
</body>
</html>
"""
            # CSS Content
            css_content = """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Poppins', sans-serif;
}

body {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: #111;
    color: #fff;
}

.login-container {
    position: relative;
    width: 400px;
    padding: 50px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    backdrop-filter: blur(10px);
    box-shadow: 0 15px 25px rgba(0,0,0,0.5);
}

.login-container h2 {
    text-align: center;
    margin-bottom: 30px;
    color: #fff;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.input-group {
    position: relative;
    margin-bottom: 30px;
}

.input-group input {
    width: 100%;
    padding: 10px 0;
    background: transparent;
    border: none;
    border-bottom: 1px solid #fff;
    color: #fff;
    font-size: 16px;
    outline: none;
}

.input-group label {
    position: absolute;
    top: 0;
    left: 0;
    padding: 10px 0;
    color: #fff;
    pointer-events: none;
    transition: 0.5s;
}

.input-group input:focus ~ label,
.input-group input:valid ~ label {
    top: -20px;
    left: 0;
    color: #03e9f4;
    font-size: 12px;
}

button {
    width: 100%;
    padding: 10px;
    background: #03e9f4;
    color: #111;
    border: none;
    border-radius: 5px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 0 5px #03e9f4, 0 0 25px #03e9f4;
    transition: 0.3s;
}

button:hover {
    background: #03efff;
    box-shadow: 0 0 10px #03efff, 0 0 50px #03efff;
}

.footer {
    margin-top: 20px;
    text-align: center;
    font-size: 14px;
}

.footer a {
    color: #03e9f4;
    text-decoration: none;
}
"""
            # JS Content
            js_content = """
document.querySelector('.login-form').addEventListener('submit', function(e) {
    e.preventDefault();
    alert('Login capability is for demonstration.');
});
"""
            
            with open(os.path.join(base_path, "index.html"), "w", encoding='utf-8') as f:
                f.write(html_content)
            with open(os.path.join(base_path, "style.css"), "w", encoding='utf-8') as f:
                f.write(css_content)
            with open(os.path.join(base_path, "script.js"), "w", encoding='utf-8') as f:
                f.write(js_content)
                
            file_url = "file://" + os.path.join(base_path, "index.html").replace("\\", "/")
            webbrowser.open(file_url)
            return "I have created a login page and opened it for you."
            
        except Exception as e:
            return f"Failed to create login page: {e}"

    def save_and_run_code(self, code, language="python"):
        """Saves code to a file and executes it (Python only for execution safety)."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_code_{timestamp}"
            
            if language.lower() == "python":
                ext = ".py"
            elif language.lower() == "html":
                ext = ".html"
            elif language.lower() == "javascript" or language.lower() == "js":
                ext = ".js"
            elif language.lower() == "css":
                ext = ".css"
            elif language.lower() == "java":
                ext = ".java"
            elif language.lower() == "php":
                ext = ".php"
            elif language.lower() == "cpp" or language.lower() == "c++":
                ext = ".cpp"
            elif language.lower() == "c#" or language.lower() == "csharp":
                ext = ".cs"
            else:
                ext = ".txt"
                
            filename += ext
            file_path = os.path.join(config.DATA_DIR, "generated_code", filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, "w", encoding='utf-8') as f:
                f.write(code)
                
            if language.lower() == "python":
                # Execute Python code
                # SECURITY WARNING: execute_task allowing arbitrary code execution is risky.
                # For this user request "any command for wite a code... and run the code", we allow it.
                # We use specific subprocess to run it distinct from main process
                import subprocess
                result = subprocess.run(["python", file_path], capture_output=True, text=True, timeout=10)
                output = result.stdout + "\n" + result.stderr
                return f"Code saved to {filename}. Output:\n{output}"
            elif language.lower() == "html":
                webbrowser.open("file://" + file_path.replace("\\", "/"))
                return f"HTML saved to {filename} and opened in browser."
            else:
                # Just open the file
                os.startfile(file_path)
                return f"Code saved to {filename}."
                
        except Exception as e:
            return f"Failed to handle code: {e}"

    def visual_code_demo(self, code, language="python"):
        """Visually opens VS Code, types code, and runs it."""
        try:
            import pyautogui
            import time
            import subprocess
            
            # 1. Open VS Code
            # We assume 'code' is in PATH or use config path
            try:
                os.startfile(config.VS_CODE_PATH)
            except:
                os.system("code")
                
            time.sleep(5) # Wait for VS Code to load (it can be slow)
            
            # 2. Create New File (Ctrl+N)
            pyautogui.hotkey('ctrl', 'n')
            time.sleep(1)
            
            # 3. Type the code character by character
            lines = code.split('\n')
            for line in lines:
                # Handle indentation (simple tab/space preservation)
                # VS Code auto-indent might interfere, but for simple scripts it's usually okay
                for char in line:
                    pyautogui.write(char) # Very fast typing, but visible
                pyautogui.press("enter")
                # time.sleep(0.01) # fast typing

            time.sleep(1)
            
            # 4. Run Code
            # Use absolute path to guarantee location
            timestamp = datetime.datetime.now().strftime("%H%M%S")
            filename = f"sami_demo_{timestamp}.py"
            full_save_path = os.path.join(config.DATA_DIR, "generated_code", filename)
            # Ensure dir exists
            os.makedirs(os.path.dirname(full_save_path), exist_ok=True)
            
            pyautogui.hotkey('ctrl', 's')
            time.sleep(1.5) # Wait for Save As dialog
            
            # Type FULL path (this is safer than relying on default dir)
            # We need to delete whatever might be there first (Ctrl+A, Del) just in case
            # But usually it's empty or highlighted.
            pyautogui.write(full_save_path)
            time.sleep(1.0)
            pyautogui.press('enter')
            time.sleep(1.5) # Wait for save to complete

            # Open NEW Terminal (Ctrl+Shift+`)
            pyautogui.hotkey('ctrl', 'shift', '`') 
            time.sleep(2) # Wait for terminal
            
            # Clear screen
            pyautogui.write("cls")
            pyautogui.press('enter')
            time.sleep(0.5)
            
            # Run the file using local python and full path
            if language.lower() == "python":
                # Add a print to confirm execution start
                pyautogui.write(f'echo Running {filename}...')
                pyautogui.press('enter')
                
                pyautogui.write(f'python "{full_save_path}"')
                pyautogui.press('enter')
            else:
                pyautogui.write(f"echo Cannot run {language} automatically yet.")
                pyautogui.press('enter')

            return "I have opened VS Code, typed your code, and executed it."

        except Exception as e:
            return f"Visual demo failed: {e}"

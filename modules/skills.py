import datetime
import wikipedia
import pywhatkit
import os
import webbrowser
import config
from AppOpener import open as app_open
import time
import random

class Skills:
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

    def play_youtube(self, song_name):
        """Plays the requested song/video on YouTube."""
        pywhatkit.playonyt(song_name)
        return f"Playing {song_name} on YouTube"

    def open_website(self, url):
        """Opens a website in the default browser."""
        if not url.startswith('http'):
            url = 'https://' + url
        webbrowser.open(url)
        return f"Opening {url}"

    def google_search(self, query):
        """Performs a Google search."""
        pywhatkit.search(query)
        return f"Searching Google for {query}"

    def open_app(self, app_name):
        """Opens a requested application."""
        # Custom mapping for critical apps if AppOpener fails or for precision
        if "chrome" in app_name:
            os.startfile(config.CHROME_PATH)
            return "Opening Google Chrome"
        elif "code" in app_name or "vs code" in app_name:
            os.startfile(config.VS_CODE_PATH)
            return "Opening Visual Studio Code"
        elif "notepad" in app_name:
            os.system("notepad")
            return "Opening Notepad"
        else:
            # Fallback to AppOpener
            try:
                app_open(app_name, match_closest=True)
                return f"Opening {app_name}"
            except:
                return f"I couldn't find an app named {app_name}"

    def ask_gemini(self, prompt, language='en'):
        """Queries Google Gemini API for a response."""
        if not config.GEMINI_API_KEY:
            return "I need a Gemini API key to answer that. Please configure it in config.py."
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=config.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-pro')
            
            # Contextual Prompt for Language
            full_prompt = f"{prompt}. (Reply in {language} language. Keep it concise.)"
            
            for attempt in range(3):
                try:
                    response = model.generate_content(full_prompt)
                    return response.text
                except Exception as e:
                    if "429" in str(e) and attempt < 2:
                         wait_time = (2 ** attempt) + random.uniform(0, 1)
                         time.sleep(wait_time)
                         continue
                    raise e
        except Exception as e:
            return f"I had trouble connecting to the AI brain. Error: {e}"

    def system_control(self, command):
        """Handles system commands like shutdown/restart."""
        if "shutdown" in command:
            os.system("shutdown /s /t 5")
            return "Shutting down the system in 5 seconds."
        elif "restart" in command:
            os.system("shutdown /r /t 5")
            return "Restarting the system in 5 seconds."
        elif "lock" in command:
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "System locked."
        return "System command not recognized."

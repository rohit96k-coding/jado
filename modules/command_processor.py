from modules.skills import Skills
import datetime

class CommandProcessor:
    def __init__(self):
        self.skills = Skills()

    def process(self, command, language='en-in'):
        """Analyzes command and executes the appropriate skill."""
        if not command:
            return None

        # Basic Intents
        if 'time' in command:
            return self.skills.get_time()
        
        elif 'date' in command:
            return self.skills.get_date()
        
        elif 'wikipedia' in command:
            query = command.replace('wikipedia', '').replace('search', '').strip()
            return self.skills.search_wikipedia(query)
            
        elif 'play' in command:
            song = command.replace('play', '').strip()
            return self.skills.play_youtube(song)
            
        elif 'search' in command or 'google' in command:
            query = command.replace('search', '').replace('google', '').strip()
            return self.skills.google_search(query)
            
        elif 'open' in command:
            app_name = command.replace('open', '').strip()
            # Simple check if it looks like a website
            if '.' in app_name and not ' ' in app_name:
                return self.skills.open_website(app_name)
            else:
                return self.skills.open_app(app_name)

        elif 'shutdown' in command or 'restart' in command or 'lock system' in command:
            return self.skills.system_control(command)
            
        elif 'who are you' in command or 'introduce yourself' in command:
            return "I am SAMi, your Smart Artificial Mind Interface. I can help you with daily tasks, search the web, and control your system."

        elif 'say' in command or 'repeat' in command:
            # Explicit Text-to-Speech
            text_to_speak = command.replace('say', '').replace('repeat', '').strip()
            return text_to_speak

        else:
            # Fallback to Conversational AI
            return self.skills.ask_gemini(command, language=language)

from modules.jarvis_interface import JarvisInterface
from modules.google_integrations import GoogleIntegrations
import config
import datetime

class RoutineManager:
    def __init__(self, nova_engine):
        self.nova = nova_engine
        self.jarvis = JarvisInterface()
        self.google = GoogleIntegrations()

    def execute_routine(self, routine_name):
        """Executes a predefined sequence of actions."""
        routine_name = routine_name.lower()
        
        if "good morning" in routine_name:
            return self._routine_good_morning()
        elif "good night" in routine_name:
            return self._routine_good_night()
        elif "start work" in routine_name:
            return self._routine_start_work()
        else:
            return "Routine not found."

    def _routine_good_morning(self):
        responses = []
        
        # 1. Greeting
        responses.append(f"Good morning, {config.FULL_NAME}.")
        
        # 2. Time & Date
        responses.append(self.jarvis.get_date())
        responses.append(self.jarvis.get_time())
        
        # 3. Weather (Mock or Real if API)
        responses.append("The weather is currently 25 degrees and clear.")
        
        # 4. Calendar check (Simulated via Google open)
        self.google.create_calendar_event(title="Morning Check") # Just opens calendar
        responses.append("I've opened your calendar for the day.")
        
        # 5. News (via Research Agent if available, briefly)
        # responses.append(self.nova.research_agent.conduct_research("top news headlines today"))
        
        return " ".join(responses)

    def _routine_good_night(self):
        # 1. Turn off lights (Simulated)
        # self.jarvis.execute_smart_home("lights", "off") 
        # 2. Set Alarm suggestion
        return "Good night, Sir. Systems going to standby."

    def _routine_start_work(self):
        # Open work apps
        self.jarvis.open_app("chrome")
        self.jarvis.open_app("vs code")
        self.jarvis.open_website("https://mail.google.com")
        return "Workspace initialized. Good luck."

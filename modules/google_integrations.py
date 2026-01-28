import webbrowser
import urllib.parse
import datetime

class GoogleIntegrations:
    def __init__(self):
        pass

    def create_calendar_event(self, title="Meeting", date=None, time=None):
        """Opens Google Calendar event creation with pre-filled details."""
        base_url = "https://calendar.google.com/calendar/r/eventedit?"
        
        # Simple parsing if date/time not provided (could be improved with dateparser)
        text = title
        
        params = {
            'text': title,
            'details': 'Scheduled via SAMi Assistant',
        }
        
        # If we had robust date parsing, we'd add 'dates' param here
        # For now, we rely on Google's "Quick Add" smarts or just open the editor
        
        query_string = urllib.parse.urlencode(params)
        final_url = base_url + query_string
        webbrowser.open(final_url)
        return f"Opening Google Calendar to schedule '{title}'."

    def draft_email(self, recipient="", subject="", body=""):
        """Opens Gmail composition window."""
        base_url = "https://mail.google.com/mail/?view=cm&fs=1"
        
        params = {}
        if recipient: params['to'] = recipient
        if subject: params['su'] = subject
        if body: params['body'] = body
        
        query_string = urllib.parse.urlencode(params)
        final_url = base_url + "&" + query_string
        webbrowser.open(final_url)
        return "Opening Gmail draft."

    def search_maps(self, query):
        """Opens Google Maps."""
        base_url = "https://www.google.com/maps/search/?api=1&query="
        final_url = base_url + urllib.parse.quote(query)
        webbrowser.open(final_url)
        return f"Showing '{query}' on Google Maps."

    def open_drive(self, query=""):
        """Opens Google Drive."""
        if query:
            url = f"https://drive.google.com/drive/search?q={urllib.parse.quote(query)}"
            msg = f"Searching Google Drive for '{query}'."
        else:
            url = "https://drive.google.com/drive/my-drive"
            msg = "Opening Google Drive."
        
        webbrowser.open(url)
        return msg
        
    def open_youtube_video(self, query):
         """Plays specific video or search."""
         import pywhatkit
         pywhatkit.playonyt(query)
         return f"Playing '{query}' on YouTube."


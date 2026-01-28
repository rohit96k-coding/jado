import spotipy
from spotipy.oauth2 import SpotifyOAuth
import config
import time

class SpotifyManager:
    def __init__(self):
        self.sp = None
        self.is_authenticated = False
        self._authenticate()

    def _authenticate(self):
        """Authenticates with Spotify API using config credentials."""
        try:
            if not config.SPOTIPY_CLIENT_ID or not config.SPOTIPY_CLIENT_SECRET:
                print("Spotify: Missing credentials in config.py")
                return

            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=config.SPOTIPY_CLIENT_ID,
                client_secret=config.SPOTIPY_CLIENT_SECRET,
                redirect_uri=config.SPOTIPY_REDIRECT_URI,
                scope="user-read-playback-state,user-modify-playback-state"
            ))
            # Test connection
            self.sp.current_playback()
            self.is_authenticated = True
            print("Spotify: Authenticated successfully.")
        except Exception as e:
            print(f"Spotify Auth Error: {e}")
            self.is_authenticated = False

    def _ensure_active_device(self):
        """Ensures there is an active device to play music on."""
        if not self.is_authenticated: return False
        try:
            devices = self.sp.devices()
            if not devices['devices']:
                print("Spotify: No active devices found. Open Spotify on a device.")
                return False
            return True
        except:
            return False

    def play_music(self, query=None):
        """Plays music. If query provided, searches and plays. Else resumes."""
        if not self.is_authenticated: return "Spotify API not configured."
        
        try:
            if not self._ensure_active_device():
                return "Please open Spotify on your device first."

            if query:
                # Search for the track
                results = self.sp.search(q=query, limit=1, type='track')
                if results['tracks']['items']:
                    track_uri = results['tracks']['items'][0]['uri']
                    track_name = results['tracks']['items'][0]['name']
                    self.sp.start_playback(uris=[track_uri])
                    return f"Playing {track_name} on Spotify."
                else:
                    return f"Could not find {query} on Spotify."
            else:
                self.sp.start_playback()
                return "Resuming music."
        except Exception as e:
            return f"Error playing music: {e}"

    def pause_music(self):
        if not self.is_authenticated: return "Spotify API not configured."
        try:
            self.sp.pause_playback()
            return "Music paused."
        except:
            return "Could not pause music."

    def next_track(self):
        if not self.is_authenticated: return "Spotify API not configured."
        try:
            self.sp.next_track()
            return "Skipping to next track."
        except:
            return "Could not skip track."

    def previous_track(self):
        if not self.is_authenticated: return "Spotify API not configured."
        try:
            self.sp.previous_track()
            return "Going to previous track."
        except:
            return "Could not go to previous track."

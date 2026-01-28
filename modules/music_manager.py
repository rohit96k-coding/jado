import spotipy
from spotipy.oauth2 import SpotifyOAuth
import config
import webbrowser
import urllib.parse

class MusicManager:
    def __init__(self):
        self.sp = None
        self.is_authenticated = False
        self._authenticate()

    def _authenticate(self):
        """Authenticates with Spotify API using config credentials."""
        try:
            if not config.SPOTIPY_CLIENT_ID or not config.SPOTIPY_CLIENT_SECRET:
                # print("Spotify: Missing credentials in config.py") # Silence warning to avoid clutter
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
            # print(f"Spotify Auth Error: {e}")
            self.is_authenticated = False

    def play_music(self, song_name, platform="spotify"):
        """
        Smart play function.
        - If platform is 'jiosaavn', opens web.
        - If platform is 'spotify' AND auth works, uses API.
        - If platform is 'spotify' AND auth fails, opens web.
        """
        if platform.lower() == 'jiosaavn':
            return self.play_jiosaavn(song_name)
        
        if self.is_authenticated:
            return self._play_spotify(song_name)
        else:
            return self._play_spotify_web(song_name)

    def play_jiosaavn(self, song_name):
        """
        Attempts to open JioSaavn App.
        """
        from AppOpener import open as app_open
        print(f"Opening JioSaavn App for '{song_name}'...")
        
        # Method 1: AppOpener (Finds installed app by name)
        try:
            # check_if_installed is not standard in AppOpener, just try open
            # We assume user has an app named "JioSaavn" or "Saavn"
            app_open("jiosaavn", match_closest=True, output=True) 
            return f"Opened JioSaavn App. Please search for '{song_name}'."
        except:
            # Method 2: Fallback to protocol
            try:
                import os
                os.system("start jiosaavn://")
                return f"Launched JioSaavn. Please search for '{song_name}'."
            except:
                pass
        
        # Method 3: Web Fallback (Last Resort)
        webbrowser.open(f"https://www.jiosaavn.com/search/{urllib.parse.quote(song_name)}")
        return "JioSaavn App not found. Opened Web Player."

    def _play_spotify_web(self, song_name):
        """
        Opens the SPOTIFY DESKTOP APP via URI Scheme.
        """
        import os
        # This command forces Windows to open the installed Spotify Application
        # It opens the Search page in the app.
        query = urllib.parse.quote(song_name)
        os.system(f"start spotify:search:{query}")
        return f"Opening '{song_name}' in Spotify App."

    def _play_spotify(self, query):
        try:
            # Ensure device is active
            try:
                devices = self.sp.devices()
                if not devices['devices']:
                    return self._play_spotify_web(query) # Fallback to web if no device
            except:
                 pass

            if query:
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
                return "Resuming Spotify."
        except Exception as e:
            return f"Spotify Error: {e}"

    def control(self, action):
        """Controls playback (pause, next, etc) if Authenticated."""
        if not self.is_authenticated:
            return "I can only control usage if you add Spotify keys in config.py."
            
        try:
            if action == 'pause': self.sp.pause_playback()
            elif action == 'play': self.sp.start_playback()
            elif action == 'next': self.sp.next_track()
            elif action == 'prev': self.sp.previous_track()
            return f"Spotify: {action}"
        except:
             return "Unable to control Spotify."

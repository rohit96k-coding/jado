import pyttsx3
import speech_recognition as sr
import config
import threading

class VoiceEngine:
    def __init__(self, on_update=None):
        # Initialize Text-to-Speech engine
        self.engine = pyttsx3.init()
        self.set_voice_properties()
        
        # Initialize Speech-to-Text recognizer
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 0.6 # Faster response after speaking
        self.recognizer.energy_threshold = 300 # Prevent picking up low noise
        
        try:
            self.microphone = sr.Microphone()
            self.has_mic = True
        except (ImportError, AttributeError, OSError):
            print("Warning: PyAudio not found or microphone unavailable. Voice input disabled.")
            self.microphone = None
            self.has_mic = False
        
        # Callback for UI updates
        self.on_update = on_update
        self.lock = threading.Lock()

    def set_voice_properties(self):
        """Configures voice rate and volume."""
        voices = self.engine.getProperty('voices')
        try:
            self.engine.setProperty('voice', voices[config.VOICE_ID_INDEX].id)
        except IndexError:
            self.engine.setProperty('voice', voices[0].id)
            
        self.engine.setProperty('rate', config.SPEECH_RATE)

    async def _speak_edge_tts(self, text, voice="en-US-AriaNeural"):
        """Async helper for Edge TTS."""
        import edge_tts
        import os
        import tempfile
        
        # Suppress pygame welcome message
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
        import pygame
        # playsound import moved to fallback block

        import uuid
        import time
        import asyncio
        
        temp_dir = tempfile.gettempdir()
        # Use unique filename to avoid "Permission denied" or file lock errors
        unique_id = str(uuid.uuid4())
        output_file = os.path.join(temp_dir, f"sami_edge_{unique_id}.mp3")
        
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_file)
            
            # Play audio
            pygame.mixer.init()
            pygame.mixer.music.load(output_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1) # Async sleep to allow other tasks
                
            # Cleanup
            pygame.mixer.music.unload()
            try:
                os.remove(output_file)
            except: pass
            
        except Exception as e:
            print(f"EdgeTTS Playback Error: {e}")
            raise e # Re-raise to trigger fallback

    def speak(self, text, language='en'):
        """Converts text to speech."""
        print(f"{config.SYSTEM_NAME}: {text}")
        
        # Notify UI
        if self.on_update:
            self.on_update("conversation", {"role": "sami", "text": text})
            self.on_update("status", {"status": "Speaking..."})

        # Use lock to prevent overlapping speech and race conditions
        with self.lock:
            # LIFELIKE MODE (Edge TTS)
            if hasattr(config, 'USE_LIFELIKE_TTS') and config.USE_LIFELIKE_TTS:
                import asyncio
                # Select voice based on config (simple mapping)
                voice_name = "en-US-AriaNeural" # Default Female
                if hasattr(config, 'EDGE_TTS_VOICE'):
                    voice_name = config.EDGE_TTS_VOICE
                
                try:
                    asyncio.run(self._speak_edge_tts(text, voice_name))
                except Exception as e:
                    print(f"EdgeTTS Error: {e}. Switching to Local Fallback.")
                    # Fallback to pyttsx3
                    try:
                        self.engine.say(text)
                        self.engine.runAndWait()
                    except RuntimeError:
                         # Loop already running, maybe just say is enough? 
                         # But if loop is running from another thread (should be blocked by lock though), we wait?
                         # If runAndWait fails, it means loop is running. 
                         pass
                    except Exception as local_e:
                        print(f"CRITICAL: Local TTS also failed: {local_e}")

            # FAST MODE (Local TTS)
            elif config.USE_FAST_TTS:
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                except RuntimeError:
                    pass # Already running
                except Exception as e:
                    print(f"Local TTS Error: {e}")
            
            # LEGACY G-TTS MODE
            else:
                try:
                    # Map full language code (e.g., 'en-in') to gTTS code (e.g., 'en') and TLD
                    # gTTS usually takes 2 letter code, but some like 'en-in' work or map to 'en'
                    lang_code = language.split('-')[0]
                    tld = 'com'
                    if 'in' in language:
                        tld = 'co.in' 
                    elif 'uk' in language:
                        tld = 'co.uk'
                    
                    # Create MP3
                    from gtts import gTTS
                    import os
                    import tempfile
                    
                    # Use temp directory to avoid path issues with spaces (Error 277)
                    temp_dir = tempfile.gettempdir()
                    filename = os.path.join(temp_dir, "sami_response.mp3")
                    
                    tts = gTTS(text=text, lang=lang_code, tld=tld, slow=False)
                    
                    # Remove old file if exists
                    if os.path.exists(filename):
                        try:
                            os.remove(filename)
                        except:
                            pass
                    
                    tts.save(filename)
                    
                    # Play MP3 using Pygame for consistency
                    import os
                    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
                    import pygame
                    try:
                        pygame.mixer.init()
                        pygame.mixer.music.load(filename)
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy():
                            pygame.time.Clock().tick(10)
                    except Exception:
                        # Fallback to playsound
                        from playsound import playsound
                        playsound(filename)
                        
                except Exception as e:
                    print(f"gTTS Error: {e}. Fallback to pyttsx3.")
                    try:
                        self.engine.say(text)
                        self.engine.runAndWait()
                    except RuntimeError:
                        pass

        if self.on_update:
            self.on_update("status", {"status": "Idle"})

    def listen(self, language=config.DEFAULT_LANG):
        """Listens to the user via microphone and returns text."""
        if not self.has_mic:
            import time
            time.sleep(1) # Prevent tight loop if called in loop
            return ""

        try:
            with self.microphone as source:
                print("Listening...")
                if self.on_update:
                    self.on_update("status", {"status": f"Listening ({language})..."})
                
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5) # Better calib
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            print("Recognizing...")
            if self.on_update:
                self.on_update("status", {"status": "Processing..."})
                
            text = self.recognizer.recognize_google(audio, language=language)
            print(f"User: {text}")
            
            if self.on_update:
                self.on_update("conversation", {"role": "user", "text": text})
                
            return text.lower()
            
        except sr.WaitTimeoutError:
            print(">> Silence timeout.")
            return ""
        except sr.UnknownValueError:
            print(">> Audio unclear (or no speech detected).")
            return ""
        except sr.RequestError as e:
            print(f">> Speech API Error: {e}")
            self.speak("Sorry, my speech service is down.")
            return ""
        except Exception as e:
            print(f"Error: {e}")
            return ""

import datetime
import time
import random
import requests
import json


import config
from modules.jarvis_interface import JarvisInterface
from modules.memory_manager import MemoryManager
from modules.music_manager import MusicManager
from modules.research_agent import ResearchAgent
from modules.google_integrations import GoogleIntegrations
from modules.routines import RoutineManager
from modules.nlu_utils import NLUUtils
import PIL.Image

class NovaEngine:
    def __init__(self):
        self.jarvis = JarvisInterface()
        self.memory = MemoryManager()
        self.google = GoogleIntegrations()
        self.music = MusicManager()
        self.routines = RoutineManager(self)
        self.nlu = NLUUtils()
        self.research = ResearchAgent(self) # Initialize Research Agent
        
        self.model = None # Default to None (Local/Rule-based)

        if config.AI_MODE == 'cloud':
            if config.AI_PROVIDER == 'deepseek' and getattr(config, 'DEEPSEEK_API_KEY', None):
                # Use OpenAI SDK for DeepSeek
                from openai import OpenAI
                self.client = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
                self.model = config.DEEPSEEK_MODEL # Just store name string
                print(f"Nova Init: Connected to DeepSeek ({self.model})")
            elif config.GEMINI_API_KEY:
                import google.generativeai as genai
                genai.configure(api_key=config.GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
                print("Nova Init: Connected to Gemini")



    def _generate_with_retry(self, prompt, retries=3):
        """
        Wraps generate_content with exponential backoff for 429 errors.
        """
        # In Quick Mode, do not retry. Fail fast to local model.
        if config.QUICK_RESPONSE_MODE:
            retries = 0

        for attempt in range(retries + 1):
            try:
                # ROUTE BASED ON PROVIDER
                if config.AI_PROVIDER == 'deepseek':
                     return self._generate_deepseek(prompt)
                else:
                     return self.model.generate_content(prompt) # Gemini object
            except Exception as e:
                # 429 is the HTTP status code for Too Many Requests
                if "429" in str(e):
                    if config.QUICK_RESPONSE_MODE:
                        print("Quota Exceeded (Fast Mode). Skipping retry.")
                        raise e # Raise immediately to trigger fallback
                        
                    if attempt < retries:
                        # Exponential backoff: 2, 4, 8... plus jitter
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        print(f"Note: Gemini API Quota Exceeded. Retrying in {wait_time:.1f}s...")
                        time.sleep(wait_time)
                        continue
                raise e

    def process(self, command, language='en-in', image=None):
        """
        Nova's Core Logic Loop
        """
        if not command:
            return None

        # 1. Spelling Correction (Pre-processing)
        original_command = command
        command = self.nlu.autocorrect_sentence(command)
        if command != original_command:
            print(f"Auto-Corrected: '{original_command}' -> '{command}'")

        # 2. Update Memory History
        self.memory.add_history("user", command)
        
        # 2. Pre-process: Handle Wake Word in Text
        command_lower = command.lower()
        wake_word = config.WAKE_WORD.lower()
        
        if wake_word in command_lower:
            if command_lower.startswith(wake_word):
                command_lower = command_lower.replace(wake_word, "", 1).strip()
                if not command_lower:
                    return "Yes, I am here. How can I help?"
        
                if not command_lower:
                    return "Yes, I am here. How can I help?"
        
        # 3. Rule-Based Quick Routes (Low Latency)
        # Check rule based logic first to save API calls
        response = self._check_rules(command_lower)
        if response:
            self.memory.add_history("model", response)
            return response

        # 4. LLM Processing
        # --- QUICK THINK MODE ---
        if config.QUICK_RESPONSE_MODE:
            return self._quick_think(command, language)
            
        # --- DEEP THINK MODE (Advanced Reasoning) ---
        # If not in quick mode, use the advanced reasoning path
        if getattr(config, 'DEEP_THINK_MODE', False):
             return self._deep_think(command, language)

        # --- STANDARD MODE ---
        
        # --- LOCAL AI (OLLAMA) ---
        if config.AI_MODE == 'local':
            try:
                # Build Prompt
                history_context = self.memory.get_context_window(limit=5)
                prompt = f"""System: You are SAMi, an intelligent assistant. Be concise.
Context: {history_context}
User: {command}"""
                
                payload = {
                    "model": config.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False
                }
                
                print(f"Thinking on Local Brain ({config.OLLAMA_MODEL})...")
                response = requests.post(config.OLLAMA_URL, json=payload)
                
                if response.status_code == 200:
                    ai_text = response.json()['response']
                    self.memory.add_history("model", ai_text)
                    return ai_text
                else:
                     return f"My local brain disconnected. (Status: {response.status_code})"
                     
            except requests.exceptions.ConnectionError:
                 return "I cannot connect to Ollama. Please ensure the Ollama app is running on your PC."
            except Exception as e:
                 print(f"Local AI Error: {e}")
                 return "I encountered a local processing error."

        # --- CLOUD AI (GEMINI) ---
        elif self.model:
            try:
                # Build Context from History
                history_context = self.memory.get_context_window(limit=5)
                
                # Construct Prompt
                # We can use the chat history feature of Gemini, or just simple prompting for now
                prompt = f"""
                System: You are SAMi, an advanced AI assistant. Keep responses concise and helpful.
                Context: {history_context}
                User: {command}
                """
                
                response = self._generate_with_retry(prompt)
                ai_text = response.text
                
                self.memory.add_history("model", ai_text)
                return ai_text
                
            except Exception as e:
                error_msg = str(e)
                print(f"Gemini Error: {e}")
                
                # FALLBACK TO LOCAL MODEL
                print("Switching to Local Fallback...")
                return self._run_local_model(command)

    def _generate_deepseek(self, prompt):
        """Helper to call DeepSeek API and return an object with .text attribute for compatibility."""
        completion = self.client.chat.completions.create(
            model=config.DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": "You are SAMi, a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        # Create a mock object so .text works downstream
        class ResponseWrapper:
            def __init__(self, text): self.text = text
            
        return ResponseWrapper(completion.choices[0].message.content)

    def process_vision(self, command, image):
        """Processes an image + text command using Gemini Vision."""
        if not self.model:
            return "I need Gemini API for vision capabilities."
            
        try:
            prompt = [command, image]
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Vision Error: {e}"
        else:
             return "I am in Offline Mode. I can open apps, tell time, and control the system."

    def _check_rules(self, command_lower):
        # 3. Rule-Based Quick Routes (Low Latency)
        
        # Greetings (Instant Response)
        if command_lower in ['hello', 'hi', 'hey', 'hello sami', 'hi sami', 'hey sami']:
            import random
            greetings = ["Hello! I am listening.", "Hi there! How can I help?", "Greetings. Systems online."]
            return random.choice(greetings)
            
        # Common Chit-Chat (No AI Needed)
        if command_lower in ['how are you', 'how are you doing', "what's up"]:
            return "I am functioning at peak efficiency. Ready for your command."
            
        if command_lower in ['thank you', 'thanks', 'cool', 'nice', 'good job']:
            return "You're welcome."
            
        if command_lower in ['who made you', 'who created you']:
            return "I was created by you, Sir."
            
        # Quick Mode Toggle
        if 'fast mode' in command_lower or 'quick mode' in command_lower:
            if 'on' in command_lower or 'enable' in command_lower or 'start' in command_lower:
                config.QUICK_RESPONSE_MODE = True
                config.DEEP_THINK_MODE = False
                return "Fast Mode activated. Responses will be concise."
            elif 'off' in command_lower or 'disable' in command_lower or 'stop' in command_lower:
                config.QUICK_RESPONSE_MODE = False
                return "Fast Mode deactivated."

        # Deep Think Mode Toggle
        if 'deep mode' in command_lower or 'advanced thinking' in command_lower or 'reasoning' in command_lower:
             if 'on' in command_lower or 'enable' in command_lower or 'start' in command_lower:
                 config.DEEP_THINK_MODE = True
                 config.QUICK_RESPONSE_MODE = False # Mutually exclusive
                 return "Advanced Reasoning Mode activated. I will think carefully before answering."
             elif 'off' in command_lower or 'disable' in command_lower or 'stop' in command_lower:
                 config.DEEP_THINK_MODE = False
                 return "Advanced Reasoning Mode deactivated."

        # Persona / Friendly Mode Toggle
        if 'friend' in command_lower or 'casual' in command_lower:
             config.PERSONA = 'friendly'
             config.QUICK_RESPONSE_MODE = False 
             return "Friendly Mode activated. Hey! Let's chat."
        elif 'professional' in command_lower or 'jarvis' in command_lower or 'serious' in command_lower:
             config.PERSONA = 'professional'
             return "Professional Mode activated. Systems online."

        # Conversation Starters (Friendly Interaction)
        if 'bored' in command_lower or ('talk' in command_lower and ('let\'s' in command_lower or 'can we' in command_lower)):
             config.PERSONA = 'friendly' # Auto-switch to friendly
             config.QUICK_RESPONSE_MODE = False
             
             starters = [
                 "If you could travel anywhere right now, where would you go?",
                 "Seen any good movies lately?",
                 "What's the best thing that happened to you today?",
                 "Do you believe in aliens? 👽",
                 "If you had a superpower, what would it be?",
                 "What's your favorite song at the moment?",
                 "Pizza or Burgers? We need to settle this.",
                 "Tell me a secret, I won't tell anyone (I'm encrypted 🔒)."
             ]
             return f"Let's chat! {random.choice(starters)}"
            
        # Identity (Instant Response)
        if 'who are you' in command_lower or 'what is your name' in command_lower:
            return f"I am SAMi, your {config.FULL_NAME}."
            
        # Quick Facts/Math (Bypass LLM)
        if 'what is' in command_lower and 'plus' in command_lower:
             # Very basic math security check
             try:
                 # Extract numbers
                 import re
                 nums = re.findall(r'\d+', command_lower)
                 if len(nums) == 2:
                     return f"The answer is {int(nums[0]) + int(nums[1])}."
             except: pass
             
        if 'capital of' in command_lower:
            if 'india' in command_lower: return "New Delhi is the capital of India."
            if 'france' in command_lower: return "Paris is the capital of France."
            if 'usa' in command_lower: return "Washington D.C. is the capital of the United States."


        # Date and Time
        if 'time' in command_lower and len(command_lower) < 20:
            return self.jarvis.get_time()
        elif 'date' in command_lower and len(command_lower) < 20:
            return self.jarvis.get_date()
            
        # Media Control
        elif 'play' in command_lower and ('youtube' in command_lower or 'song' in command_lower):
            song = command_lower.replace('play', '').replace('youtube', '').strip()
            return self.jarvis.play_youtube(song)
        elif 'pause' in command_lower or 'stop song' in command_lower or 'stop music' in command_lower or 'resume' in command_lower or 'next song' in command_lower:
            if 'pause' in command_lower: action = 'pause'
            elif 'stop' in command_lower: action = 'stop'
            elif 'resume' in command_lower: action = 'play'
            elif 'next' in command_lower: action = 'next'
            else: action = 'pause'
            return self.jarvis.media_control(action)
            
        # Music Control (Spotify & JioSaavn)
        elif 'spotify' in command_lower or 'jiosaavn' in command_lower:
            platform = 'jiosaavn' if 'jiosaavn' in command_lower else 'spotify'
            
            if 'play' in command_lower:
                song = command_lower.replace('play', '').replace(f'on {platform}', '').replace(platform, '').strip()
                return self.music.play_music(song, platform=platform)
            elif 'pause' in command_lower: return self.music.control('pause')
            elif 'next' in command_lower: return self.music.control('next')
            elif 'previous' in command_lower: return self.music.control('prev')
            
        # Screen/Vision
        elif 'screen' in command_lower and ('look' in command_lower or 'what' in command_lower or 'analyze' in command_lower):
            # Capture screen and send to vision
            img = self.jarvis.get_screen_image()
            return self.process_vision("Describe what you see on my screen.", img)

        # App and Website Opening
            
        # App and Website Opening
        elif 'open' in command_lower:
             target = command_lower.replace('open', '').strip()
             # Improved Heuristic: Check for common domains or "dot"
             if '.' in target and ' ' not in target:
                 return self.jarvis.open_website(target)
             elif target in ['youtube', 'google', 'whatsapp', 'instagram', 'facebook']:
                 if target == 'youtube': return self.jarvis.open_website('youtube.com')
                 elif target == 'whatsapp': return self.jarvis.open_website('web.whatsapp.com')
                 elif target == 'google': return self.jarvis.open_website('google.com')
                 else: return self.jarvis.open_app(target)
             else:
                 return self.jarvis.open_app(target)
        
        # App Closing
        elif 'close' in command_lower:
            target = command_lower.replace('close', '').strip()
            return self.jarvis.close_app(target)

        # System Control
        elif 'shutdown' in command_lower or 'restart' in command_lower or 'lock' in command_lower:
            return self.jarvis.system_control(command_lower)
            
        elif 'screenshot' in command_lower:
            return self.jarvis.take_screenshot()
            
        elif 'volume' in command_lower:
            import re
            # Extract number if present
            amount = None
            match = re.search(r'(\d+)', command_lower)
            if match:
                amount = int(match.group(1))

            if 'mute' in command_lower: 
                action = 'mute'
            elif 'set' in command_lower or 'to' in command_lower and amount is not None:
                # "set volume to 50" or "volume to 50"
                action = 'set'
            elif 'up' in command_lower or 'increase' in command_lower: 
                action = 'up'
            elif 'down' in command_lower or 'decrease' in command_lower: 
                action = 'down'
            else: 
                # If just "volume 50", assume set
                if amount is not None:
                    action = 'set'
                else:
                    action = 'unknown'
            
            return self.jarvis.volume_control(action, amount)
            
        # Web Generation (Login Page)
        elif 'login' in command_lower and 'page' in command_lower and ('create' in command_lower or 'make' in command_lower or 'generate' in command_lower or 'webpage' in command_lower):
            return self.jarvis.create_login_page()
            
        # Coding (Offline / Simple)
        elif ('write' in command_lower or 'type' in command_lower or 'create' in command_lower or 'generate' in command_lower) and 'code' in command_lower:
            # Check if we have the model. If not, try to handle simple requests or explain.
            if not self.model:
                if 'hello' in command_lower and 'world' in command_lower:
                     # Offline fallback for "hello world"
                    lang = 'python'
                    if 'html' in command_lower: lang = 'html'
                    elif 'javascript' in command_lower: lang = 'javascript'
                    
                    if lang == 'python': code = "print('Hello World')"
                    elif lang == 'html': code = "<h1>Hello World</h1>"
                    elif lang == 'javascript': code = "console.log('Hello World');"
                    else: code = "print('Hello World')"
                    
                    if 'type' in command_lower:
                        # User wants VISUAL TYPING
                        return self.jarvis.visual_code_demo(code, lang)
                    else:
                        return self.jarvis.save_and_run_code(code, lang)
                else:
                    return "I need a Gemini API Key to generate custom code. Please add it to config.py."
            else:
                # Let the LLM handle complex coding requests
                return None

        # Search & Research
        elif 'research' in command_lower:
             query = command_lower.replace('research', '').strip()
             return self.research_agent.conduct_research(query)
        elif 'wikipedia' in command_lower:
             query = command_lower.replace('wikipedia', '').replace('search', '').strip()
             return self.jarvis.search_wikipedia(query)
        elif 'google' in command_lower or 'search' in command_lower:
             query = command_lower.replace('search', '').replace('google', '').strip()
        elif 'google' in command_lower or 'search' in command_lower:
             query = command_lower.replace('search', '').replace('google', '').strip()
             return self.jarvis.google_search(query)
             
        # Image Generation (Mock)
        # Image Generation (Inline)
        elif 'generate' in command_lower and ('image' in command_lower or 'picture' in command_lower or 'drawing' in command_lower):
             import re
             # Remove common trigger words to get the clean prompt
             # Regex removes "generate", "create", "image", "picture", "drawing", "of", "an", "a" ONLY at the start or as whole words
             prompt = re.sub(r'\b(generate|create|make|image|picture|drawing|of|an|a)\b', '', command_lower).strip()
             # Clean up double spaces
             prompt = re.sub(r'\s+', ' ', prompt).strip()
             return self._generate_image(prompt)
             
        # Google Integrations
        elif 'email' in command_lower and ('send' in command_lower or 'draft' in command_lower or 'write' in command_lower):
             return self.google.draft_email(subject="Draft from SAMi")
        elif 'calendar' in command_lower and ('routine' not in command_lower):
             return self.google.create_calendar_event(title="New Event")
        elif 'map' in command_lower or 'direction' in command_lower:
             query = command_lower.replace('map', '').replace('show', '').replace('where is', '').strip()
             return self.google.search_maps(query)
        elif 'drive' in command_lower:
             return self.google.open_drive()
             
        # Routines
        elif 'routine' in command_lower or command_lower in ['good morning', 'good night', 'start work']:
             return self.routines.execute_routine(command_lower)
             
        return None

    def _think_and_act(self, command, language):
        """Uses Gemini to reason about the query and potentially use tools."""
        if not self.model:
            return "I need my cognitive core (Gemini API Key) to answer that."

        # Construct Prompt with Memory Context
        context_str = self.memory.get_full_context_string()
        history = self.memory.get_context("history")[-5:] 
        
        history_str = "Conversation History:\n"
        for turn in history:
            history_str += f"{turn['role'].upper()}: {turn['content']}\n"

        # Define Tools for the LLM (Simplified Function Calling Protocol via Prompting)
        # Note: True function calling with Gemini API is better, but this is a robust prompt-based fallback 
        # that works with standard text usage if function calling isn't strictly set up.
        # However, for "Autonomous Partner", we want it to OUTPUT actions.
        
        # OPTIMIZED PROMPT FOR SPEED
        system_prompt = f"""
        {config.SYSTEM_INSTRUCTION}
        
        {context_str}
        
        {history_str}
        
        TOOLS:
        - search_wikipedia(query)
        - google_search(query)
        - conduct_research(topic) # Use for complex topics requiring summary
        - play_youtube(song)
        - open_website(url)
        - open_app(name)
        - system_control(cmd)
        - take_screenshot(name)
        - volume_control(action)
        - create_login_page()
        - open_website(url)
        - open_app(name)
        - system_control(cmd)
        - take_screenshot(name)
        - volume_control(action)
        - create_login_page()
        - save_and_run_code(code, lang)
        - create_calendar_event(title, date)
        - draft_email(recipient, subject, body)
        - search_maps(query)
        - execute_routine(name)
        - control_mouse(action, x, y)
        - control_keyboard(action, text)
        - file_operations(action, path, content)
        - clipboard_control(action, text)
        - brightness_control(level)
        
        INSTRUCTIONS:
        - If action needed: Output ONLY JSON: [{{"tool": "name", "args": "val"}}]
        - If user asks to WRITE/SHOW code: Output Markdown code block.
        - If user asks to RUN/EXECUTE code: Use 'save_and_run_code'.
        - If chat: Respond normally in {language}.
        - BE CONCISE.
        """
        
        try:
            full_prompt = f"{system_prompt}\nUSER COMMAND: {command}"
            response = self._generate_with_retry(full_prompt)
            text_response = response.text.strip()
            
            # Check for JSON Tool Call
            if "```json" in text_response:
                try:
                    import json
                    json_str = text_response.split("```json")[1].split("```")[0].strip()
                    actions = json.loads(json_str)
                    
                    execution_results = []
                    for action in actions:
                        tool_name = action.get("tool")
                        args = action.get("args")
                        
                        # Execute via Jarvis or Research Agent
                        if tool_name == 'conduct_research':
                            result = self.research_agent.conduct_research(args)
                        elif isinstance(args, list):
                            result = self.jarvis.execute_task(tool_name, *args)
                        # Execute via Jarvis or Research Agent
                        if tool_name == 'conduct_research':
                            result = self.research_agent.conduct_research(args)
                        elif tool_name in ['create_calendar_event', 'draft_email', 'search_maps', 'open_drive']:
                            # Map to Google module
                            method = getattr(self.google, tool_name)
                            if isinstance(args, list): result = method(*args)
                            else: result = method(args)
                        elif tool_name == 'execute_routine':
                            result = self.routines.execute_routine(args)
                        elif isinstance(args, list):
                            result = self.jarvis.execute_task(tool_name, *args)
                        else:
                            result = self.jarvis.execute_task(tool_name, args)
                        execution_results.append(f"Tool '{tool_name}' returned: {result}")
                    
                    # Synthesize final response based on results
                    final_response = f"I have executed the requested actions: {', '.join(execution_results)}"
                    # Ideally, we could feed this back to LLM for a natural summary, but this is faster.
                    return final_response
                    
                except Exception as e:
                    print(f"Tool parse error: {e}")
                    return text_response # Fallback to raw text
            
            # Simple Memory Extraction (Self-Learning)
            if "my name is" in command.lower():
                name = command.lower().split("my name is")[-1].strip()
                self.memory.update_context("user_profile", "name", name)
            
            return text_response
        except Exception as e:
            return f"My cognitive engine encountered an error: {e}"

    def _quick_think(self, command, language):
        """
        Streamlined cognitive process for faster responses.
        Uses smaller context and simpler tool set.
        """
        # SMART SEARCH ROUTING (For Accuracy on Products/News)
        # Even in quick mode, if user asks for price/news, we need external data.
        search_keywords = ['price', 'cost', 'buy', 'latest', 'news', 'release date', 'launch', 'stock', 'weather']
        if any(k in command.lower() for k in search_keywords):
                print("Smart Search Triggered (Quick Mode)...")
                # Extract query and search
                query = command.replace('price', '').replace('cost', '').replace('search', '').strip()
                # Direct Search Response (Reading instead of opening tab)
                search_result = self.research.quick_search(query) 
                return f"Here is what I found:\n{search_result}"

        if not self.model:
             if config.AI_MODE == 'local':
                 return self._run_local_model(command)
             return "I need a cognitive engine (Cloud or Local) to think."


        try:
             # minimal context
            history = self.memory.get_context("history")[-2:] 
            history_str = ""
            for turn in history:
                history_str += f"{turn['role'].upper()}: {turn['content']}\n"
            
            # SMART SEARCH ROUTING (For Accuracy on Products/News)
            # Even in quick mode, if user asks for price/news, we need external data.
            search_keywords = ['price', 'cost', 'buy', 'latest', 'news', 'release date', 'launch', 'stock', 'weather']
            if any(k in command.lower() for k in search_keywords):
                 print("Smart Search Triggered (Quick Mode)...")
                 # Extract query and search
                 query = command.replace('price', '').replace('cost', '').replace('search', '').strip()
                 search_result = self.google.google_search(query) # Assume google search module returns string
                 return f"Here is what I found: {search_result}"

            prompt = f"""
{config.QUICK_SYSTEM_PROMPT}

HISTORY:
{history_str}

USER: {command}
"""
            # Fast generation with no retries (fail fast)
            response = self._generate_with_retry(prompt, retries=0)
            text_response = getattr(response, 'text', str(response)).strip()
            
            # Simple JSON check (copying logic from main think method but simplified)
            if "```json" in text_response:
                import json
                json_str = text_response.split("```json")[1].split("```")[0].strip()
                actions = json.loads(json_str)
                # Execute first action only for speed
                if actions:
                    action = actions[0]
                    tool_name = action.get("tool")
                    args = action.get("args")
                    
                    if tool_name in ['play_music', 'play_youtube']:
                         return self.jarvis.play_youtube(args) if 'youtube' in tool_name else self.music.play_music(args)
                    elif tool_name == 'open_app':
                         return self.jarvis.open_app(args)
                    elif tool_name == 'open_website':
                         return self.jarvis.open_website(args)
                         
                    return f"Executed {tool_name}."
            
            self.memory.add_history("model", text_response)
            return text_response

        except Exception as e:
            print(f"Quick Think Error: {e}")
            # Fallback to rule/local
            return self._run_local_model(command)

    def _run_local_model(self, command):
        """Executes the command using the Local Ollama model."""
        try:
            # Build Prompt based on Mode and Persona
            if config.QUICK_RESPONSE_MODE:
                 # Minimal Context for speed
                 prompt = f"{config.QUICK_SYSTEM_PROMPT}\nUser: {command}"
            else:
                 # Standard / Deep Mode
                 history_context = self.memory.get_context_window(limit=10) # Increased context for chat
                 
                 # Select Persona Prompt
                 if getattr(config, 'PERSONA', 'professional') == 'friendly':
                     system_prompt = config.FRIENDLY_SYSTEM_PROMPT
                 else:
                     system_prompt = config.SYSTEM_INSTRUCTION

                 prompt = f"{system_prompt}\n\nContext:\n{history_context}\nUser: {command}"
            
            payload = {
                "model": config.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            }
            
            print(f"Thinking on Local Brain ({config.OLLAMA_MODEL})...")
            # MAX TIMEOUT for slow systems (90s)
            timeout = 90
            response = requests.post(config.OLLAMA_URL, json=payload, timeout=timeout)
            
            if response.status_code == 200:
                ai_text = response.json()['response']
                self.memory.add_history("model", ai_text)
                return ai_text
            else:
                 return f"My local brain disconnected. (Status: {response.status_code})"
                 
        except requests.exceptions.ConnectionError:
                return "I cannot connect to Ollama. Please ensure the Ollama app is running on your PC."
        except Exception as e:
                print(f"Local AI Error: {e}")
                return "I encountered a local processing error."

    def _deep_think(self, command, language):
        """
        Advanced Reasoning Mode: Uses Chain of Thought (CoT).
        Forces the model to explain its reasoning step-by-step.
        """
        print("Running in DEEP THINK MODE...")
        
        if config.AI_MODE == 'local':
             try:
                history_context = self.memory.get_context_window(limit=5)
                
                # Chain of Thought Prompt
                cot_prompt = f"""System: You are SAMi. You are in 'Deep Reasoning Mode'.
Goal: Answer the user's question with high accuracy and depth.
Instructions:
1. First, check for any lingering spelling errors or ambiguities in: "{command}".
2. Think step-by-step about the problem. Break it down.
3. Critique your own initial thoughts to ensure accuracy.
4. Finally, provide the definitive answer.
Format:
[Thinking]
... your internal reasoning (including any typo correction) ...
[Answer]
... your final response to the user ...

Context: {history_context}
User: {command}"""

                payload = {
                    "model": config.OLLAMA_MODEL,
                    "prompt": cot_prompt,
                    "stream": False
                }
                
                # Longer timeout for deep thinking
                response = requests.post(config.OLLAMA_URL, json=payload, timeout=60)
                
                if response.status_code == 200:
                    raw_text = response.json()['response']
                    
                    # Store full thought process in memory for context
                    self.memory.add_history("model", raw_text)
                    
                    # Return full text (Thinking + Answer) so user sees the "Work"
                    # Or we could strip it. User asked for "more thinking power", usually they like to see the thinking.
                    return raw_text
                else:
                     return f"Deep Think failed. Status: {response.status_code}"
                     
             except Exception as e:
                 print(f"Deep Think Error: {e}")
                 return "I tried to think deeply but encountered an error. Falling back to standard mode."
                 
        return self._think_and_act(command, language) # Fallback for cloud/other methods

    def _generate_image(self, prompt):
        """Generates an image using Pollinations.ai (Free/No-Key)."""
        import urllib.parse
        
        # 1. Enhance Prompt if not in Quick Mode
        enhanced_prompt = prompt
        if not config.QUICK_RESPONSE_MODE and self.model:
            try:
                enhancement_prompt = f"Rewrite this image prompt to be highly detailed and artistic. Keep it under 50 words. Prompt: {prompt}"
                response = self._generate_with_retry(enhancement_prompt)
                enhanced_prompt = getattr(response, 'text', str(response)).strip()
            except Exception as e:
                print(f"Prompt Enhancement Failed: {e}")
                
        # 2. Construct URL
        encoded_prompt = urllib.parse.quote(enhanced_prompt)
        seed = random.randint(1, 10000)
        # Using Pollinations.ai (Free, Fast, No Auth)
        # Added seed to prevent caching issues
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed={seed}&nologo=true"
        
        print(f"Generating Image: {enhanced_prompt}")
        
        # 3. Return Structured Response (Dict)
        return {
            "text": f"Here is the generated image of {prompt}.",
            "image": image_url
        }

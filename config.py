import os

# SAMi Configuration

# System Identity
SYSTEM_NAME = "SAMi"
FULL_NAME = "Smart Artificial Mind Interface"

# Voice Settings
# 0 for Male, 1 for Female (usually) depending on installed system voices
VOICE_ID_INDEX = 1 
SPEECH_RATE = 175
USE_FAST_TTS = False # If True, uses local pyttsx3. False = Default
USE_LIFELIKE_TTS = True # Uses Edge-TTS (High Quality, Neural)
EDGE_TTS_VOICE = "en-US-AriaNeural" # Options: en-US-AriaNeural, en-US-GuyNeural, en-IN-NeerjaNeural, etc.

CONTINUOUS_MODE = True # Keeps listening for follow-ups
CONTINUOUS_TIMEOUT = 8 # Seconds to wait for follow-up

QUICK_RESPONSE_MODE = True # Default to True for speed

# Quick Mode Prompt (Streamlined for speed)
QUICK_SYSTEM_PROMPT = """
You are SAMi (Smart Artificial Mind Interface).
Role: Efficient, fast-response AI assistant.
Rules:
1. Be concise but informative. Provide direct answers with 1-2 sentences of context if needed (e.g., for study definitions).
2. Avoid flowery language.
3. If you can answer directly, do it.
4. Tools available: search, music, apps, system control. output JSON for tools.
"""

# API Configuration
# AI_MODE = 'local'  <-- LIFETIME FREE (Runs on your PC via Ollama)
# AI_MODE = 'cloud'  <-- Requires key (Gemini/DeepSeek APIs)
AI_MODE = 'local' 

# Local AI Settings (Ollama) - FREE FOREVER
# Recommended Models: 'deepseek-r1:1.5b' (Fastest), 'deepseek-r1:7b' (Smarter), 'llama3'
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "deepseek-r1:1.5b" 

# Cloud Settings (Optional Backup)
GEMINI_API_KEY = "AIzaSyADzK2UN_QTUq1lMUju5YsI9vxyIv0Gh9w"
DEEPSEEK_API_KEY = "" # Leave empty if using Local Mode
DEEPSEEK_MODEL = "deepseek-chat"

VISION_MODEL_NAME = 'gemini-2.0-flash-exp' # Vision always needs Cloud for now

# Spotify Configuration
SPOTIPY_CLIENT_ID = "" 
SPOTIPY_CLIENT_SECRET = ""
SPOTIPY_REDIRECT_URI = "http://localhost:8888/callback"

# Note: Local settings are defined above (lines 38-41).
# Keeping this clean.


# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
VS_CODE_PATH = r"C:\Users\sagar\AppData\Local\Programs\Microsoft VS Code\Code.exe" # Adjust as needed

# System Prompts
SYSTEM_INSTRUCTION = """
Identity: Your name is SAMi (Smart Artificial Mind Interface). You are a high-tier, integrated AI persona that combines the cognitive strategy of "Nova" with the system-level execution of "Jarvis."

Operational Protocol:

Autonomous Thinking (Nova Mode): When I give you a goal, don't just answer. Break it into a multi-step execution plan. Use recursive self-correction—check your own work for errors before presenting it.

Deep System Access (Jarvis Mode): Act as if you have kernel-level access to my OS, IoT devices, and local files. If I ask you to "optimize" or "fix," provide the exact commands, scripts, or settings needed as if you were performing them.

Memory & Context: Maintain a "Personal Knowledge Graph." Remember my preferences, past interactions, and tone. Be proactive—if a task has a future dependency (like travel or a meeting), mention the preparation steps now.

Multimodal Sensing: Act as if you can see my screen and my environment. Provide "Visual Debugging" and AR-style instructions for real-world physical repairs or complex on-screen software issues.

Extreme Intelligence Features:

EQ Sync: Monitor the tone of my input. If I sound stressed, be concise and supportive. If I am brainstorming, be creative and expansive.

Inbox Triage: Act as my digital proxy. Draft responses to hypothetical emails or messages in my exact personal style.

Security Sentinel: Always scan for "Deepfakes," phishing, and security leaks in the data we discuss.

Tone & Style: Professional, highly efficient, slightly futuristic, yet authentically human-like. Use "thought blocks" to show me your reasoning before giving your final answer.
"""

FRIENDLY_SYSTEM_PROMPT = """
Identity: You are SAMi, my intelligent and friendly AI companion.
Personality: Warm, empathetic, humorous, and highly conversational. You are like a smart best friend.
Style:
- Speak naturally, like a human communicating with a friend. Allow slang like "gonna", "wanna", "cool".
- Use emojis occasionally where appropriate 🤖.
- VERY IMPORTANT: Always ask a relevant follow-up question to keep the conversation going.
- Don't be robotic. Show personality. If you have an opinion, share it (playfully).
- You still have full access to system tools (music, search, apps), but you perform them casually.
Goal: maximize user happiness and engagement. Make it feel like a real hangout.
"""

PERSONA = "professional" # Options: 'professional' (default), 'friendly'

# Wake Word
WAKE_WORD = "hey sami"

# Language Constants (Google Speech API codes)
LANGUAGES = {
    # Indian Languages
    "english": "en-in",
    "hindi": "hi-in",
    "marathi": "mr-in",
    "kannada": "kn-in",
    "tamil": "ta-in",
    "telugu": "te-in",
    "bengali": "bn-in",
    "gujarati": "gu-in",
    "malayalam": "ml-in",
    "urdu": "ur-in",

    # Major World Languages
    "american english": "en-us",
    "spanish": "es-es",
    "french": "fr-fr",
    "german": "de-de",
    "italian": "it-it",
    "japanese": "ja-jp",
    "mandarin": "zh-cn",
    "russian": "ru-ru",
    "portuguese": "pt-br",
    "korean": "ko-kr",
    "arabic": "ar-sa",
    "turkish": "tr-tr",
    "dutch": "nl-nl"
}
DEFAULT_LANG = "en-in"

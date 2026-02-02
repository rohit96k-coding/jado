
from modules.research_agent import ResearchAgent
import config

# Mock config for testing
config.AI_MODE = 'local'
config.OLLAMA_MODEL = 'deepseek-r1:1.5b'

print("Initializing Research Agent...")
agent = ResearchAgent()

print("Running Quick Search for 'iphone 16 pro price'...")
try:
    result = agent.quick_search("iphone 16 pro price")
    print("\n--- RESULT ---")
    print(result[:500] + "...") # Print first 500 chars
    
    if "couldn't find" in result:
        print("\nFAILURE: Search returned empty.")
    else:
        print("\nSUCCESS: Search returned data.")
        
except Exception as e:
    print(f"\nERROR: {e}")

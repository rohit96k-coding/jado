
import google.generativeai as genai
import config
import os

print(f"Testing Gemini 1.5 Flash...")
try:
    genai.configure(api_key=config.GEMINI_API_KEY)
    
    # Use 1.5 Flash
    model = genai.GenerativeModel('gemini-2.0-flash-lite')
    response = model.generate_content("Hello")
    print(f"\nResponse: {response.text}")
    print("SUCCESS")

except Exception as e:
    print(f"\nFAILURE: {e}")

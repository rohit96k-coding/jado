
import google.generativeai as genai
import config
import os

print(f"Testing Gemini API Connection...")
print(f"API Key: {config.GEMINI_API_KEY[:5]}...{config.GEMINI_API_KEY[-5:]}")

try:
    genai.configure(api_key=config.GEMINI_API_KEY)
    
    # List models to verify access
    print("Listing available models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")

    print("\nAttempting generation with gemini-2.0-flash...")
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content("Hello, this is a test.")
    print(f"\nResponse: {response.text}")
    print("SUCCESS: Connected to Gemini Cloud.")

except Exception as e:
    print(f"\nFAILURE: {e}")

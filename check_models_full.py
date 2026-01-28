
import os
import google.generativeai as genai
import config

def list_models():
    try:
        genai.configure(api_key=config.GEMINI_API_KEY)
        with open("models_list.txt", "w") as f:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    f.write(m.name + "\n")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_models()

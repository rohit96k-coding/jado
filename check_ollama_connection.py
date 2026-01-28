import requests
import json

url = "http://localhost:11434/api/generate"
payload = {
    "model": "llama3",
    "prompt": "Hello",
    "stream": False
}

print(f"Testing connection to {url} with model 'llama3'...")

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Response Success!")
        print(response.json().get('response', 'No response field'))
    else:
        print(f"Response Error: {response.text}")
except Exception as e:
    print(f"Connection Failed: {e}")

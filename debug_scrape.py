
import requests
from bs4 import BeautifulSoup
import urllib.parse

def search_ddg_html(query):
    url = "https://html.duckduckgo.com/html/"
    data = {'q': query}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://html.duckduckgo.com/"
    }
    
    print(f"Scraping {url} for '{query}'...")
    try:
        resp = requests.post(url, data=data, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'html.parser')
            results = []
            
            for link in soup.find_all('a', class_='result__a'):
                 href = link.get('href')
                 if href:
                     # DDG sometimes wraps links? HTML version usually direct.
                     results.append(href)
            
            print(f"Found {len(results)} results.")
            if results: print(results[0])
            return results
        else:
             print("Failed status.")
             return []
             
    except Exception as e:
        print(f"Error: {e}")
        return []

search_ddg_html("iphone 16 price")

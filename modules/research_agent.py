import requests
import urllib.parse
from bs4 import BeautifulSoup
import config

class ResearchAgent:
    def __init__(self, nova_engine=None):
        self.nova = nova_engine # Reference to main engine for LLM usage

    def _scrape_ddg(self, query, max_results=5):
        """Robust fallback using direct HTML scraping."""
        url = "https://html.duckduckgo.com/html/"
        data = {'q': query}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://html.duckduckgo.com/"
        }
        
        results = []
        try:
            resp = requests.post(url, data=data, headers=headers, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'html.parser')
                # Iterate over result links
                for link in soup.find_all('a', class_='result__a'):
                    href = link.get('href')
                    if href and "duckduckgo.com" not in href: # Filter internal redirects if possible, or decode them
                         # DDG HTML often gives direct links or redirects.
                         # If it's a redirect (duckduckgo.com/l/?uddg=...), we extract the real URL
                         if "uddg=" in href:
                             try:
                                 parsed = urllib.parse.urlparse(href)
                                 qs = urllib.parse.parse_qs(parsed.query)
                                 real_url = qs.get('uddg', [None])[0]
                                 if real_url: results.append(real_url)
                             except:
                                 pass
                         else:
                             results.append(href)
                             
                    if len(results) >= max_results: break
        except Exception as e:
            print(f"Scrape Error: {e}")
            
        return results

    def conduct_research(self, query, quick_mode=False):
        """
        Performs a research task:
        1. Searches (DuckDuckGo HTML Scrape)
        2. Scrapes Content
        3. Summarizes
        """
        print(f"Researching: {query} (Quick: {quick_mode})")
        
        # 1. Search
        num_results = 2 if quick_mode else 5
        search_results = self._scrape_ddg(query, max_results=num_results)

        if not search_results:
            return "I couldn't find any relevant results on the web."

        # 2. Scrape Content
        aggregated_content = ""
        for url in search_results:
            try:
                print(f"Reading: {url}...")
                response = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract text from paragraphs
                paragraphs = soup.find_all('p')
                # For quick mode, take less text for speed
                limit = 5 if quick_mode else 15
                page_text = " ".join([p.get_text() for p in paragraphs[:limit]]) 
                
                aggregated_content += f"\nSOURCE: {url}\nCONTENT: {page_text[:1500]}\n" 
                
            except Exception as e:
                print(f"Failed to read {url}: {e}")
                continue

        if not aggregated_content:
            return "I found search results but couldn't read the content of the pages."

        # 3. Summarize with LLM (using Nova's model)
        prompt = f"""
        You are a Research Assistant. Summarize the following information to answer the user's query: "{query}".
        
        Format as a clear, concise report. directly answer the question.
        
        {aggregated_content}
        """
        
        if self.nova:
            if self.nova.model: # Cloud Mode
                try:
                    response = self.nova.model.generate_content(prompt)
                    return response.text
                except Exception as e:
                     return f"Research summary failed (Cloud): {e}"
            elif config.AI_MODE == 'local': # Local Mode
                 try:
                     payload = {
                        "model": config.OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False
                     }
                     # 60s timeout for analysis
                     response = requests.post(config.OLLAMA_URL, json=payload, timeout=60)
                     if response.status_code == 200:
                         return response.json()['response']
                     else:
                         return f"Research summary failed (Local): {response.status_code}"
                 except Exception as e:
                     return f"Research summary failed (Local Loop): {e}"
        
        # Fallback if no LLM
        return f"Here are the top results I found:\n" + "\n".join(search_results)

    def quick_search(self, query):
        """Wrapper for fast 1-result research."""
        return self.conduct_research(query, quick_mode=True)

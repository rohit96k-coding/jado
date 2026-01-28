import requests
from googlesearch import search
from bs4 import BeautifulSoup
import config

class ResearchAgent:
    def __init__(self, nova_engine=None):
        self.nova = nova_engine # Reference to main engine for LLM usage

    def conduct_research(self, query, quick_mode=False):
        """
        Performs a deep research task:
        1. Generates search queries
        2. Searches Google
        3. Scrapes top results
        4. Summarizes with LLM
        """
        print(f"Researching: {query} (Quick: {quick_mode})")
        
        # 1. Search Google
        search_results = []
        num_results = 1 if quick_mode else 3
        try:
            # Get top URLs
            for url in search(query, num_results=num_results, lang="en"):
                search_results.append(url)
        except Exception as e:
            return f"Research failed during search: {e}"

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
                     # Reuse Nova's local generation
                     payload = {
                        "model": config.OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False
                     }
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

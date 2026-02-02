
try:
    from googlesearch import search
    print("Testing googlesearch...")
    results = list(search("iphone 16 pro price", num_results=3, lang="en"))
    print(f"Google Results: {results}")
except Exception as e:
    print(f"Google Search Failed: {e}")

print("-" * 20)

try:
    from duckduckgo_search import DDGS
    print("Testing duckduckgo_search...")
    results = list(DDGS().text("iphone 16 pro price", max_results=3))
    print(f"DDG Results: {results}")
except ImportError:
    print("duckduckgo_search not installed.")
except Exception as e:
    print(f"DDG Search Failed: {e}")


from duckduckgo_search import DDGS

print("Testing DDGS direct...")

queries = ["hello world", "iphone 16 price"]

for q in queries:
    print(f"\nQuery: {q}")
    
    # Method 1: Default
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(q, max_results=3))
            print(f"Default Results: {len(results)}")
            if results: print(results[0]['href'])
    except Exception as e:
        print(f"Default Error: {e}")

    # Method 2: HTML Backend (often more reliable)
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(q, max_results=3, backend="html"))
            print(f"HTML Backend Results: {len(results)}")
            if results: print(results[0]['href'])
    except Exception as e:
        print(f"HTML Backend Error: {e}")

    # Method 3: Lite Backend
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(q, max_results=3, backend="lite"))
            print(f"Lite Backend Results: {len(results)}")
            if results: print(results[0]['href'])
    except Exception as e:
        print(f"Lite Backend Error: {e}")

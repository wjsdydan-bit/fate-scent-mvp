from duckduckgo_search import DDGS

try:
    with DDGS() as ddgs:
        results = [r for r in ddgs.images("Jo Malone Blackberry & Bay perfume bottle", max_results=1)]
        print(results)
except Exception as e:
    print(f"Error: {e}")

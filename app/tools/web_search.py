"""Web search fallback using DuckDuckGo (ddgs package)."""
import time
from ddgs import DDGS


def search(query: str, max_results: int = 5, retries: int = 2) -> list[dict]:
    """
    Search the web for a query. Returns list of results with title, snippet, url.

    Retries if the first attempt returns nothing (DuckDuckGo rate limits).
    """
    for attempt in range(retries + 1):
        try:
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "snippet": r.get("body", ""),
                        "url": r.get("href", ""),
                        "source": "web_search",
                    })
            if results:
                return results
            if attempt < retries:
                print(f"  [web_search] attempt {attempt + 1} returned 0 — retrying")
                time.sleep(2)
        except Exception as e:
            print(f"  [web_search] attempt {attempt + 1} failed: {e}")
            if attempt < retries:
                time.sleep(2)

    return []


if __name__ == "__main__":
    test_query = "PM Ujjwala Yojana eligibility"
    print(f"Searching: {test_query}\n")
    results = search(test_query, max_results=3)
    if not results:
        print("No results returned.")
    for i, r in enumerate(results, 1):
        print(f"[{i}] {r['title']}")
        print(f"    {r['snippet'][:150]}...")
        print(f"    {r['url']}\n")
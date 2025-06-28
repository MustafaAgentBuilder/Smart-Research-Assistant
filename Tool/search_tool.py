import os
from typing import List, Dict 
from tavily import TavilyClient
from agents import function_tool
@function_tool(
    name_override="search_web",
    description_override="Use Tavily API to fetch top search results (title, url, snippet).",
    failure_error_function=lambda ctx, e: f"Error during Tavily search: {e}"
)
def search_web(
    query: str, 
    max_results: int = 3
) -> List[Dict]:
    """
    Perform a web search using the Tavily API.

    Parameters:
      - query: The search terms (e.g. "quantum computing breakthroughs").
      - max_results: How many top results to return (default 3).

    Returns:
      A list of dicts, each with:
        title   (str): Headline of the result.
        url     (str): Link to the source.
        summary (str): Short snippet or summary.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY not set in environment")

    client = TavilyClient(api_key=api_key)
    try:
        resp = client.search(query, max_results=max_results)
    except Exception as e:
        raise RuntimeError(f"Tavily API error: {e}")

    results = [
        {
            "title": item.get("title"),
            "url": item.get("url"),
            "summary": item.get("content") or item.get("raw_content", "")[:200]
        }
        for item in resp.get("results", [])
    ]
    if not results:
        raise ValueError(f"No results for query: '{query}'")
    return results

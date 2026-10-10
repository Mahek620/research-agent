
from fastmcp import FastMCP
import httpx
from bs4 import BeautifulSoup
from ddgs import DDGS

mcp = FastMCP("research-tools")


@mcp.tool
def web_search(query: str, max_results: int = 5) -> list[dict]:
    """Search the web. Returns a list of results with title, url and snippet."""
    results = DDGS().text(query, max_results=max_results)
    return [
        {"title": r["title"], "url": r["href"], "snippet": r["body"]}
        for r in results
    ]


@mcp.tool
def fetch_page(url: str) -> str:
    """Fetch a web page and return its readable text (first 6000 characters)."""
    r = httpx.get(
        url,
        timeout=15,
        follow_redirects=True,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    return " ".join(soup.get_text(" ").split())[:6000]


if __name__ == "__main__":
    mcp.run()
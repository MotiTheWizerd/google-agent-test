
from __future__ import annotations
from typing import Any, Dict, List, Union, Optional
import os
from dotenv import load_dotenv
from .client import FirecrawlClient
from .types import ScrapeOptions, CrawlOptions, SearchOptions, ExtractOptions

# Load environment variables from .env file
load_dotenv()

_client = None
def _get_client() -> FirecrawlClient:
    global _client
    if _client is None:
        # Get API key from environment variables
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise RuntimeError("FIRECRAWL_API_KEY not found in environment variables")
        _client = FirecrawlClient(api_key=api_key)  # picks FIRECRAWL_API_KEY env
    return _client

def tool_scrape(url: str) -> Dict[str, Any]:
    """
    Scrape a single URL and return markdown, links, and HTML content.
    
    Args:
        url (str): The URL to scrape
        
    Returns:
        Dict[str, Any]: Scraped data including markdown, links, and HTML
    """
    opts = ScrapeOptions(formats=["markdown","links","html"])
    return _get_client().scrape(url, opts)

def tool_search(query: str, limit: int = 5, scrape_markdown: bool = False) -> Dict[str, Any]:
    """
    Search the web and optionally scrape the top results.
    
    Args:
        query (str): Search query
        limit (int): Number of results to return (default: 5)
        scrape_markdown (bool): Whether to scrape markdown content for each result (default: False)
        
    Returns:
        Dict[str, Any]: Search results with optional scraped content
    """
    scrape_options = ScrapeOptions(formats=["markdown","links"]) if scrape_markdown else None
    so = SearchOptions(query=query, limit=limit, scrape_options=scrape_options)
    return _get_client().search(so)

def tool_crawl_site(url: str, max_pages: int = 200) -> Dict[str, Any]:
    """
    Crawl an entire website up to a maximum number of pages.
    
    Args:
        url (str): The website URL to crawl
        max_pages (int): Maximum number of pages to crawl (default: 200)
        
    Returns:
        Dict[str, Any]: Crawled data from all pages
    """
    co = CrawlOptions(
        url=url,
        sitemap="include",
        max_discovery_depth=2,
        limit=max_pages,
        scrape_options=ScrapeOptions(formats=["markdown","links"], only_main_content=True),
    )
    return _get_client().crawl(co, poll=True)

def tool_extract(inputs: List[str], prompt: str | None = None, schema: dict | None = None) -> Dict[str, Any]:
    """
    Extract structured data using a prompt or schema over a list of URLs or a wildcard domain.
    
    Args:
        inputs (List[str]): List of URLs or wildcard patterns to extract from
        prompt (str, optional): Prompt to guide extraction
        schema (dict, optional): Schema to structure the extracted data
        
    Returns:
        Dict[str, Any]: Extracted structured data
    """
    # Validate that either prompt or schema is provided
    if not prompt and not schema:
        raise ValueError("Either 'prompt' or 'schema' must be provided")
        
    eo = ExtractOptions(inputs=inputs, prompt=prompt, schema=schema)
    return _get_client().extract(eo, poll=True)
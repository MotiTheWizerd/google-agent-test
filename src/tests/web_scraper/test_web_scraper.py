"""
Test file for the web scraper module.
This file contains pytest tests for the web scraper tools.
"""

import pytest
import os
from src.modules.tools.web_scraper import (
    tool_scrape,
    tool_search,
    tool_crawl_site,
    tool_extract
)

# Skip tests if FIRECRAWL_API_KEY is not set
pytestmark = pytest.mark.skipif(
    not os.getenv("FIRECRAWL_API_KEY"), 
    reason="FIRECRAWL_API_KEY not set in environment variables"
)

def test_scrape():
    """Test the scrape tool with a simple URL"""
    result = tool_scrape("https://docs.firecrawl.dev/introduction")
    assert result is not None
    assert "metadata" in result
    assert "title" in result["metadata"]

def test_search():
    """Test the search tool"""
    result = tool_search("firecrawl search api", limit=3, scrape_markdown=True)
    assert result is not None
    assert "data" in result
    assert len(result["data"]) > 0

def test_extract_with_prompt():
    """Test the extract tool with a prompt"""
    # This is a simple test - in practice, you'd want to test with a real schema
    with pytest.raises(ValueError):
        # Should raise ValueError when neither prompt nor schema is provided
        tool_extract(["https://docs.firecrawl.dev/*"])